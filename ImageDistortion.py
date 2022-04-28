import math
import numpy as np
import cv2 as cv


class ImageOperation:
    """

    Class consisting of image on which transformations will be applied, all important information for transformation
    and methods implementing conversions between coordinates
    """

    # [MIN, MAX]
    NORM_SETTINGS = [-1, 1]

    def __init__(self, arr_image, bi_linear_interpolation=False):
        """

        :param arr_image: 2D array of image pixels
        :param bi_linear_interpolation: True enables bilinear interpolation
        """
        self.arrImage = arr_image
        self.height = arr_image.shape[0]
        self.width = arr_image.shape[1]

        self.bi_linear_interpolation = bi_linear_interpolation
        self.result_image = np.zeros(arr_image.shape)

    def get_value_by_image_cords(self, y, x):
        """

        @brief: Gets value of pixel on given coordinates
        :param y: Y coordinate of pixel
        :param x: X coordinate of pixel
        :return: Value of pixel (0-255) or 0 if pixel is non existent
        """
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.arrImage[y, x]
        else:
            return 0

    def get_value_by_norm_cords(self, norm_y, norm_x):
        """

        @brief: Converts normalized coordinates to standard and returns pixel value
        :param norm_y: Normalized y coordinate (between -1 and 1)
        :param norm_x: Normalized x coordinate (between -1 and 1)
        :return: Pixel value (0-255)
        """
        y = ((norm_y - self.NORM_SETTINGS[0]) / (self.NORM_SETTINGS[1] - self.NORM_SETTINGS[0]) * self.height)
        x = ((norm_x - self.NORM_SETTINGS[0]) / (self.NORM_SETTINGS[1] - self.NORM_SETTINGS[0]) * self.width)

        y_base = math.floor(y)
        x_base = math.floor(x)

        if self.bi_linear_interpolation:
            y_next = y_base + 1
            x_next = x_base + 1

            Q11 = self.get_value_by_image_cords(y_base, x_base)
            Q12 = self.get_value_by_image_cords(y_base, x_next)
            Q21 = self.get_value_by_image_cords(y_next, x_base)
            Q22 = self.get_value_by_image_cords(y_next, x_next)

            total = (x_next - x_base) * (y_next - y_base)
            Q11_ratio = (x_next - x) * (y_next - y)
            Q12_ratio = (x_next - x) * (y - y_base)
            Q21_ratio = (x - x_base) * (y_next - y)
            Q22_ratio = (x - x_base) * (y - y_base)

            result = (Q11_ratio / total * Q11) + (Q12_ratio / total * Q12) + \
                     (Q21_ratio / total * Q21) + (Q22_ratio / total * Q22)

            return result
        else:
            return self.get_value_by_image_cords(y_base, x_base)

    # Cords out of bounds will result in 0
    def get_value_by_polar_cords(self, phi, r):
        """

        @brief: Converts polar coordinates to standard and returns pixel value
        :param phi: Angle from the x-axis
        :param r: Radial distance from origin
        :return: Pixel value (0-255)
        """
        norm_y = r * math.sin(phi)
        norm_x = r * math.cos(phi)

        return self.get_value_by_norm_cords(norm_y, norm_x)

    def get_norm_cords_from_image_cords(self, y, x):
        """

        @brief Gets normal coordinates (number between 0 and 1) of given pixel
        :param y: Y coordinate of pixel
        :param x: X coordinate of pixel
        :return: Tuple of normalized (y,x) coordinates of pixel
        """
        norm_y = (y / (self.height - 1)) * \
                 (abs(self.NORM_SETTINGS[0]) + self.NORM_SETTINGS[1]) + self.NORM_SETTINGS[0]

        norm_x = (x / (self.width - 1)) * \
                 (abs(self.NORM_SETTINGS[0]) + self.NORM_SETTINGS[1]) + self.NORM_SETTINGS[0]

        return tuple([norm_y, norm_x])

    def get_polar_cords_from_image_cords(self, y, x):
        """

        @brief: Gets polar coordinates of pixel with (y, x) standard coordinates
        :param y: Y coordinate of pixel
        :param x: X coordinate of pixel
        :return: Polar coordinates of pixel as (phi, r)
        """
        norm_cords = self.get_norm_cords_from_image_cords(y, x)

        r = math.sqrt(norm_cords[0] ** 2 + norm_cords[1] ** 2)
        phi = math.atan2(norm_cords[0], norm_cords[1])

        return tuple([phi, r])

    def get_norm_cords_from_image_cords_in_area(self, y, x, center_y, center_x, radius):
        """

        @brief Returns normal coordinates of pixel based on circular area, not whole picture
        :param y: Y coordinate of pixel
        :param x: X coordinate of pixel
        :param center_y: Y coordinate of center of the circular area
        :param center_x: X coordinate of center of the circular area
        :param radius:  radius of the circular area
        :return: normal coordinates of pixel as (y,x)
        """

        if center_x + radius >= self.width or center_x - radius < 0 or \
                center_y + radius >= self.height or center_y - radius < 0:
            return -1

        norm_y = ((y - (center_y - radius)) / ((center_y + radius) - (center_y - radius))) * \
                 (abs(self.NORM_SETTINGS[0]) + self.NORM_SETTINGS[1]) + self.NORM_SETTINGS[0]

        norm_x = ((x - (center_x - radius)) / ((center_x + radius) - (center_x - radius))) * \
                 (abs(self.NORM_SETTINGS[0]) + self.NORM_SETTINGS[1]) + self.NORM_SETTINGS[0]

        return tuple([norm_y, norm_x])

    def get_polar_cords_from_image_cords_in_area(self, y, x, center_y, center_x, radius):
        """

        @brief Returns polar coordinates of pixel based on circular area, not whole picture
        :param y: Y coordinate of pixel
        :param x: X coordinate of pixel
        :param center_y: Y coordinate of center of the circular area
        :param center_x: X coordinate of center of the circular area
        :param radius:  radius of the circular area
        :return: polar coordinates of pixel as (y, x)
        """
        norm_cords = self.get_norm_cords_from_image_cords_in_area(y, x, center_y, center_x, radius)
        return self.get_polar_cords_from_norm_cord(norm_cords[0], norm_cords[1])

    @staticmethod
    def get_polar_cords_from_norm_cord(norm_y, norm_x):
        """

        @brief Converts polar coordinates to normal coordinates
        :param norm_y: Y coordinate of normal coordinate of pixel
        :param norm_x: X coordinate of normal coordinate of pixel
        :return: polar coordinates of pixel as (phi, r)
        """
        r = math.sqrt(norm_y ** 2 + norm_x ** 2)
        phi = math.atan2(norm_y, norm_x)

        return tuple([phi, r])

    def get_value_by_norm_cords_in_area(self, norm_y, norm_x, center_y, center_x, radius):
        """

        @brief Gets value of pixel by his normal coordinates. Normal coordinates are based on circular area,
                not whole picture
        :param norm_y: Normal y coordinate of pixel
        :param norm_x: Normal x coordinate of pixel
        :param center_y: Y coordinate of center of the circular area
        :param center_x: X coordinate of center of the circular area
        :param radius:  radius of the circular area
        :return: value of pixel between (0-255)
        """

        y = ((norm_y - self.NORM_SETTINGS[0]) / (self.NORM_SETTINGS[1] - self.NORM_SETTINGS[0]) *
             ((center_y + radius) - (center_y - radius)) + (center_y - radius))

        x = ((norm_x - self.NORM_SETTINGS[0]) / (self.NORM_SETTINGS[1] - self.NORM_SETTINGS[0]) *
             ((center_x + radius) - (center_x - radius)) + (center_x - radius))

        y_base = math.floor(y)
        x_base = math.floor(x)

        if self.bi_linear_interpolation:
            y_next = y_base + 1
            x_next = x_base + 1

            Q11 = self.get_value_by_image_cords(y_base, x_base)
            Q12 = self.get_value_by_image_cords(y_base, x_next)
            Q21 = self.get_value_by_image_cords(y_next, x_base)
            Q22 = self.get_value_by_image_cords(y_next, x_next)

            total = (x_next - x_base) * (y_next - y_base)
            Q11_ratio = (x_next - x) * (y_next - y)
            Q12_ratio = (x_next - x) * (y - y_base)
            Q21_ratio = (x - x_base) * (y_next - y)
            Q22_ratio = (x - x_base) * (y - y_base)

            result = (Q11_ratio / total * Q11) + (Q12_ratio / total * Q12) + \
                     (Q21_ratio / total * Q21) + (Q22_ratio / total * Q22)
            return result
        else:
            return self.get_value_by_image_cords(y_base, x_base)

    def get_value_by_polar_cords_in_area(self, phi, r, center_y, center_x, radius):
        """

        @brief Gets value of pixel by his polar coordinates. Polar coordinates are based on circular area,
                not whole picture
        :param phi: Angle from the x-axis
        :param r: Radial distance from origin
        :param center_y: Y coordinate of center of the circular area
        :param center_x: X coordinate of center of the circular area
        :param radius:  radius of the circular area
        :return: value of pixel between (0-255)
        """
        norm_y = r * math.sin(phi)
        norm_x = r * math.cos(phi)

        return self.get_value_by_norm_cords_in_area(norm_y, norm_x, center_y, center_x, radius)

    def reset_result_to_original(self):
        """

        @brief: Sets result of transformation as new image
        :return: None
        """
        self.arrImage = self.result_image.astype(np.uint8)
        self.result_image = np.zeros(self.arrImage.shape)


def soak_of_circle_area(image_operation: ImageOperation, center_y, center_x, radius, c, lin_interpolation=True):
    """

    @brief: Performs pincushion (soak) distortion in circular area given by center and radius
    :param image_operation: instance of class ImageOperation with image loaded
    :param center_y: Y coordinate of center of the circular area
    :param center_x: X coordinate of center of the circular area
    :param radius: Radius of the circular area
    :param c: Intensity of transformation
    :param lin_interpolation: Toggle linear interpolation on/off
    :return: None
    """
    min_y = (center_y - radius)
    max_y = (center_y + radius)
    min_x = (center_x - radius)
    max_x = (center_x + radius)

    for y in range(image_operation.height):
        for x in range(image_operation.width):
            if min_y <= y <= max_y and min_x <= x <= max_x:

                norm_cords = image_operation.get_norm_cords_from_image_cords_in_area(y, x, center_y, center_x, radius)
                if norm_cords == -1:
                    return

                if norm_cords[0] ** 2 + norm_cords[1] ** 2 < 1:
                    polar_cords = image_operation.get_polar_cords_from_norm_cord(norm_cords[0], norm_cords[1])
                    if lin_interpolation:
                        new_r = polar_cords[1] ** 2 + (1.0 - polar_cords[1]) * c * math.sqrt(polar_cords[1])
                    else:
                        new_r = c * math.sqrt(polar_cords[1])
                    image_operation.result_image[y, x] = \
                        image_operation.get_value_by_polar_cords_in_area(polar_cords[0], new_r,
                                                                         center_y, center_x, radius)
                else:
                    image_operation.result_image[y, x] = image_operation.arrImage[y, x]
            else:
                image_operation.result_image[y, x] = image_operation.arrImage[y, x]
    image_operation.reset_result_to_original()


def test_soak(image_operation: ImageOperation, area_mask, c, lin_interpolation=True):
    height, width = image_operation.result_image.shape
    min_y = 0
    max_y = height
    min_x = 0
    max_x = width

    distortion_pixels = np.transpose(np.where(area_mask == 255))
    unchanged_pixels = np.transpose(np.where(area_mask == 0))

    for point in distortion_pixels:
        x = point[0]
        y = point[1]
        if min_y <= y <= max_y and min_x <= x <= max_x:
            norm_coords = image_operation.get_norm_cords_from_image_cords(x, y)
            polar_cords = image_operation.get_polar_cords_from_norm_cord(norm_coords[0], norm_coords[1])
            if lin_interpolation:
                new_r = polar_cords[1] ** 2 + (1.0 - polar_cords[1]) * c * math.sqrt(polar_cords[1])
            else:
                new_r = c * math.sqrt(polar_cords[1])
            image_operation.result_image[x, y] = \
                image_operation.get_value_by_polar_cords(polar_cords[0], new_r)

    for pixel in unchanged_pixels:
        x = pixel[0]
        y = pixel[1]
        image_operation.result_image[x, y] = image_operation.arrImage[x, y]

    cv.imshow("test", image_operation.result_image)
    cv.waitKey(0)
