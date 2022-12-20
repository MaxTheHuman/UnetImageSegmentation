# Create by Packetsss
# Personal use is allowed
# Commercial use is prohibited

import numpy as np
import cv2
from scipy import ndimage
import math
from copy import deepcopy


class Images:
    def __init__(self, img):
        self.img = cv2.imread(img, 1)
        if self.img.shape[0] / self.img.shape[1] < 0.76:
            self.img_width = 1100
            self.img_height = int(self.img_width * self.img.shape[0] / self.img.shape[1])
        else:
            self.img_height = 700
            self.img_width = int(self.img_height * self.img.shape[1] / self.img.shape[0])

        self.img = cv2.resize(self.img, (self.img_width, self.img_height))
        self.img_copy = deepcopy(self.img)
        self.grand_img_copy = deepcopy(self.img)

        self.img_name = img.split('\\')[-1].split(".")[0]
        self.img_format = img.split('\\')[-1].split(".")[1]

        self.left, self.right, self.top, self.bottom = None, None, None, None

        # self.bypass_censorship()

    def save_img(self, file):
        cv2.imwrite(file, self.img)


def main():
    path = "ppl.jpg"
    img = Images(path)
    img_name = path.split('\\')[-1].split(".")[0]

    cv2.imshow(img_name, img.img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
