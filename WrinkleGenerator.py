#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Vanessa Jóriová
# Date        : 8.5.2022
# Version     : 1.0

from LineGenerator import LineGenerator, LineOrientation, LineLength, LineThickness
import random as random
import cv2 as cv
import numpy as np


class WrinkleGenerator:
    """

    Class generating wrinkle damage into synthetic fingerprint image
    """

    def __init__(self, fingerprint):
        """

        :param fingerprint: instance of FingerprintImage
        """
        self.fingerprint = fingerprint
        self.line_generator = LineGenerator(fingerprint)
        self.generated_image = None
        self.damage_pixels = np.zeros(self.line_generator.background.shape[:2], np.uint8)

    def get_damage_pixels(self):
        for point in self.line_generator.damage_pixels:
            self.damage_pixels[point[0], point[1]] = 255

    def is_crease_overlapping_with_other(self):
        total_pixel_amount = len(self.line_generator.damage_pixels)
        overlapping_pixels = 0
        for pixel in self.line_generator.damage_pixels:
            if self.damage_pixels[pixel[0], pixel[1]] == 255:
                overlapping_pixels += 1
        if overlapping_pixels > total_pixel_amount // 4:
            return True
        else:
            return False

    def generate_crease(self, line_length, line_orientation, line_thickness):
        max_attempts = 100
        for i in range(0, max_attempts):
            image_save = self.line_generator.background.copy()
            self.line_generator.generate_line(length_type=line_length, orientation=line_orientation,
                                              thickness=line_thickness)
            if self.is_crease_overlapping_with_other() is False:
                break
            self.line_generator.background = image_save
        self.get_damage_pixels()

    def wrinkles_level_1(self):
        """

        @brief:  Generates creases of level 1 (damage consisting of 4-6 individual lines).
        :return: None
        """
        max_amount = random.randrange(4, 7)

        # amount of primary wrinkles (thin or medium, long or medium)
        amount = random.randrange(2, 4)
        generate = random.randrange(0, 10)

        thickness = LineThickness.THIN

        for x in range(0, amount):

            generate = random.randrange(0, 20)
            if generate < 16:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL

            line_length = random.choice((LineLength.LONG, LineLength.MEDIUM))
            self.generate_crease(line_length, orientation, thickness)

        # short thin wrinkles added to get final amount of wrinkles in image
        small_wrinkles_amount = max_amount - amount
        if small_wrinkles_amount < 0:
            small_wrinkles_amount = 0
        for x in range(0, small_wrinkles_amount):
            generate = random.randrange(0, 20)
            if generate < 15:
                orientation = LineOrientation.HORIZONTAL
            else:
                orientation = LineOrientation.VERTICAL
            self.generate_crease(LineLength.SHORT, orientation, LineThickness.THIN)

        self.generated_image = self.line_generator.background.copy()

    def wrinkles_level_2(self):
        """

        @brief:  Generates creases of level 2 (damage consisting of 6-12 individual lines).
        :return: None
        """

        max_amount = random.randrange(6, 13)

        # amount of primary wrinkles (thin or medium and long or medium)
        amount = random.randrange(2, 7)
        thickness = LineThickness.THIN
        for x in range(0, amount):
            generate = random.randrange(0, 20)
            if generate < 16:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL
            line_length = random.choice((LineLength.LONG, LineLength.MEDIUM))
            self.generate_crease(line_length, orientation, thickness)

        # short thin wrinkles added to get final amount of wrinkles in image
        small_wrinkles_amount = max_amount - amount
        if small_wrinkles_amount < 0:
            small_wrinkles_amount = 0
        for x in range(0, small_wrinkles_amount):
            generate = random.randrange(0, 20)
            if generate < 16:
                orientation = LineOrientation.HORIZONTAL
            else:
                orientation = LineOrientation.VERTICAL
            self.line_generator.generate_line(length_type=LineLength.SHORT, orientation=orientation,
                                              thickness=LineThickness.THIN)

        self.generated_image = self.line_generator.background.copy()

    def wrinkles_level_3(self):
        """

        @brief:  Generates creases of level 3 (damage consisting of 12-20 individual lines).
        :return: None
        """

        total_amount = random.randrange(12, 21)

        # amount of thick wrinkles
        generate_thick = random.randrange(0, 2)
        if generate_thick:
            self.generate_crease(LineLength.LONG, LineOrientation.RANDOM, LineThickness.THICK)

        # amount of medium wrinkles
        medium_amount = random.randrange(1, 3)
        for x in range(0, medium_amount):
            generate = random.randrange(0, 20)
            if generate < 16:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL
            line_len = random.choice((LineLength.LONG, LineLength.MEDIUM))
            self.generate_crease(line_len, orientation, LineThickness.MEDIUM)

        # amount of long thin wrinkles
        long_amount = random.randrange(0, 9)
        for x in range(0, long_amount):

            generate = random.randrange(0, 20)
            if generate < 15:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL

            self.generate_crease(LineLength.LONG, orientation, LineThickness.THIN)

        # thin short wrinkles are added to reach total amount of wrinkles
        thin_amount = total_amount - medium_amount - long_amount
        for x in range(0, thin_amount):
            line_len = random.choice((LineLength.SHORT, LineLength.MEDIUM))

            generate = random.randrange(0, 11)
            if generate < 6:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 9:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL

            self.generate_crease(line_len, orientation, LineThickness.THIN)
        self.generated_image = self.line_generator.background.copy()

    def show_generated_image(self):
        """

        @brief Shows generated image
        :return: None
        """
        cv.imshow("Wrinkles", self.generated_image)
        cv.waitKey(0)
