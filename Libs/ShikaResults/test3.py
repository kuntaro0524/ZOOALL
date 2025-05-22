import cv2
import sys
import numpy as np
import pandas as pd

# 画像の読み込み（グレースケール変換）
image_cv = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
pixel_resolution=int(sys.argv[2])

# 画像のリサイズ（指定ピクセルごとに平均化）
new_width = image_cv.shape[1] // pixel_resolution
new_height = image_cv.shape[0] // pixel_resolution
image_resized_cv = cv2.resize(image_cv, (new_width, new_height), interpolation=cv2.INTER_AREA)

# X, Y, Score のデータフレーム作成
x_coords, y_coords = np.meshgrid(np.arange(new_width), np.arange(new_height))
df_cv = pd.DataFrame({
    "X": x_coords.flatten(),
    "Y": y_coords.flatten(),
    "Score": image_resized_cv.flatten()
})

# csv
df_cv.to_csv(sys.argv[3],index=False)

# PNGに書き出す
cv2.imwrite(sys.argv[4], image_resized_cv)

# データフレームを表示
#tools.display_dataframe_to_user(name="Grayscale Pixel Data (OpenCV)", dataframe=df_cv)