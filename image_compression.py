#!/usr/bin/env python3
# Name: Sonali Patil | Class: COMP 157 |  Project: 3
# Python ImageCompression or decompression processor
#
# Example usage
#
# Editing Run configurations:
# 1. Edit Run configurations to have parameters type and name
# 2. Inside parameters put
# For compression use type c:
#   -type=c --name=ocean.bmp (or --name=compress_images/ocean.bmp depending on file location)
# For compression use type d:
#   --type=c --name=ocean.txt (or --name=compress_images/ocean.txt depending on file location)
#
# Editing terminal:
# For compression use type c:
#   ./ImageCompression.py --type=c --name=ocean.bmp
# For compression use type d:
#   ./ImageCompression.py --type=c --name=ocean.txt

import argparse
import time
import sys
import os
from Huffman import Huffman


def main():

    # Setup configuration
    parser = argparse.ArgumentParser(description='ImageCompression')
    parser.add_argument('--type', action='store', dest='itype',
                        required=True, help='Compress: C or Decompress: D')
    parser.add_argument('--name', action='store', dest='iname',
                        required=True, help='Image file Name')

    args = parser.parse_args()
    type = str(args.itype).lower()
    in_file_name = args.iname
    if not os.path.exists(in_file_name):
        print('File {} doesn\'t exist'.format(in_file_name))
        sys.exit(-1)

    if type != 'c' and type != 'd':
        print('Invalid compression or decompression option type')
        sys.exit(-2)

    filename, ext = os.path.splitext(in_file_name)
    huffman = Huffman(None)

    if type == 'c':
        start_time = time.time()

        huffman.compress_image(in_file_name, filename + ".txt")

        elapsed_time = time.time() - start_time
        print('Compression run time (COMBINED TIMES: : Compression + Read / Compression + Write): {:12.2f} ms'.format(elapsed_time * 1000))
    else:
        start_time = time.time()

        huffman.decompress_image(in_file_name, filename + "_out.bmp")

        elapsed_time = time.time() - start_time
        print('Decompression Run time: {:12.2f} ms'.format(elapsed_time * 1000))


if __name__ == "__main__":
    main()
