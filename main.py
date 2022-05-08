#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Vanessa Jóriová
# Date        : 8.5.2022
# Version     : 1.0

from ArgParser import ArgParser


def main():
    """

    @brief: Main function of line damage generator
    :return: None
    """
    arg_parser = ArgParser()
    arg_parser.add_args()
    arg_parser.get_arguments()


if __name__ == '__main__':
    main()

