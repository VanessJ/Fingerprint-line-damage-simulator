import math
import cv2 as cv
import numpy as np
import random as rnd
import enum


class LineLength(enum.Enum):
    """
    Values representing different length types of line damage
    """
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    RANDOM = 4


class LineOrientation(enum.Enum):
    """
    Values representing different orientation types of line damage
    """
    HORIZONTAL = 1
    VERTICAL = 2
    DIAGONAL = 3
    RANDOM = 4


class LineThickness(enum.Enum):
    """
    Values representing different thickness types of line damage
    """
    THIN = 1
    MEDIUM = 2
    THICK = 3
    RANDOM = 4


class DamageLine:
    """
    Class representing irregular line used for simulating line damage in synthetic fingerprint with variable width
    """

    def __init__(self):
        self.control_points = None
        self.orientation = None
        self.length_type = None
        self.thickness_type = None
        self.control_points = None
        self.max_width = None
        self.length = None

        @staticmethod
        def distance(point_1, point_2):
            """
            @brief Calculates distance between points
            :param point_1: first_point
            :param point_2: second point
            :return: distance between two points
            """
            return int(math.sqrt((point_2[0] - point_1[0]) ** 2 + (point_2[1] - point_1[1]) ** 2))
