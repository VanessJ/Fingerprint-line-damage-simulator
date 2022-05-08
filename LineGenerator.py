#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Vanessa Jóriová
# Date        : 8.5.2022
# Version     : 1.0

from Generator import Generator

import math
import cv2 as cv
import numpy as np
import random as rnd
import enum

BLACK = 0
WHITE = 255


class LineLength(enum.Enum):
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    RANDOM = 4


class LineOrientation(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    DIAGONAL = 3
    RANDOM = 4


class LineThickness(enum.Enum):
    THIN = 1
    MEDIUM = 2
    THICK = 3
    RANDOM = 4


class LineGenerator(Generator):
    """

    Class implementation of irregular line with variable width, that can be used as crease
    """

    def __init__(self, fingerprint):
        super().__init__(fingerprint)
        self.control_points = None
        self.orientation = None
        self.length_type = None
        self.thickness = None
        self.control_points = None
        self.length = None
        self.damage_canvas = None
        self.max_width = None


    @staticmethod
    def distance(point_1, point_2):
        """

        @brief: Returns distance between two points
        :param point_1: (y,x) coordinate of first point
        :param point_2: (y,x) coordinate of second point
        :return: distance between two points as integer
        """
        return int(math.sqrt((point_2[0] - point_1[0]) ** 2 + (point_2[1] - point_1[1]) ** 2))

    def set_line_type(self, length, orientation, thickness):
        """

        @brief: Sets line length, orientation, thickness depending on the parameters, in case of RANDOM randomly
                selects type
        :param length: LineLength enum
        :param orientation: LineOrientation enum
        :param thickness: LineThickness enum
        :return: None
        """
        if length == LineLength.RANDOM:
            self.length_type = rnd.choice((LineLength.SHORT, LineLength.MEDIUM, LineLength.LONG))
        else:
            self.length_type = length

        if orientation == LineOrientation.RANDOM:
            self.orientation = rnd.choice((
                LineOrientation.HORIZONTAL, LineOrientation.VERTICAL, LineOrientation.DIAGONAL))
        else:
            self.orientation = orientation

        if thickness == LineThickness.RANDOM:
            self.thickness = rnd.choice((LineThickness.THIN, LineThickness.MEDIUM, LineThickness.THICK))
        else:
            self.thickness = thickness

    def generate_line(self, length_type=LineLength.RANDOM, orientation=LineOrientation.RANDOM,
                      thickness=LineThickness.RANDOM):
        """

        @brief: Generates line specified by parameters
        :param length_type: LineLength enum value
        :param orientation: LineOrientation enum value
        :param thickness:   LineThickness enum value
        :return: None
        """

        if self.background is None:
            print("Synthetic fingerprint image is not available")
            return

        self.set_line_type(length_type, orientation, thickness)
        self.damage_canvas = self.create_damage_canvas()

        while True:
            # Iterate until line of given parameters that is mostly inside fingerprint is generated
            while True:
                point1, point2 = self.generate_start_end_point()
                if point1 != -1:
                    break
            self.get_control_points(point1, point2)
            self.move_control_points()
            self.add_width_points()

            if self.thickness is LineThickness.THICK:
                # adding more thickness points to make line thinning more obvious
                self.add_width_points()
                self.add_width_points()
            if self.half_points_outside() is False:
                break

        self.thicken_line()
        self.irregular_edges()
        self.draw_on_background()
        self.crop_by_mask()

    def get_edge_coordinates(self):
        """

        @brief: This function detects edges of line damage drawn on canvas
        :return: list of edge points as (y,x) coordinates
        """
        edges = cv.Canny(self.damage_canvas, 100, 200)
        indices = np.where(edges != [0])
        coordinates = list(zip(indices[0], indices[1]))
        coordinates = np.array(coordinates)
        return coordinates

    def irregular_edges(self):
        """

        @brief: This function generates black circles along the edges of line on black_canvas, thus deleting
                parts of the damage and making edges more irregular
        :return: None
        """
        edge_points = self.get_edge_coordinates()
        for p in edge_points:
            generate = rnd.randrange(0, 10)
            if generate < 4:
                cv.circle(self.damage_canvas, (p[1], p[0]), self.max_width // 7, 0, -1)
            generate = rnd.choice((0, 1))
            if generate:
                cv.circle(self.damage_canvas, (p[1], p[0]), 1, 0, -1)

    def get_max_width(self):
        """

        @brief   Calculates thickness in most thick point in line depending on line parameters and fingerprint size
        :return: thickness in most thick point of line (as integer)
        """
        bigger_side = self.get_bigger_fingerprint_side_size()

        if self.thickness == LineThickness.THICK:
            max_thickness = bigger_side // 20
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
            variance = rnd.randrange(0, (max_thickness // 3 * 2))

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
        max_thickness_point = rnd.randrange(0, len(self.control_points) - 1)

        segments_to_left = max_thickness_point
        for i in range(0, max_thickness_point):
            point_1 = self.control_points[i]
            point_2 = self.control_points[i + 1]
            width = self.max_width - segments_to_left + 1 + i
            if width < 2:
                width = 2
            cv.line(self.damage_canvas, point_1, point_2, (255, 0, 255), width)

        for i in reversed(range(max_thickness_point + 1, len(self.control_points))):
            point_1 = self.control_points[i]
            point_2 = self.control_points[i - 1]
            width = self.max_width + (max_thickness_point - i + 1)
            if width < 2:
                width = 2
            cv.line(self.damage_canvas, point_1, point_2, (255, 0, 255), width)

    def get_control_points(self, start_point, end_point):
        """

        :param start_point: starting point of line as (x,y) coordinates
        :param end_point: end point of line as (x,y) coordinates
        :return: control points - list of (x,y) points
        """
        if self.length_type is LineLength.SHORT:
            num_of_points = rnd.randrange(3, 6)
        elif self.length_type is LineLength.MEDIUM:
            num_of_points = rnd.randrange(3, 7)
        elif self.length_type is LineLength.LONG:
            num_of_points = rnd.randrange(3, 9)
        self.control_points = np.linspace(start_point, end_point, num_of_points)
        self.control_points = self.control_points.astype(int)
        return self.control_points

    def half_points_outside(self):
        """

        @brief: determines if more than half control points of generated line lie outside of fingerprint
        :return: True if more than half control point lies outside of fingerprint area, False if not
        """

        outside_points = 0
        for point in self.control_points:
            if self.point_outside(point[1], point[0]):
                outside_points += 1
        if outside_points >= (len(self.control_points) // 2):
            return True
        return False

    def point_outside(self, point_y, point_x):
        """

        @brief: Determines if point is outside based on color of given pixel in mask (black point means outside)
        :param point_y: y coordinate of point
        :param point_x: x coordinate of point
        :return: True if point is outside, False if not
        """
        if self.background_mask[point_y, point_x] == BLACK:
            return True
        return False

    def move_control_points(self):
        """

        @brief Shifts control point in x and y axis for random value based on line length and line orientation
        :return: None
        """

        max_displacement = self.length // 9
        if max_displacement < 3:
            max_displacement = 3

        if self.orientation is LineOrientation.DIAGONAL:

            for point in self.control_points:
                displacement_x = rnd.randrange(2, max_displacement + 1)
                point[0] = point[0] + displacement_x
                displacement_y = rnd.randrange(2, max_displacement + 1)
                point[1] = point[1] + displacement_y

                if point[0] >= self.fingerprint.img_width:
                    point[0] = self.fingerprint.img_width - 1
                if point[1] >= self.fingerprint.img_height:
                    point[1] = self.fingerprint.img_height - 1

        else:
            for point in self.control_points:
                displacement_y = rnd.randrange(2, max_displacement + 1)
                displacement_x = rnd.randrange(2, max_displacement + 1)
                point[0] += displacement_x
                point[1] += displacement_y
                if point[0] >= self.fingerprint.img_width:
                    point[0] = self.fingerprint.img_width - 1
                if point[1] >= self.fingerprint.img_height:
                    point[1] = self.fingerprint.img_height - 1

    def add_width_points(self):
        """

        @brief Adds point between two control points
        :return: None
        """
        mid_points = np.array([])

        index = 0
        for point in self.control_points:
            next_index = index + 1
            if next_index > len(self.control_points) - 1:
                break

            next_point = self.control_points[next_index]
            mid_point_x = (point[0] + next_point[0]) // 2
            mid_point_y = (point[1] + next_point[1]) // 2
            index += 1
            mid_points = np.append(mid_points, [mid_point_x, mid_point_y], axis=0)

        mid_points = mid_points.reshape(-1, 2)
        mid_points = mid_points.astype(int)
        merge_points = np.array([])

        # merge mid_points with control points
        i = 0
        while i < (len(self.control_points)):
            merge_points = np.append(merge_points, self.control_points[i])
            if i < len(mid_points):
                merge_points = np.append(merge_points, mid_points[i])
            i += 1

        merge_points = merge_points.reshape(-1, 2)
        merge_points = merge_points.astype(int)
        self.control_points = merge_points

    def generate_start_end_point(self):
        """

        @brief:  Generates start and end point of line based line type (orientation and length)
        :return: start and end point of line as (x,y) coordinates
        """

        width = self.fingerprint.fingerprint_width
        height = self.fingerprint.fingerprint_height
        diagonal = int(math.sqrt(width ** 2 + height ** 2))

        scale, angle = self.get_scale_and_angle(width, height, diagonal)
        min_value, max_value = self.get_length_range(scale)

        self.length = rnd.randrange(min_value, max_value + 1)
        radian_angle = angle * (math.pi / 180)

        counter = 0
        while True:
            x1 = rnd.randrange(0, self.fingerprint.img_width)
            y1 = rnd.randrange(0, self.fingerprint.img_height)
            x2 = int(x1 + self.length * math.cos(radian_angle))
            y2 = int(y1 + self.length * math.sin(radian_angle))

            if (x2 in range(0, self.fingerprint.img_width)) and (y2 in range(0, self.fingerprint.img_height)):
                break
            counter += 1

            # avoiding infinite cycling if method fails to generate line of given length and angle
            if counter > 100:
                return -1, -1

        return (x1, y1), (x2, y2)

    def get_length_range(self, scale):
        """

        @brief: Function determines interval of possible lengths of line determined by length type and scale
                (which is determined by orientation)
        :param scale: size of horizontal, vertical or diagonal line of bounding rect around fingerprint
        :return: left and right value of interval of possible length for line as int
        """
        if self.length_type is LineLength.SHORT:
            min_value = scale // 10
            max_value = int(scale * 0.3)
        elif self.length_type is LineLength.MEDIUM:
            min_value = int(scale * 0.4)
            max_value = int(scale * 0.7)
        elif self.length_type is LineLength.LONG:
            min_value = int(scale * 0.7)
            max_value = int(scale * 1)
        return min_value, max_value

    def get_scale_and_angle(self, width, height, diagonal):
        """

        @brief: Based on line orientation determines scale (horizontal side, vertical side or diagonal line of
                fingerprint bounding rect) used for generating line size and randomly generates angle
        :param width: width of fingerprint
        :param height: height of fingerprint
        :param diagonal: size of diagonal of fingerprint
        :return: scale and randomly generated angle of line (both as integers)
        """
        if self.orientation is LineOrientation.HORIZONTAL:
            angle = rnd.choice((0, 180))
            variance = rnd.randrange(0, 10)
            angle += variance
            if angle < 0:
                angle = 360 + angle
            scale = width

        elif self.orientation is LineOrientation.VERTICAL:
            angle = rnd.choice((90, 270))
            variance = rnd.randrange(-10, 10)
            angle += variance
            if angle < 0:
                angle = 360 + angle
            scale = height
        elif self.orientation is LineOrientation.DIAGONAL:
            angle = rnd.choice((45, 135, 225, 315))
            variance = rnd.randrange(-35, 35)
            angle += variance
            if angle < 0:
                angle = 360 + angle
            scale = diagonal * 0.7
        return scale, angle
