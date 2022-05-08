#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Vanessa Jóriová
# Date        : 8.5.2022
# Version     : 1.0

import cv2 as cv
import numpy as np
from FingerprintImage import FingerprintImage


class Generator:
    """

    Class capable of drawing synthetic damage from damage_canvas into fingerprint area
    """

    def __init__(self, fingerprint: FingerprintImage):
        """

        :param fingerprint: Instance of FingerprintImage class with loaded image
        """
        fingerprint.create_mask()
        fingerprint.get_fingerprint_size()
        self.fingerprint = fingerprint
        self.background = fingerprint.img
        self.background_mask = fingerprint.fingerprint_mask
        self.background_width = fingerprint.img_width
        self.background_height = fingerprint.img_height
        self.original_img = np.copy(fingerprint.img)
        self.fingerprint_width = fingerprint.fingerprint_width
        self.fingerprint_height = fingerprint.fingerprint_height
        self.damage_canvas = self.create_damage_canvas()

        self.damage_pixels = None
        self.background_pixels = None
        self.fingerprint_pixels = None

    def create_damage_canvas(self):
        """

        :return: Black canvas with size of the image background
        """
        return np.zeros(self.background.shape[:2], np.uint8)

    def crop_by_mask(self):
        """

        @brief: Crops any synthetic damage drawn outside of fingerprint area
        """
        cropped_by_mask = cv.bitwise_and(self.background, self.background, mask=self.background_mask)
        cropped_by_inverse_mask = cv.bitwise_and(self.original_img, self.original_img, mask=255 - self.background_mask)
        self.background = cv.add(cropped_by_mask, cropped_by_inverse_mask)

    def get_damage_pixels(self):
        """

        @brief: Detects and returns any white (damage) pixels drawn on black canvas
        :return: [x,y] coordinates of white points on canvas
        """
        non_zero = np.nonzero(self.damage_canvas)
        coordinates = list(zip(non_zero[0], non_zero[1]))
        coordinates = np.array(coordinates)
        points = coordinates.reshape(-1, 2)
        self.damage_pixels = points
        return points

    def draw_on_background(self):
        """

        @brief:  Copies all white pixels from damage_canvas into background image, thus redrawing
        the damage
        """
        pixels = self.get_damage_pixels()
        for p in pixels:
            self.background[p[0], p[1]] = self.damage_canvas[p[0], p[1]]

    def find_fingerprint_pixels(self):
        """

        @brief: Gets [x,y] coordinates of all pixels belonging to the fingerprint area based on color of the same pixel
        in the mask (pixels inside fingerprint are white, outside black)
        """
        white_pixels = np.nonzero(self.background_mask)

        coordinates = list(zip(white_pixels[0], white_pixels[1]))
        coordinates = np.array(coordinates)
        points = coordinates.reshape(-1, 2)

        self.fingerprint_pixels = points

    def get_bigger_side_size(self):
        """

        @brief: compares height and width of image and returns size of bigger side
        :return: side size as int
        """
        if self.background_width > self.background_height:
            return self.background_width
        else:
            return self.background_height

    def get_bigger_fingerprint_side_size(self):
        """

        @brief: compares height and width of fingerprint area (approximated by bounding rect) and returns size of bigger
                side
        :return: side size as int
        """
        if self.fingerprint_width > self.fingerprint_height:
            return self.fingerprint_width
        else:
            return self.fingerprint_height

    def find_background_pixels(self):
        """

        @brief: Gets [x,y] coordinates of all pixels belonging to the background area based on color of the same pixel
        in the mask (pixels inside fingerprint are white, outside black)
        """
        black_pixels = np.where(self.background_mask == 0)
        coordinates = list(zip(black_pixels[0], black_pixels[1]))
        coordinates = np.array(coordinates)
        points = coordinates.reshape(-1, 2)
        self.background_pixels = points

    def split_fingerprint_and_background_pixels(self):
        """

        @brief: Finds coordinates of pixels belonging to the fingerprint area and coordinates of pixels outside of
        fingerprint area
        """
        self.find_background_pixels()
        self.find_fingerprint_pixels()

    def show_background(self):
        """

        @brief: Shows background if background exists
        """

        if self.background is not None:
            cv.imshow("Background", self.background)
            cv.waitKey(0)
        else:
            print("Background does not exist")
