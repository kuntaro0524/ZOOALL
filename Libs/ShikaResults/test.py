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

# 単結晶部分をクラスタ0として選定（通常は低スコアが単結晶）
non_overlap_data = data[data['cluster'] == 0]

# yごとにクラスタを分けて最小x（左端）と最大x（右端）を取得
non_overlap_bounds = non_overlap_data.groupby(['y', 'cluster']).agg(
    left_edge=('x', 'min'),
    right_edge=('x', 'max')
).reset_index()

# 結果を表示
print(non_overlap_bounds)

# クラスタと選択された座標を描画
plt.figure(figsize=(10, 6))
for cluster_id in data['cluster'].unique():
    cluster_data = data[data['cluster'] == cluster_id]
    plt.scatter(cluster_data['x'], cluster_data['y'], label=f'Cluster {cluster_id}', s=25)

for _, row in non_overlap_bounds.iterrows():
    plt.hlines(row['y'], row['left_edge'], row['right_edge'], colors='red', linewidth=1)

plt.title('Clusters and Selected Coordinates')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.show()

# 必要ならCSVに出力
output_path = 'non_overlap_edges.csv'
non_overlap_bounds.to_csv(output_path, index=False)
print(f'重ならない部分の左端・右端の座標を {output_path} に保存しました。')