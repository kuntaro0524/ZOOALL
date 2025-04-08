#-*- coding:utf-8 -*-
import v4l2
import cv2
import numpy as np
from fcntl import ioctl


def main():

    # チャンネル選択(Composite3)
    fd=open('/dev/video0', 'rw')
    ioctl(fd, v4l2.VIDIOC_S_INPUT, v4l2.c_int(2))

    # 動画の読み込み
    cap = cv2.VideoCapture(0)

    # 動画終了まで繰り返し
    while(cap.isOpened()):

        # フレームを取得
        ret, frame = cap.read()

        # フレームを表示
        cv2.imshow("Flame", frame)
#        cv2.imwrite("test.png", frame)

        # qキーが押されたら途中終了
	key=cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s'):
	    cv2.imwrite("back.png",frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

