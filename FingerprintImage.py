import cv2 as cv
import numpy as np
import os


class FingerprintImage:
    """
      Class for loading and masking synthetic fingerprint images.
    """

    def __init__(self, greyscale=True):
        """
        :param greyscale: image will be loaded as grayscale if true, else RGB image will be loaded
        """
        self.load_as_grayscale = greyscale
        self.img = None
        self.img_height = None
        self.img_width = None
        self.fingerprint_mask = None
        self.fingerprint_height = None
        self.fingerprint_width = None

    def load_file_from_path(self, path):
        """
        @brief Loads image from given path
        :param path: path to file
        """

        if self.load_as_grayscale:
            self.img = cv.imread(path, cv.IMREAD_GRAYSCALE)
        else:
            self.img = cv.imread(path)

        if self.img is None:
            print("Image could not be loaded.")
            os._exit(-1)
        else:
            self.img_width = int(self.img.shape[1])
            self.img_height = int(self.img.shape[0])

    def set_img(self, image):
        """
        @brief:
        :param image: Loaded image in matrix form
        """
        self.img = image
        self.img_width = int(self.img.shape[1])
        self.img_height = int(self.img.shape[0])

    def create_mask(self):
        """
        @brief Creates fingerprint mask used for detecting the area of the fingerprint

        Black image of the same size as the original image is created. Fingerprint image is blurred and threshold is
        applied. Contours are detected from threshold - each contour is then wrapped in convex hull to smooth the edges
        and resulting convex hulls are filled with white color  - result should be smooth mask in shape of fingerprint.
        Contours are then detected again and again filled with white color - this should prevent any black spots in
        final mask.
        """

        if self.img is None:
            print("An image must be loaded before creating mask")
            return

        self.fingerprint_mask = np.zeros(self.img.shape[:2], np.uint8)

        blur = cv.blur(self.img, (7, 7))
        ret, thresh = cv.threshold(blur, 240, 255, cv.THRESH_BINARY_INV)

        contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # Find the convex hull object for each contour
        hull_list = []
        for i in range(len(contours)):
            hull = cv.convexHull(contours[i])
            hull_list.append(hull)

        # Fill convex hulls with white
        color = (255, 255, 255)
        cv.drawContours(self.fingerprint_mask, hull_list, -1, color, -1)

        # Fill contours again to ensure there is no black space in mask
        contours, hierarchy = cv.findContours(self.fingerprint_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for c in range(0, len(contours)):
            cv.drawContours(self.fingerprint_mask, contours, c, 255, -1)

    def get_fingerprint_size(self):
        """
        @brief: fingerprint area is wrapped in bounding rectangle and fingerprint width and height are aproximated
        by this rectangle
        """
        contours, hierarchy = cv.findContours(self.fingerprint_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # Find the index of the largest contour
        # Inspired by https://stackoverflow.com/a/17507192

        areas = [cv.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        x, y, width, height = cv.boundingRect(cnt)

        self.fingerprint_height = height
        self.fingerprint_width = width

    def show_image(self):
        """

        @brief: Shows image if image exists
        """
        if self.img:
            cv.imshow('Mask', self.img)
            cv.waitKey(0)
        else:
            print("Fingerprint image does not exists")

    def show_mask(self):
        """

        @brief Shows mask if mask exists
        """
        if self.fingerprint_mask:
            cv.imshow("Mask", self.fingerprint_mask)
            cv.waitKey(0)
        else:
            print("Fingerprint mask does not exist")
