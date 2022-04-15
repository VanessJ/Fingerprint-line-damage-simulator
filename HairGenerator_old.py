import math

from Generator import Generator
from HairGenerator import HairGenerator, HairLength
import cv2 as cv
import numpy as np
import random as rnd
import enum



class HairGenerator(Generator):

    def __init__(self, fingerprint):
        super().__init__(fingerprint)
        self.length_type = None
        self.points = None

    def generate_hair(self, length=HairLength.LONG):
        hair = HairGenerator(self.fingerprint)
        hair.generate_hair(HairLength.SHORT)
        self.background = hair.background

    # def generate_hair(self, length=HairLength.LONG):
    #     if length == HairLength.RANDOM:
    #         self.length_type = rnd.choice((HairLength.SHORT, HairLength.LONG))
    #     else:
    #         self.length_type = length
    #
    #     while True:
    #
    #         hair = CurveGenerator(self.fingerprint)
    #         start_point, end_point, control_point = hair.get_start_end_and_control_point()
    #         hair.quadratic_bezier(start_point, end_point, control_point)
    #         #self.quadratic_bezier(start_point, end_point, control_point)
    #         self.points = hair.points
    #         if self.length_type is HairLength.LONG:
    #             point = self.points[len(self.points)-1]
    #             if (self.background_mask[point[1], point[0]] == 0) and (self.all_points_outside() is False):
    #                 break;
    #         else:
    #             if self.all_points_outside() is False:
    #                 break
    #     self.draw_hair()
    #     self.hair_irregularity()

    def all_points_outside(self):
        outside_points = 0
        for point in self.points:
            if self.background_mask[point[1], point[0]] == 0:
                outside_points += 1
        if outside_points >= len(self.points):
            return True
        return False

    def hair_irregularity(self):
        opacity_damage_level = rnd.randrange(0, 6)
        if opacity_damage_level > 0:
            for p in self.points:
                x = rnd.randrange(0, 10)
                if x < opacity_damage_level:
                    cv.circle(self.background, p, 1, (255, 0, 255), -1)

    def draw_hair(self):
        if self.fingerprint.img_width > self.fingerprint.img_height:
            bigger_side = self.fingerprint.fingerprint_width
        else:
            bigger_side = self.fingerprint.fingerprint_height

        width = int(bigger_side/150)

        variance = rnd.randrange(0, width)
        width += variance
        if width < 3:
            width = 3
        cv.polylines(self.damage_canvas, [self.points], False, 255, int(width))
        self.line_irregularity(width)
        self.draw_on_background()
        self.crop_by_mask()
        hair_opacity = rnd.randrange(180, 210)
        cv.polylines(self.background, [self.points], False, hair_opacity, 1)
        self.crop_by_mask()

    def line_irregularity(self,  width):
        circle_radius = width - 1
        if circle_radius <= 0:
            circle_radius = 1
        for p in self.points:
            x = rnd.randrange(0, 3)
            for x in range(0, x):

                if width > 5:
                    variance = int(circle_radius/3)
                else:
                    variance = 2
                if variance != 0:
                    x_variance = rnd.randrange(-variance, variance+1)
                    y_variance = rnd.randrange(-variance, variance+1)
                else:
                    x_variance = rnd.choice((-1, 1))
                    y_variance = rnd.choice((-1, 1))
                new_x = p[0] + x_variance
                new_y = p[1] + y_variance
                cv.circle(self.damage_canvas, (new_x, new_y), circle_radius, (255, 0, 255), -1)

    def generate_points(self):
        self.split_fingerprint_and_background_pixels()

        if self.fingerprint.img_width > self.fingerprint.img_height:
            bigger_size = self.fingerprint.img_width
        else:
            bigger_size = self.fingerprint.img_height
        if self.length_type == HairLength.LONG:
            side = rnd.choice(('x', 'y'))
            if side == 'x':
                start_x = 0
                end_x = self.fingerprint.img_width
                start_y = rnd.randrange(0, self.fingerprint.img_height)
                end_y = rnd.randrange(0, self.fingerprint.img_height)
            else:
                start_y = 0
                end_y = self.fingerprint.img_height
                start_x = rnd.randrange(0, self.fingerprint.img_width)
                end_x = rnd.randrange(0, self.fingerprint.img_width)

            start_point = (start_x, start_y)
            end_point = (end_x, end_y)
        else:
            while True:
                index_1 = np.random.choice(self.fingerprint_pixels.shape[0], 1, replace=False)
                index_2 = np.random.choice(self.fingerprint_pixels.shape[0], 1, replace=False)
                start_point = self.fingerprint_pixels[index_1][0]
                end_point = self.fingerprint_pixels[index_2][0]
                start_point = (start_point[1], start_point[0])
                end_point = (end_point[1], end_point[0])
                distance = math.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)
                if distance > bigger_size / 4:
                    break

        control_x = rnd.randrange(0, self.fingerprint.img_width)
        control_y = rnd.randrange(0, self.fingerprint.img_height)
        return start_point, end_point, (control_x, control_y)

    def quadratic_bezier(self, start_point, end_point, control_point):

        bezier_points = np.array([])
        for x in range(0, 1001, 1):
            t = x / 1000
            point_x = int(
                math.pow(1 - t, 2) * start_point[0] + 2 * (1 - t) * t * control_point[0] + math.pow(t, 2) * end_point[
                    0])
            if point_x < 0:
                point_x = 0
            if point_x >= self.fingerprint.img_width:
                point_x = self.fingerprint.img_width - 1
            point_y = int(
                math.pow(1 - t, 2) * start_point[1] + 2 * (1 - t) * t * control_point[1] + math.pow(t, 2) * end_point[
                    0])
            if point_y < 0:
                point_y = 0
            if point_y >= self.fingerprint.img_height:
                point_y = self.fingerprint.img_height - 1

            bezier_points = np.append(bezier_points, [point_x, point_y], axis=0)

        bezier_points = bezier_points.reshape(-1, 2)
        bezier_points = bezier_points.astype(int)
        self.points = bezier_points






