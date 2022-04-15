import math

import numpy as np
import enum
import random as rnd
import cv2 as cv

from FingerprintImage import FingerprintImage
from Generator import Generator


class HairLength(enum.Enum):
    SHORT = 1
    LONG = 2
    RANDOM = 3


def check_line_length(distance_between_points, bigger_side_size):
    """

    @brief: Checks if hair is long enough
    :param distance_between_points: Distance between start and end point
    :param bigger_side_size: Bigger side of image as scale
    :return: None
    """
    if distance_between_points > bigger_side_size / 4:
        return True
    else:
        return False


class HairGenerator(Generator):
    """

    Class generating hair into synthetic fingerprint image
    Attributes:
        :length_type     SHORT or LONG
        :points          array of points of curve in (x,y) coordinate format
        :fingerprint     instance of Fingerprint class with
    """

    def __init__(self, fingerprint: FingerprintImage):
        super().__init__(fingerprint)
        self.length_type = None
        self.points = None

    def set_length_type(self, length_type):
        """

        @brief: Sets length type, in case of random type randomly selects type
        :param length_type: short hair (in area of fingerprint) or large hair (larger than fingerprint area)
        :return:
        """
        if length_type == HairLength.RANDOM:
            self.length_type = rnd.choice((HairLength.SHORT, HairLength.LONG))
        else:
            self.length_type = length_type

    def generate_hair(self, length_type=HairLength.RANDOM):
        """

        @brief: Generate hair of given type
        :param length_type:
        :return:
        """
        self.set_length_type(length_type)

        while True:
            start_point, end_point, control_point = self.get_start_end_and_control_point()

            self.quadratic_bezier(start_point, end_point, control_point)
            if self.length_type is HairLength.LONG:
                point = self.points[len(self.points) - 1]
                if (self.background_mask[point[1], point[0]] == 0) and (
                        self.all_points_outside_fingerprint_area() is False):
                    break;
            else:
                if self.all_points_outside_fingerprint_area() is False:
                    break
        self.draw_hair()
        self.hair_opacity_damage()

    def draw_hair(self):
        """

        @brief: Draw hair damage (hair and crease around hair)
        :return: None
        """

        bigger_side_size = self.get_bigger_fingerprint_side_size()

        width = int(bigger_side_size / 150)
        variance = rnd.randrange(0, width)
        width += variance
        if width < 3:
            width = 3

        # draw crease around hair
        cv.polylines(self.damage_canvas, [self.points], False, 255, int(width))
        self.crease_irregularities(width)
        self.draw_on_background()
        self.crop_by_mask()

        # draw hair
        hair_opacity = rnd.randrange(180, 210)
        cv.polylines(self.background, [self.points], False, hair_opacity, 1)
        self.crop_by_mask()

    def hair_opacity_damage(self):
        """

        @brief: Draws small white circles over some parts of hair to lower it's opacity
        :return: None
        """
        opacity_damage_level = rnd.randrange(1, 6)
        for p in self.points:
            x = rnd.randrange(0, 10)
            if x < opacity_damage_level:
                cv.circle(self.background, p, 1, (255, 0, 255), -1)

    def get_start_end_and_control_point(self):
        """

        @brief: gets start point, end point and control point depending on
        :return: start, end and control point of bezier curve as (x, y) coordinates
        """

        self.split_fingerprint_and_background_pixels()
        bigger_side_size = self.get_bigger_side_size()

        if self.length_type == HairLength.LONG:
            side = rnd.choice(('X', 'Y'))
            if side == 'X':
                start_x = 0
                end_x = self.background_width
                start_y = rnd.randrange(0, self.background_height)
                end_y = rnd.randrange(0, self.background_height)
            elif side == 'Y':
                start_y = 0
                end_y = self.background_height
                start_x = rnd.randrange(0, self.background_width)
                end_x = rnd.randrange(0, self.background_width)

            start_point = (start_x, start_y)
            end_point = (end_x, end_y)

        elif self.length_type == HairLength.SHORT:
            start_point, end_point = self.get_two_points_inside_fingerprint(bigger_side_size)

        control_x = rnd.randrange(0, self.fingerprint.img_width)
        control_y = rnd.randrange(0, self.fingerprint.img_height)
        control_point = (control_x, control_y)
        return start_point, end_point, control_point

    def get_two_points_inside_fingerprint(self, bigger_side_size):
        """

        @brief: Randomly generates two points in fingerprint area
        :param bigger_side_size: Bigger side of image
        :return: start and end point as (x, y) coordinates
        """
        while True:
            index_1 = np.random.choice(self.fingerprint_pixels.shape[0], 1, replace=False)
            index_2 = np.random.choice(self.fingerprint_pixels.shape[0], 1, replace=False)
            start_point = self.fingerprint_pixels[index_1][0]
            end_point = self.fingerprint_pixels[index_2][0]
            start_point = (start_point[1], start_point[0])
            end_point = (end_point[1], end_point[0])
            distance = math.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)
            if check_line_length(distance, bigger_side_size):
                return start_point, end_point

    def quadratic_bezier(self, start_point, end_point, control_point):
        """

        @brief: Calculates points of bezier curve given by start, end and control point
        :param start_point: Starting point of bezier curve in as (x,y) coordinates
        :param end_point: End point of bezier curve as (x,y) coordinates
        :param control_point: Control point of bezier curve as (x,y) coordinates
        :return: None
        """

        bezier_points = np.array([])
        for i in range(0, 1001, 1):
            t = i / 1000

            point_x = self.calculate_x(start_point, end_point, control_point, t)
            point_y = self.calculate_y(start_point, end_point, control_point, t)

            bezier_points = np.append(bezier_points, [point_x, point_y], axis=0)

        bezier_points = bezier_points.reshape(-1, 2)
        bezier_points = bezier_points.astype(int)
        self.points = bezier_points

    def calculate_x(self, start_point, end_point, control_point, t):
        """

        @brief: calculates x coordinate of point in bezier curve
        :param start_point: Starting point of bezier curve
        :param end_point: End point of bezier curve
        :param control_point: Control point of bezier curve
        :param t: step (between 0-1)
        :return: x coordinate of point
        """
        start_x = start_point[0]
        end_x = end_point[0]
        control_x = control_point[0]
        point_x = int(
            math.pow(1 - t, 2) * start_x + 2 * (1 - t) * t * control_x + math.pow(t, 2) * end_x)

        if point_x < 0:
            point_x = 0

        if point_x >= self.fingerprint.img_width:
            point_x = self.fingerprint.img_width - 1
        return point_x

    def calculate_y(self, start_point, end_point, control_point, t):
        """

        @brief: calculates y coordinate of point in bezier curve
        :param start_point: Starting point of bezier curve as (x,y) coordinates
        :param end_point: End point of bezier curve  as (x,y) coordinates
        :param control_point: Control point of bezier curve  as (x,y) coordinates
        :param t: step (between 0-1)
        :return: y coordinate of point
        """
        start_y = start_point[1]
        end_y = end_point[1]
        control_y = control_point[1]

        point_y = int(
            math.pow(1 - t, 2) * start_y + 2 * (1 - t) * t * control_y + math.pow(t, 2) * end_y)
        if point_y < 0:
            point_y = 0
        if point_y >= self.fingerprint.img_height:
            point_y = self.fingerprint.img_height - 1
        return point_y

    def crease_irregularities(self, width):
        """

        @brief: On every point of bezier line draws white circle with radius size depending on line width shifted
        by random amount in axis x and y, creating irregular line
        :param width: width of crease
        :return: None
        """
        circle_radius = width - 1
        if circle_radius <= 0:
            circle_radius = 1

        for p in self.points:
            x = rnd.randrange(0, 3)
            for x in range(0, x):
                if width > 5:
                    variance = int(circle_radius / 3)
                else:
                    variance = 2

                if variance != 0:
                    x_variance = rnd.randrange(-variance, variance + 1)
                    y_variance = rnd.randrange(-variance, variance + 1)
                else:
                    x_variance = rnd.choice((-1, 1))
                    y_variance = rnd.choice((-1, 1))

                new_x = p[0] + x_variance
                new_y = p[1] + y_variance
                cv.circle(self.damage_canvas, (new_x, new_y), circle_radius, (255, 0, 255), -1)

    def all_points_outside_fingerprint_area(self):
        """

        @brief: Checks if control points of bezier curve lie within fingerprint area
        :return: True or False
        """
        outside_points = 0
        for point in self.points:
            # control points are in (x,y) format, coordinates must be swapped
            if self.background_mask[point[1], point[0]] == 0:
                outside_points += 1
        if outside_points >= len(self.points):
            return True
        return False
