#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Vanessa Jóriová
# Date        : 8.5.2022
# Version     : 1.0

from LineGenerator import LineGenerator, LineOrientation, LineLength, LineThickness
from ImageDistortion import *
from FingerprintImage import FingerprintImage
import math
import cv2 as cv
import numpy as np
import random as rnd


class ScarGenerator(LineGenerator):
    """
    Class capable of generating synthetic scar into synthetic fingerprint image
    """

    def __init__(self, fingerprint):
        super().__init__(fingerprint)
        self.main_print = True
        self.max_width = None
        self.new_edges = None
        self.line_irregularities = True
        self.irregular_edge = True
        self.black_outline = False
        self.distortion = False
        self.artifacts = False
        self.frequency_center = True
        self.filter_mask = None

    def get_max_width(self):
        """

        @brief: Calculates maximum width of line depending on parameters and fingerprint size
        :return: max thickness as integer
        """
        if self.fingerprint.fingerprint_width > self.fingerprint.fingerprint_height:
            bigger_side = self.fingerprint.fingerprint_width
        else:
            bigger_side = self.fingerprint.fingerprint_height
        if self.line_irregularities is True:
            if self.thickness == LineThickness.THICK:
                max_thickness = bigger_side // 25
                if max_thickness < 1:
                    max_thickness = 1
                variance = rnd.randrange(0, +max_thickness // 2)
                max_thickness += variance
            elif self.thickness == LineThickness.MEDIUM:
                max_thickness = bigger_side // 35
                if max_thickness < 1:
                    max_thickness = 1
                variance = rnd.randrange(0, +max_thickness // 2)
                max_thickness += variance
            elif self.thickness == LineThickness.THIN:
                max_thickness = bigger_side // 60
                if max_thickness < 1:
                    max_thickness = 1
                variance = rnd.randrange(0, +max_thickness // 2)
                max_thickness += variance

        else:
            if self.thickness == LineThickness.THICK:
                max_thickness = bigger_side // 6
                if max_thickness < 1:
                    max_thickness = 1
                variance = rnd.randrange(0, +max_thickness // 2)
                max_thickness += variance
            elif self.thickness == LineThickness.MEDIUM:
                max_thickness = bigger_side // 10
                if max_thickness < 1:
                    max_thickness = 1
                variance = rnd.randrange(0, +max_thickness // 2)
                max_thickness += variance
            elif self.thickness == LineThickness.THIN:
                max_thickness = bigger_side // 30
                if max_thickness < 1:
                    max_thickness = 1
                variance = rnd.randrange(0, +max_thickness // 2)
                max_thickness += variance

        return max_thickness

    def thicken_line(self):
        """

        @brief: Draws lines of given thickness between two points of line, creating width variance. Left and right
                (if they exist) sectors around point with maximum width are drawn with maximum width, width of sectors
                further away decreases by 1, visually thickening the line in both direction
        :return: None
        """

        self.max_width = self.get_max_width()

        if len(self.control_points) - 1 <= 5:
            max_thickness_point = (len(self.control_points) - 1)//2
        max_thickness_point = rnd.randrange(2, len(self.control_points) - 2)
        segments_to_left = max_thickness_point
        segments_to_right = (len(self.control_points) - 1) - max_thickness_point
        for i in range(0, max_thickness_point):
            point_1 = self.control_points[i]
            point_2 = self.control_points[i + 1]
            width = self.max_width - segments_to_left + 1 + i
            if width < 2:
                if self.thickness == LineThickness.THICK:
                    width = 5
                else:
                    width = 2
            cv.line(self.damage_canvas, point_1, point_2, (255, 0, 255), width)

            if self.line_irregularities:
                self.line_irregularity(point_1, point_2, width)

        for i in reversed(range(max_thickness_point + 1, len(self.control_points))):
            point_1 = self.control_points[i]
            point_2 = self.control_points[i - 1]
            width = self.max_width + (max_thickness_point - i + 1)
            if width < 2:
                if self.thickness == LineThickness.THICK:
                    width = 5
                else:
                    width = 2
            cv.line(self.damage_canvas, point_1, point_2, (255, 0, 255), width)

            if self.line_irregularities:
                self.line_irregularity(point_1, point_2, width)

    def line_irregularity(self, point_1, point_2, width):
        """

        @brief: Creates irregular line edges between two points by drawing white circles among the line
        :param point_1: Point as (x,y) coordinates
        :param point_2: Point as (x,y) coordinates
        :param width: Width of line between two points
        :return: none
        """
        distance = int(math.sqrt((point_2[0] - point_1[0]) ** 2 + (point_2[1] - point_1[1]) ** 2))
        circle_radius = width - 3
        if circle_radius <= 0:
            circle_radius = 1
        radius_variance = circle_radius//3
        if radius_variance != 0:
            circle_radius += rnd.randrange(0, radius_variance+1)
        points_nmbr = int(distance / (circle_radius / 2))
        if points_nmbr == 0:
            points_nmbr = rnd.choice((0, 1))

        points_on_line = np.linspace(point_1, point_2, points_nmbr)
        points_on_line = points_on_line.astype(int)
        for p in points_on_line:
            x = rnd.randrange(0, 10)
            for x in range(0, x):

                if width > 5:
                    variance = int(circle_radius / 3)
                else:
                    variance = 2
                if variance != 0:
                    x_variance = rnd.randrange(-variance, variance+1)
                    y_variance = rnd.randrange(-variance, variance+1)
                else:
                    x_variance = rnd.choice((-1, 2))
                    y_variance = rnd.choice((-1, 2))
                new_x = p[0] + x_variance
                new_y = p[1] + y_variance
                cv.circle(self.damage_canvas, (new_x, new_y), circle_radius, 255, -1)

    def generate_line(self, length_type=LineLength.RANDOM, orientation=LineOrientation.RANDOM,
                      thickness=LineThickness.RANDOM):
        """

        @brief: Generates line specified by parameters
        :param length_type: Instance of LineLength enum
        :param orientation: Instance of LineOrientation enum
        :param thickness: Instance of LineThickness enum
        :return: None
        """
        if self.background is None:
            print("Synthetic fingerprint image is not available")
            return

        self.damage_canvas = np.zeros(self.fingerprint.img.shape[:2], np.uint8)

        if length_type == LineLength.RANDOM:
            self.length_type = rnd.choice((LineLength.SHORT, LineLength.MEDIUM, LineLength.LONG))
        else:
            self.length_type = length_type

        if orientation == LineOrientation.RANDOM:
            self.orientation = rnd.choice((
                LineOrientation.HORIZONTAL, LineOrientation.VERTICAL, LineOrientation.DIAGONAL))
        else:
            self.orientation = orientation

        if thickness == LineThickness.RANDOM:
            self.thickness = rnd.choice((LineThickness.THIN, LineThickness.MEDIUM, LineThickness.THICK))
        else:
            self.thickness = thickness

        while True:

            while True:
                point1, point2 = self.generate_start_end_point()
                if point1 != -1:
                    break
            self.get_control_points(point1, point2)

            self.move_control_points()

            if self.more_than_one_point_outside() is False:
                break
        self.add_width_points()
        if (self.thickness is LineThickness.THICK) and (self.line_irregularities is False):
            self.add_width_points()
            self.add_width_points()

        if self.line_irregularities:
            generate = rnd.randrange(0, 3)
            for x in range(0, generate):
                self.add_width_points()
        self.thicken_line()

        if self.irregular_edge:
            self.irregular_edges()
        if self.distortion:
            self.distort_edges()
            if self.main_print:
                filtered = self.background.copy()
                filtered = cv.medianBlur(filtered, 5)
                ret, thresh = cv.threshold(filtered, 100, 255, cv.THRESH_BINARY)
                self.background = thresh
                if (self.distortion and self.artifacts) or (self.distortion and self.black_outline):
                    self.distortion_mask()

        if self.black_outline:
            self.draw_black_outline()
        self.draw_on_background()
        if self.artifacts:
            self.generate_artifacts(patch_center=self.frequency_center)
        self.crop_by_mask()
        if self.distortion is False:
            ret, thresh = cv.threshold(self.background, 200, 255, cv.THRESH_BINARY)
            self.background = thresh

    def distortion_mask(self):
        """

        @brief: Creates new fingerprint mask of distorted image
        :return: None
        """

        fingerprint_mask = np.zeros(self.background.shape[:2], np.uint8)
        blur = cv.blur(self.background, (7, 7))
        ret, thresh = cv.threshold(blur, 240, 255, cv.THRESH_BINARY_INV)

        contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for c in range(0, len(contours)):
            cv.drawContours(fingerprint_mask, contours, c, 255, -1)
        self.fingerprint.fingerprint_mask = fingerprint_mask

    def new_mask(self):
        """

        @brief: applies new fingerprint mask based on distorted
        :return: None
        """
        fingerprint = FingerprintImage()
        fingerprint.set_img(self.background)
        fingerprint.create_mask()
        self.fingerprint = fingerprint

    def distort_edges(self):
        """

        @brief: applies soak distortion along the scar on specific points
        :return: None
        """
        distortion_mask = np.zeros(self.background.shape[:2], np.uint8)

        img_dist = ImageOperation(self.original_img)
        if self.length_type == LineLength.SHORT:
            radius = self.max_width * 3
        else:
            radius = self.max_width*4
        scale = 1.1
        point_without_distortion = None
        for i in range(0, len(self.control_points)-1):
            point_1 = self.control_points[i]
            point_2 = self.control_points[i + 1]
            if self.point_outside(point_1[1], point_1[0]) is False:
                dist = self.distance(point_1, point_2)
                amount_of_points = dist//(radius//3)
                if dist > radius//3:
                    cv.circle(self.background, point_1, radius, 255, 2)
                    cv.circle(distortion_mask, point_1, radius, 255, -1)
                    soak_of_circle_area(img_dist, point_1[1], point_1[0], radius, scale)
                else:
                    if point_without_distortion is not None:
                        if self.distance(point_without_distortion, point_1) > radius//3:
                            cv.circle(distortion_mask, point_1, radius, 255, -1)
                            soak_of_circle_area(img_dist, point_1[1], point_1[0], radius, scale)
                            point_without_distortion = None
                    else:
                        point_without_distortion = point_1

                    # generate = rnd.randrange(0, 6)
                    # if generate < 1:
                    #     cv.circle(self.background, point_1, radius, 255, 2)
                    #     cv.circle(distortion_mask, point_1, radius, 255, -1)
                    #     soak_of_circle_area(img_dist, point_1[1], point_1[0], radius, scale)

                if amount_of_points > 2:
                    distortion_points = np.linspace(point_1, point_2, amount_of_points).astype(int)
                    # delete first and last element
                    distortion_points = np.delete(distortion_points, 0, axis=0)
                    distortion_points = np.delete(distortion_points, -1, axis=0)
                    for point in distortion_points:
                        cv.circle(self.background, point_1, radius, 255, 2)
                        cv.circle(distortion_mask, point, radius, 255, -1)
                        soak_of_circle_area(img_dist, point[1], point[0], radius, scale)

        #cv.imshow("B", self.background)
        self.filter_mask = distortion_mask

        self.background = np.copy(img_dist.arrImage)
        cv.waitKey()

    def more_than_one_point_outside(self):
        """

        @brief: this function detects if there are more than one control point generated outside fingerprint area
        :return: True if yes, false if no
        """
        outside_points = 0
        for point in self.control_points:
            if self.background_mask[point[1], point[0]] == 0:
                outside_points += 1
        if outside_points > 1:
            return True
        return False

    def generate_artifacts(self, patch_center=False):
        """

        @brief: Generates black irregular shapes in area of scar
        :param patch_center: True - artifacts will have greater frequency in randomly selected area
        :return: None
        """
        pixels = self.get_damage_pixels()
        frequency = rnd.randrange(10, 1000)
        frequency = 100
        for p in pixels:
            black_point = rnd.randrange(0, frequency)
            if black_point < 1:
                self.background[p[0], p[1]] = 0
            black_oval = rnd.randrange(0, frequency)
            if black_oval < 1:
                self.black_patch(p)
        if patch_center:
            self.intensify_black_patches_in_area(frequency)

    def black_patch(self, point):
        """

        @brief: draws irregular shape consisting of multiple points shifted in different directions
        :param point: coordinates of point in (x,y) format
        :return: None
        """
        amount = rnd.randrange(3, 10)
        x_coord = point[0]
        y_coord = point[1]
        for patch in range(0, amount):
            variance_x = rnd.randrange(-1, 2)
            variance_y = rnd.randrange(-1, 2)
            x_coord = x_coord + variance_x
            y_coord = y_coord + variance_y
            cv.circle(self.damage_canvas, (y_coord, x_coord), 1, 0, -1)

    def intensify_black_patches_in_area(self, frequency):
        """

        @brief: Randomly chooses area of scar and generates greater amount of black artifacts in this area.
        :param frequency: int number measuring amount of black artefacts in scar - higher frequency means higher number.
        :return: None
        """

        frequency_multiplier = rnd.randrange(5, 11)
        frequency = frequency//frequency_multiplier
        index = rnd.randrange(0, len(self.damage_pixels)-1)
        center = self.damage_pixels[index]
        radius = self.length//4
        radius_variance = radius//2
        if radius_variance < 1:
            radius_variance = 1
        radius += rnd.randrange(0, radius_variance)

        x_start = center[1]-radius//2
        if x_start < 0:
            x_start = 0

        x_end = center[1]+radius//2
        if x_end >= self.fingerprint.img_width:
            x_end = self.fingerprint.img_width - 1

        y_start = center[0]-radius//2
        if y_start < 0:
            y_start = 0

        y_end = center[0]+radius//2
        if y_end >= self.fingerprint.img_height:
            y_end = self.fingerprint.img_height - 1

        rand_arr = np.random.randint(frequency, size=(y_end - y_start, x_end - x_start))
        indexes = np.where(rand_arr == 0)
        indexes_y = indexes[0] + y_start
        indexes_x = indexes[1] + x_start

        for index in range(len(indexes_y)):
            self.black_patch((indexes_y[index], indexes_x[index]))

        for point in self.damage_pixels:
            if self.damage_canvas[point[0], point[1]] == 0:
                self.background[point[0], point[1]] = 0

    def irregular_edges(self):
        """

        @brief: Simulates shape irregularities of scars by drawing black circles alongside scar shape on black canvas,
        thus erasing parts of the damage.
        :return: None
        """
        edge_points = self.get_edge_coordinates()
        for p in edge_points:
            if self.length_type != LineLength.SHORT:
                generate = rnd.randrange(0, 10)
                if generate < 2:
                    radius = self.max_width // 3
                    if self.thickness == LineThickness.THICK:
                        radius = self.max_width // 4
                    cv.circle(self.damage_canvas, (p[1], p[0]), radius, 0, -1)
            else:
                generate = rnd.randrange(0, 30)
                if generate < 1:
                    cv.circle(self.damage_canvas, (p[1], p[0]), self.max_width // 5, 0, -1)
            generate = rnd.randrange(0, 40)
            if generate < 1:
                cv.circle(self.damage_canvas, (p[1], p[0]), 2, 0, -1)

    def draw_black_outline(self):
        """

        @brief: On every pixel of detected edge of scar generates a variable amount of black points. Every black point
                is then shifted in x and y axis by random amount and drawn.
        :return: None
        """
        self.new_edges = self.get_edge_coordinates()

        canvas = np.ones(self.fingerprint.img.shape[:2], np.uint8)
        white_canvas = canvas * 255

        for point in self.new_edges:
            generate = rnd.randrange(0, 10)

            if generate < 8:
                cv.circle(self.background, (point[1], point[0]), 1, 0, -1)
                cv.circle(white_canvas, (point[1], point[0]), 1, 0, -1)
                amount = rnd.randrange(3, 10)
                x_coord = point[0]
                y_coord = point[1]
                for patch in range(0, amount):
                    variance = self.max_width//6
                    variance_x = rnd.randrange(-variance, variance+1)
                    variance_y = rnd.randrange(-variance, variance+1)
                    x_coord = x_coord + variance_x
                    y_coord = y_coord + variance_y
                    cv.circle(self.background, (y_coord, x_coord), 1, 0, -1)
                    cv.circle(white_canvas, (y_coord, x_coord), 1, 0, -1)




