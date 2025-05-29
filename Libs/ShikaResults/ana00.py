import cv2
import sys

# スライド1の画像を読み込み（グレースケール変換）
image_slide1 = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)

# 二値化処理（背景と結晶を分離）
_, binary_image = cv2.threshold(image_slide1, 200, 255, cv2.THRESH_BINARY_INV)

# 輪郭検出
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 結果を描画
output_image = cv2.cvtColor(image_slide1, cv2.COLOR_GRAY2BGR)
cv2.drawContours(output_image, contours, -1, (0, 0, 255), 2)

# 抽出した輪郭画像を保存
contour_image_path = "/mnt/data/contours_slide1.png"
cv2.imwrite(contour_image_path, output_image)

# 結果画像を表示
cv2.imshow("Contours on Slide 1", output_image)
cv2.waitKey(0)