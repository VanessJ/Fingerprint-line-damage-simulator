#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Vanessa Jóriová
# Date        : 8.5.2022
# Version     : 1.0

import argparse
import os
import random

import cv2

from PIL import Image
from FingerprintImage import FingerprintImage
from ScarGenerator import ScarGenerator
from ImageDistortion import *
from HairGenerator import HairGenerator, HairLength
from WrinkleGenerator import WrinkleGenerator
from LineGenerator import LineGenerator, LineOrientation, LineLength, LineThickness


class ArgParser:
    """
    Class parsing user input and generating synthetic damage into synthetic fingerprints
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(add_help=False)
        self.args = None
        self.save_folder = None
        self.image = None
        self.directory = None
        self.name = None
        self.amount = None

    def add_args(self):
        """

        @brief: Configuration of all the available arguments
        :return: None
        """
        self.parser.add_argument("--help", "-h", action="store_true", help=argparse.SUPPRESS)
        self.parser.add_argument("--save", "-s", action="store", type=str, dest="save")
        self.parser.add_argument("--image", "-img", action="store", type=str, dest="image")
        self.parser.add_argument("--directory", "-dir", action="store", type=str, dest="directory")
        self.parser.add_argument("--name", "-n", action="store", type=str, dest="name")
        self.parser.add_argument("--amount", choices=range(0, 1000), action="store", type=int, dest="amount")

        self.parser.add_argument("--creases", action="store_true")
        self.parser.add_argument("--level", choices=[1, 2, 3], action="store", type=int, dest="level")

        self.parser.add_argument("--hair", action="store_true")
        self.parser.add_argument("--type", choices=["short", "long"], action="store", type=str, dest="type")

        self.parser.add_argument("--scar", action="store_true")
        self.parser.add_argument("--length", choices=["short", "medium", "long"], action="store", type=str,
                                 dest="length")
        self.parser.add_argument("--width", choices=["thin", "medium", "thick"], action="store", type=str, dest="width")
        self.parser.add_argument("--orientation", choices=["horizontal", "vertical", "diagonal"], action="store",
                                 type=str, dest="orientation")
        self.parser.add_argument("--outline", action="store_true")
        self.parser.add_argument("--patches", action="store_true")
        self.parser.add_argument("--distortion", action="store_true")
        self.parser.add_argument("--random", action="store_true")

        self.args = self.parser.parse_args()

    @staticmethod
    def is_valid_directory(path):
        """

        @brief: checks if path to directory is valid
        :param path: path to directory
        :return: True if path to directory is valid, False if not
        """
        return os.path.isdir(path)

    def configure_save_folder(self):
        """

        @brief: sets folder to save generated images. If given folder does not exist, folder is created
        :return: None
        """
        if self.args.save:
            if self.is_valid_directory(self.args.save):
                self.save_folder = self.args.save
            else:
                print("Path to directory to save generated images is not valid.")
                os._exit(-1)
        else:
            try:
                os.mkdir("Generated")
            except OSError as exc:
                pass

    def configure_image(self):
        """

        @brief: checks if image received by user arguments is valid and sets it as fingerprint image in which damage
                will be generated
        :return: None
        """
        if self.args.image:
            if os.path.isfile(self.args.image):
                self.image = self.args.image
            else:
                print("Path to image is not valid.")
                os._exit(-1)

    def configure_directory(self):
        """

        @brief: checks if directory with images received by user arguments is valid and sets it as directory from which
        images of fingerprints will be chosen randomly
        :return: None
        """
        if self.args.directory:
            if self.is_valid_directory(self.args.directory):
                self.directory = self.args.directory
            else:
                print("Path to directory with images is not valid.")
                os._exit(-1)

    def configure_name(self):
        """

        @brief: Sets name of generated images
        :return: None
        """
        if self.args.name:
            self.name = self.args.name

    def configure_amount(self):
        """

        @brief: Sets number of images generated. If not specified, default value is 1
        :return: None
        """
        if self.args.amount:
            self.amount = self.args.amount
        else:
            self.amount = 1

    def configure_basic_arguments(self):
        """

        @brief: Gets information from user arguments necessary for generating and saving image - image of synthetic
                fingerprint or directory containing synthetic fingerprints, name of generated picture, amount of these
                pictures and folder in which the image will be saved.
        :return: None
        """
        self.configure_save_folder()
        self.configure_image()
        self.configure_directory()
        if (self.directory is None) and (self.image is None):
            print("Please specify input fingerprint image with --image or --directory arguments.")
            os._exit(-1)
        self.configure_name()
        self.configure_amount()

    def get_damage_type(self):
        """

        @brief: Chooses which type of damage will be generated depending on user input
        :return: None
        """
        if self.args.creases:
            self.generate_creases()
        if self.args.scar:
            self.generate_scar()
        if self.args.hair:
            self.generate_hair()

    def save_image(self, image, number):
        """

        @brief: Saves image in JPG format
        :param image: Image that will be saved as array
        :param number: Number of generated images as integer
        :return: None
        """
        if self.save_folder:
            save_folder = self.save_folder
        else:
            save_folder = r'Generated'
        if self.name:
            name = self.name
        else:
            name = "damaged_fingerprint"
        image_name = name + str(number) + '.JPG'
        print(f"Saving {image_name}")
        image = cv.cvtColor(image, cv2.COLOR_GRAY2RGB)

        pil_image = Image.fromarray(image)
        pil_image.save(os.path.join(save_folder, image_name), dpi=(120, 120))

    def generate_creases(self):
        """

        @brief: Generates creases into synthetic fingerprint
        :return: None
        """
        if self.args.level:
            level = self.args.level
        else:
            level = random.choice((1, 2, 3))
        for i in range(0, self.amount):
            fingerprint = self.get_fingerprint_image()
            wrinkle_generator = WrinkleGenerator(fingerprint)
            if level == 1:
                wrinkle_generator.wrinkles_level_1()
            elif level == 2:
                wrinkle_generator.wrinkles_level_2()
            else:
                wrinkle_generator.wrinkles_level_3()
            self.save_image(wrinkle_generator.generated_image, i+1)

    def get_fingerprint_image(self):
        """

        @brief: chooses image in which damage will be generated depending on parameters
        :return: fingerprint image as array
        """
        if self.image:
            image = self.image
        else:
            image = self.choose_random_img_from_directory(self.directory)
        fingerprint = FingerprintImage()
        fingerprint.load_file_from_path(image)
        return fingerprint

    @staticmethod
    def parse_scar_length(length):
        """

        @brief: parses string to LineLength enum equivalent
        :param length: short, medium, or long as string
        :return: LineLength enum instance
        """
        if length == "long":
            return LineLength.LONG
        elif length == "short":
            return LineLength.SHORT
        elif length == "medium":
            return LineLength.MEDIUM

    @staticmethod
    def parse_scar_orientation(orientation):
        """

        @brief: parses string to LineOrientation enum equivalent
        :param orientation: horizontal, vertical, or diagonal as string
        :return: LineOrientation enum instance
        """
        if orientation == "horizontal":
            return LineOrientation.HORIZONTAL
        elif orientation == "vertical":
            return LineOrientation.VERTICAL
        elif orientation == "diagonal":
            return LineOrientation.DIAGONAL

    @staticmethod
    def parse_scar_width(width):
        """

        @brief: Parses string to LineThickness enum equivalent
        :param width: Thin, medium, or thick as string
        :return: LineThickness enum instance
        """
        if width == "thick":
            return LineThickness.THICK
        elif width == "medium":
            return LineThickness.MEDIUM
        elif width == "thin":
            return LineThickness.THIN

    def generate_scar(self):
        """

        @brief: Generates scar into synthetic fingerprint image
        :return: None
        """
        for i in range(0, self.amount):
            if self.args.length:
                scar_length = self.args.length
            else:
                scar_length = random.choice(("long", "medium", "short"))
            if self.args.width:
                scar_width = self.args.width
            else:
                scar_width = random.choice(("thin", "medium", "thick"))
            if self.args.orientation:
                scar_orientation = self.args.orientation
            else:
                scar_orientation = random.choice(("horizontal", "vertical", "diagonal"))

            fingerprint = self.get_fingerprint_image()
            scar_generator = ScarGenerator(fingerprint)
            scar_length = self.parse_scar_length(scar_length)
            scar_width = self.parse_scar_width(scar_width)
            scar_orientation = self.parse_scar_orientation(scar_orientation)

            if self.args.outline:
                scar_generator.black_outline = True
            if self.args.patches:
                scar_generator.artifacts = True
            if self.args.distortion:
                scar_generator.distortion = True

            if self.args.distortion and scar_width != LineThickness.THIN:
                print("Distortion of papillary lines is only supported in combination with thin scars")
                return -1

            scar_generator.generate_line(scar_length, scar_orientation, scar_width)
            self.save_image(scar_generator.background, i + 1)

    def generate_hair(self):
        """

        @brief: Generates hair into synthetic fingerprint image
        :return: None
        """
        for i in range(0, self.amount):
            if self.args.type:
                hair_type = self.args.type
            else:
                hair_type = random.choice(("long", "short"))
            fingerprint = self.get_fingerprint_image()
            hair_generator = HairGenerator(fingerprint)
            if hair_type == "long":
                hair_generator.generate_hair(HairLength.LONG)
            elif hair_type == "short":
                hair_generator.generate_hair(HairLength.SHORT)
            self.save_image(hair_generator.background, i + 1)

    def get_arguments(self):
        """

        @brief: Configures arguments
        :return: None
        """
        if self.args.help:
            print("PLACEHOLDER HELP")
            os._exit(0)

        self.configure_basic_arguments()
        self.get_damage_type()

    @staticmethod
    def choose_random_img_from_directory(directory):
        """

        @brief: Chooses random image from directory (if there are any valid valid images)
        :param directory: path to directory
        :return: Image as array
        """
        # get all images from file
        images = []
        path = directory
        valid_images = [".jpg", ".gif", ".png", ".tga"]
        for file in os.listdir(path):
            ext = os.path.splitext(file)[1]
            if ext.lower() not in valid_images:
                continue
            images.append((os.path.join(path, file)))

        if len(valid_images) == 0:
            print("There are no valid images in directory")
            os._exit(-1)
        random_index = random.randrange(0, (len(images) - 1))
        return images[random_index]



