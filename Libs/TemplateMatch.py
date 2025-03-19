import cv2
import numpy as np

class TemplateMatch:
	def __init__(self, template_ppm, target_ppm):
		self.template_ppm = template_ppm
		self.target_ppm = target_ppm

	def setNewTarget(self, target_ppm):
		self.target_ppm = target_ppm

	def getMatch(self):
		self.tmp_img = cv2.imread(self.template_ppm, cv2.IMREAD_GRAYSCALE)
		self.obj_img = cv2.imread(self.target_ppm, cv2.IMREAD_GRAYSCALE)
		dst_size = (self.obj_img.shape[1] - self.tmp_img.shape[1] + 1, self.obj_img.shape[0] - self.tmp_img.shape[0] + 1)

		dst_img = np.zeros(dst_size, np.float32)
		cv2.matchTemplate(self.obj_img, self.tmp_img, dst_img, cv2.TM_CCOEFF_NORMED)

		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(dst_img)
		self.p2 = max_loc

		cv2.namedWindow("image", cv2.WINDOW_AUTOSIZE)
		cv2.imshow("image", self.obj_img)
		cv2.waitKey(0)

if __name__ == "__main__":
	host = '172.24.242.41'
	tmplowppm = "/path/to/template.ppm"  # テンプレート画像のパスを指定してください

	tm = TemplateMatch(tmplowppm, "/isilon/users/target/target/image005.ppm")
	tm.getMatch()

	corner_point = (tm.p2[0] + tm.tmp_img.shape[1], tm.p2[1] + tm.tmp_img.shape[0])
	cv2.rectangle(tm.obj_img, tm.p2, corner_point, (255, 0, 0), 2)
	cv2.circle(tm.obj_img, tm.p2, 5, (255, 0, 0), 2)
	cv2.imshow("image", tm.obj_img)
	cv2.waitKey(0)
