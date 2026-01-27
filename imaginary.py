import math
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

from clicker import Clicker


class ImageShower:
    _image = None
    _ax = None
    _fig = None

    @property
    def ax(self):
        if self._ax is None:
            self._fig, self._ax = plt.subplots()
        return self._ax

    @property
    def fig(self):
        if self._fig is None:
            self._fig, self._ax = plt.subplots()
        return self._fig

    @property
    def image(self):
        if self._image is None:
            self._image = self.ax.imshow(np.random.rand(100, 100), cmap='gray', vmin=0, vmax=255, aspect='auto')
            plt.show(block=False)
        return self._image

    def display(self, image):
        self.image.set_data(image)
        self.fig.canvas.flush_events()
        self.fig.canvas.draw_idle()
        plt.pause(0.01)  # Short delay to visualize update


if __name__ == '__main__':
    shower = ImageShower()
    # for i in range(10):
    #     data = np.random.rand(100, 100)
    #     data[data < i / 10] = 0
    #     shower.display(data)
    #     time.sleep(.1)

    clicker = Clicker()
    clicker.hwnd = 0x2605B2
    trash_piece_img = cv2.imread('images/trash_piece.bmp')
    while True:
        start = time.time()
        clicker.screen_lookup(window=(-225, 15, -40, 200))
        image = clicker.screen[..., :3]
        bgr = [167, 184, 193]
        # length = math.dist([0, 0, 0], bgr)
        # bgr = [channel / length for channel in bgr]
        mask = np.zeros(image.shape[:-1], dtype=np.uint8)
        mask[np.where((np.abs(image - bgr) < 10).all(axis=-1))] = 255
        cmask = np.zeros(image.shape[:-1], dtype=np.uint8)
        cv2.circle(cmask, (int(cmask.shape[0] / 2), int(cmask.shape[1] / 2)), 70, 255, -1)
        mask[cmask != 255] = 0
        # mask = cv2.dilate(mask, None, iterations=1)
        mask = cv2.erode(mask, np.ones((2, 2), np.uint8), iterations=1)
        mask = cv2.dilate(mask, None, iterations=1)
        # shower.display(mask)
        contours = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
        # filter by area
        s1 = 1
        s2 = 12
        # print([cv2.contourArea(cntr) for cntr in contours])
        for cntr in contours:
            area = cv2.contourArea(cntr)
            if s1 <= area <= s2:
                # isolated contours in green
                cv2.drawContours(clicker.screen, [cntr], 0, (0, 255, 0), 1)
            else:
                # cluster contours in red
                cv2.drawContours(clicker.screen, [cntr], 0, (0, 0, 255), 1)
        # mask = cv2.adaptiveThreshold(mask, 255, 0, 1, 3, 1)
        # max_v = np.dot(image, bgr)
        # max_v = max_v.astype(np.uint8)
        # max_v[max_v < .5] = 0
        # max_v[max_v >= .5] = 1
        # shower.display(mask)
        # gray = cv2.cvtColor(clicker.screen, cv2.COLOR_BGRA2GRAY)
        # blurred = cv2.medianBlur(gray, 3)  # Reduce noise
        # shower.display(gray)
        # circles = cv2.HoughCircles(max_v, cv2.HOUGH_GRADIENT, dp=1, minDist=1,
        #                            param1=50, param2=10, minRadius=1, maxRadius=3)
        circles = None
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                cv2.circle(clicker.screen, (i[0], i[1]), i[2], (0, 255, 0), 1)  # Draw circle
                # cv2.circle(clicker.screen, (i[0], i[1]), 2, (0, 255, 0), 2)  # Draw center

        # replace_color = (195, 185, 165)
        # for pixel_idx in clicker.find_pixels(color=replace_color):
        #     clicker.fill(window=(*pixel_idx, *pixel_idx), color=(0, 255, 0))
        # for coord in clicker.find_image(trash_piece_img, threshold=.8):
        # for coord in clicker.find_pixels(color=(0, 255, 0), threshold=.7):
        #     center = (coord[0] + int(trash_piece_img.shape[1] / 2) - clicker.offset[0], coord[1] + int(trash_piece_img.shape[0] / 2) - clicker.offset[1])
            # clicker.fill((*coord_to_fill, *coord_to_fill), color=(0, 255, 0))
            # cv2.circle(clicker.screen, center, 3, (0, 255, 0), 1)  # Draw circle
        shower.display(clicker.screen[:,:,::-1])
        print(time.time() - start)
        time.sleep(0.1)
