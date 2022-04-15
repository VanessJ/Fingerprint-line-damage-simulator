from FingerprintImage import FingerprintImage
from LineGenerator import LineGenerator, LineOrientation, LineLength, LineThickness
import random, os
from ScarGenerator import ScarGenerator
from ImageDistortion import *
from HairGenerator import HairGenerator
from WrinkleGenerator import WrinkleGenerator

def choose_random_img_from_directory(directory):
    file = random.choice(os.listdir(directory))
    path = directory + '\\' + file
    return path


def wrinkles_level_1(line_generator):
    max_amount = (4, 7)
    amount = random.randrange(1, 4)
    generate = random.randrange(0, 6)
    if generate < 5:
        thickness = LineThickness.THIN
    else:
        thickness = LineThickness.MEDIUM
    for x in range (0, amount):
        generate = random.randrange(0, 20)
        if generate < 16:
            orientation = LineOrientation.HORIZONTAL
        elif generate < 18:
            orientation = LineOrientation.VERTICAL
        else:
            orientation = LineOrientation.DIAGONAL
        line_length = random.choice((LineLength.LONG, LineLength.MEDIUM))
        line_generator.generate_line(length_type=line_length, orientation=orientation,
                                     thickness=thickness)

    if max_amount > 4:
        small_wrinkles_amount = max_amount - amount
    for i in range(0, small_wrinkles_amount):
        line_generator.generate_line(length_type=LineLength.SHORT, orientation=LineOrientation.HORIZONTAL,
                                     thickness=LineThickness.THIN)


def wrinkles_level_2(line_generator):
    max_amount = (8, 12)
    amount = random.randrange(2, 8)
    generate = random.randrange(0, 6)
    if generate < 5:
        thickness = LineThickness.THIN
    else:
        thickness = LineThickness.MEDIUM
    for x in range (0, amount):
        generate = random.randrange(0, 20)
        if generate < 16:
            orientation = LineOrientation.HORIZONTAL
        elif generate < 18:
            orientation = LineOrientation.VERTICAL
        else:
            orientation = LineOrientation.DIAGONAL
        line_length = random.choice((LineLength.LONG, LineLength.MEDIUM))
        line_generator.generate_line(length_type=line_length, orientation=orientation,
                                     thickness=thickness)
    small_wrinkles_amount = max_amount - amount
    for x in range(0, small_wrinkles_amount):
        line_generator.generate_line(length_type=LineLength.SHORT, orientation=LineOrientation.HORIZONTAL,
                                     thickness=LineThickness.THIN)


def wrinkles_level_3(line_generator):
    total_amount = random.randrange(12, 21)
    generate_thick = random.randrange(0, 2)
    if generate_thick:
        line_generator.generate_line(length_type=LineLength.LONG, orientation=LineOrientation.RANDOM, thickness=LineThickness.THICK)
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
        line_generator.generate_line(length_type=line_len, orientation=orientation, thickness=LineThickness.MEDIUM)

    long_amount = random.randrange(0, 7)
    for x in range(0, long_amount):

        generate = random.randrange(0, 11)
        if generate < 6:
            orientation = LineOrientation.HORIZONTAL
        elif generate < 9:
            orientation = LineOrientation.VERTICAL
        else:
            orientation = LineOrientation.DIAGONAL

        line_generator.generate_line(length_type=LineLength.LONG, orientation=orientation, thickness=LineThickness.THIN)

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

        line_generator.generate_line(length_type=line_len, orientation=orientation, thickness=LineThickness.THIN)



if __name__ == '__main__':
    # fingerprint = FingerprintImage('SG_12.png')
    # fingerprint.create_mask()
    # line_generator = LineGenerator()
    # line_generator.set_fingerprint(fingerprint)

    # curve_generator = HairGenerator()
    # curve_generator.set_fingerprint(fingerprint)
    # curve_generator.generate_hair()
    # curve_generator.show_background()

    # for x in range(0, 10):
    #     line_generator.set_fingerprint(fingerprint)
    #     wrinkles_level_1(line_generator)


    # for x in range(0, 4):
    #       line_generator.generate_line(length=LineLength.short, orientation=LineOrientation.random, thickness=LineThickness.medium)
    #
    # for x in range(0, 10):
    #        line_generator.generate_line(length=LineLength.long, orientation=LineOrientation.random, thickness=LineThickness.thick)
    # line_generator.show_background()

    # scar_generator = ScarGenerator()
    # scar_generator.set_fingerprint(fingerprint)
    # for x in range(0, 1):
    #     scar_generator.generate_line(length=LineLength.long, orientation=LineOrientation.random, thickness=LineThickness.medium)
    # #cv.imshow("Black_background", scar_generator.black_background)
    # scar_generator.show_background()
    # cv.waitKey(0)

    for x in range(0, 100):

        image = choose_random_img_from_directory(r"C:\Users\vanes\PycharmProjects\BP_rework\synteticke")
        fingerprint = FingerprintImage()
        fingerprint.load_file_from_path(image)

        wrinkle_generator = WrinkleGenerator(fingerprint)
        wrinkle_generator.wrinkles_level_2()
        wrinkle_generator.show_generated_image()

        # scar_generator = ScarGenerator(fingerprint)
        # scar_generator.generate_line()
        # scar_generator.show_background()

        # name = 'scar' + str(x+1) + '.png'
        # print(name)
        # path = r'C:\Users\vanes\PycharmProjects\BP\Generated\Scar\Distortion\medium_long'
        # img = scar_generator.background
        # scar_generator.show_background()
        # cv.imwrite(os.path.join(path, name), img)










