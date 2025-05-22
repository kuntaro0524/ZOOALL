import cv2
import sys
import numpy as np

# スライド1の画像を読み込み（グレースケール変換）
image_slide1 = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)

# 二値化処理（背景と結晶を分離）
_, binary_image = cv2.threshold(image_slide1, 200, 255, cv2.THRESH_BINARY_INV)

# 輪郭検出
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Number of contours: {len(contours)}")

# contours を一つずつ解析する
# Xの数値でソートする
# Xの数値が同一で、Yの数値が異なる場合、X,Y座標をそれぞれ記録する
for contour in contours:
    #contourのdimensionsを取得
    print("Contour Dimensions:",contour.shape)
    for i in range(0,contour.shape[0]):
        for j in range(0,contour.shape[1]):
            print("Contour[",i,"][",j,"]:",contour[i][j])

# 結果を描画
output_image = cv2.cvtColor(image_slide1, cv2.COLOR_GRAY2BGR)
#cv2.drawContours(output_image, contours, -1, (0, 255, 255), 2)
# 赤い点を描画 from list_cross_points
for point in list_cross_points:
    print("LISTED:",point)
    cv2.circle(output_image, point, 5, (0, 0, 255), -1)

# 結果画像を表示
cv2.imshow("Contours on Slide 1", output_image)
cv2.waitKey(0)

import numpy as np
# 輪郭ごとにマスクを作成して、ピクセル値の統計を取る
mask = np.zeros_like(binary_image)
cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

# 重なり部分を判定（例えば濃度が高い部分）
overlap_threshold = 100  # このしきい値より暗い部分を重なりとして識別
overlap_mask = (image_slide1 < overlap_threshold).astype(np.uint8) * 255

# 重なり部分を除去
single_crystal_mask = cv2.bitwise_and(mask, cv2.bitwise_not(overlap_mask))

# 単結晶の輪郭を再検出
single_contours, _ = cv2.findContours(single_crystal_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 単結晶部分を識別した画像を作成
output_single_image = cv2.cvtColor(image_slide1, cv2.COLOR_GRAY2BGR)
cv2.drawContours(output_single_image, single_contours, -1, (255, 0, 0), 2)

# 結果画像の保存
single_contour_image_path = "./tmp.png"
cv2.imwrite(single_contour_image_path, output_single_image)

# 結果画像を表示
cv2.imshow("Single Crystals on Slide 1", output_single_image)
cv2.waitKey(0)