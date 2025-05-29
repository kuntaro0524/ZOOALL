import pandas as pd
import sys
from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt

# コマンドライン引数からファイルパスを取得
if len(sys.argv) != 2:
    print('Usage: python script.py <input_csv_file>')
    sys.exit(1)

file_path = sys.argv[1]
data = pd.read_csv(file_path)

# スコア分布を分析
scores = data['score'].values.reshape(-1, 1)

# DBSCANクラスタリングでスコアを自動識別
clustering = DBSCAN(eps=5, min_samples=5).fit(scores)
data['cluster'] = clustering.labels_

# 各クラスタに属しているデータ点を表示
plt.figure(figsize=(10, 6))
for cluster_id in data['cluster'].unique():
    cluster_data = data[data['cluster'] == cluster_id]
    plt.scatter(cluster_data['x'], cluster_data['y'], label=f'Cluster {cluster_id}', s=25)

# 各クラスタの平均スコアを計算する
cluster_means = data.groupby('cluster')['score'].mean().reset_index()
print(f"Cluster means:\n{cluster_means}")

# クラスタの平均値から
# 最も低いスコア→結晶ではない
# 最も高いスコア→結晶が重なっている
# 中庸なスコア→単結晶部分である
# 単結晶部分について以降の検討を行う
non_crystal_volume = data[data['cluster'] == cluster_means['score'].idxmin()]
overlap_volume = data[data['cluster'] == cluster_means['score'].idxmax()]
# それ以外の部分を単結晶部分とする
non_overlap_data = data[data['cluster'] == cluster_means['score'].idxmin()]

# yごとにクラスタを分けて最小x（左端）と最大x（右端）を取得
non_overlap_bounds = non_overlap_data.groupby(['y', 'cluster']).agg(
    left_edge=('x', 'min'),
    right_edge=('x', 'max'),
    height=('y', 'count')
).reset_index()

# クラスタ内のくびれ検出（X方向の幅とY方向の高さの両方を考慮）
threshold_ratio = 0.5  # くびれのしきい値（幅が前後平均の50%以下）
clusters_to_split = []
for cluster_id in non_overlap_bounds['cluster'].unique():
    cluster_data = non_overlap_bounds[non_overlap_bounds['cluster'] == cluster_id]
    widths = cluster_data['right_edge'] - cluster_data['left_edge']
    heights = cluster_data['height']
    for i in range(1, len(widths)-1):
        prev_width = widths.iloc[i-1]
        curr_width = widths.iloc[i]
        next_width = widths.iloc[i+1]
        avg_width = (prev_width + next_width) / 2

        prev_height = heights.iloc[i-1]
        curr_height = heights.iloc[i]
        next_height = heights.iloc[i+1]
        avg_height = (prev_height + next_height) / 2

        # X方向のくびれとY方向の高さ変動を同時に考慮
        if curr_width < avg_width * threshold_ratio and curr_height < avg_height * threshold_ratio:
            clusters_to_split.append((cluster_id, cluster_data['y'].iloc[i]))

# クラスタ再割り当て
for cluster_id, y_split in clusters_to_split:
    mask = (non_overlap_bounds['cluster'] == cluster_id) & (non_overlap_bounds['y'] >= y_split)
    new_cluster_id = non_overlap_bounds['cluster'].max() + 1
    non_overlap_bounds.loc[mask, 'cluster'] = new_cluster_id

# クラスタと選択された座標を描画
plt.figure(figsize=(10, 6))
for cluster_id in non_overlap_bounds['cluster'].unique():
    cluster_data = non_overlap_bounds[non_overlap_bounds['cluster'] == cluster_id]
    plt.scatter(cluster_data['y'], cluster_data['right_edge'] - cluster_data['left_edge'], label=f'Cluster {cluster_id}', s=50)
    for _, row in cluster_data.iterrows():
        plt.hlines(row['y'], row['left_edge'], row['right_edge'], colors='red', linewidth=0.5)

plt.title('Clusters and Selected Coordinates with Neck Detection')
plt.xlabel('Y')
plt.ylabel('Width (X range)')
plt.legend()
plt.show()

# 必要ならCSVに出力
output_path = 'non_overlap_edges.csv'
non_overlap_bounds.to_csv(output_path, index=False)
print(f'重ならない部分の左端・右端の座標を {output_path} に保存しました。')