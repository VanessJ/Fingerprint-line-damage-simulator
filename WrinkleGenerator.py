from LineGenerator import LineGenerator, LineOrientation, LineLength, LineThickness
import random as random
import cv2 as cv

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

    def wrinkles_level_1(self):
        """

        @brief:  Generates creases of level 1 (damage consisting of 4-6 individual lines).
        :return: None
        """
        max_amount = random.randrange(4, 7)

        # amount of primary wrinkles (thin or medium, long or medium)
        amount = random.randrange(1, 4)
        generate = random.randrange(0, 6)
        if generate < 5:
            thickness = LineThickness.THIN
        else:
            thickness = LineThickness.MEDIUM

        for x in range(0, amount):

            generate = random.randrange(0, 20)
            if generate < 16:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL

            line_length = random.choice((LineLength.LONG, LineLength.MEDIUM))
            self.line_generator.generate_line(length_type=line_length, orientation=orientation,
                                              thickness=thickness)

        # short thin wrinkles added to get final amount of wrinkles in image
        small_wrinkles_amount = max_amount - amount
        if small_wrinkles_amount < 0:
            small_wrinkles_amount = 0
        for x in range(0, small_wrinkles_amount):
            self.line_generator.generate_line(length_type=LineLength.SHORT, orientation=LineOrientation.HORIZONTAL,
                                              thickness=LineThickness.THIN)

        self.generated_image = self.line_generator.background.copy()

    def wrinkles_level_2(self):
        """

        @brief:  Generates creases of level 2 (damage consisting of 6-12 individual lines).
        :return: None
        """

        max_amount = random.randrange(6, 12)

        # amount of primary wrinkles (thin or medium and long or medium)
        amount = random.randrange(2, 8)
        generate = random.randrange(0, 6)
        if generate < 5:
            thickness = LineThickness.THIN
        else:
            thickness = LineThickness.MEDIUM
        for x in range(0, amount):
            generate = random.randrange(0, 20)
            if generate < 16:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL
            line_length = random.choice((LineLength.LONG, LineLength.MEDIUM))
            self.line_generator.generate_line(length_type=line_length, orientation=orientation,
                                              thickness=thickness)

        # short thin wrinkles added to get final amount of wrinkles in image
        small_wrinkles_amount = max_amount - amount
        if small_wrinkles_amount < 0:
            small_wrinkles_amount = 0
        for x in range(0, small_wrinkles_amount):
            self.line_generator.generate_line(length_type=LineLength.SHORT, orientation=LineOrientation.HORIZONTAL,
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
            self.line_generator.generate_line(length_type=LineLength.LONG, orientation=LineOrientation.RANDOM,
                                              thickness=LineThickness.THICK)

        # amount of medium wrinkles
        medium_amount = random.randrange(1, 5)
        for x in range(0, medium_amount):
            generate = random.randrange(0, 20)
            if generate < 13:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 18:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL
            line_len = random.choice((LineLength.LONG, LineLength.MEDIUM))
            self.line_generator.generate_line(length_type=line_len, orientation=orientation,
                                              thickness=LineThickness.MEDIUM)

        # amount of long thin wrinkles
        long_amount = random.randrange(0, 7)
        for x in range(0, long_amount):

            generate = random.randrange(0, 11)
            if generate < 6:
                orientation = LineOrientation.HORIZONTAL
            elif generate < 9:
                orientation = LineOrientation.VERTICAL
            else:
                orientation = LineOrientation.DIAGONAL

            self.line_generator.generate_line(length_type=LineLength.LONG, orientation=orientation,
                                              thickness=LineThickness.THIN)

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

            self.line_generator.generate_line(length_type=line_len, orientation=orientation,
                                              thickness=LineThickness.THIN)
        self.generated_image = self.line_generator.background.copy()

    def show_generated_image(self):
        """

        @brief Shows generated image
        :return: None
        """
        cv.imshow("Wrinkles", self.generated_image)
        cv.waitKey(0)
