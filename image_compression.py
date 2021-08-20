#!/usr/bin/env python3

# Python ImageCompression processor
#
# Example usage:
#   ./ImageCompression.py --name=ocean.bmp

import argparse
import time
import sys
import os
from huffman import Decompressor
from huffman import Compressor


def main():
    # Setup configuration
    parser = argparse.ArgumentParser(description='ImageCompression')
    parser.add_argument('--name', action='store', dest='iname',
                        required=True, help='Image file Name')

    args = parser.parse_args()
    iname = args.iname

    # Read image
    #try:
    #    img = Image.open(iname)
    #except img.error as msg:
    #    print("Error: could not open image file")
    #    print("Description: " + str(msg))
    #    sys.exit()

    #img.show()

    filename, ext = os.path.splitext(iname)
    output_path = filename + ".bin"

    start_time = time.time()
    print('compressing', iname)
    Compressor.compress(iname)
    elapsed_time = time.time() - start_time
    print('Compression time         : {:.2f} ms'.format(elapsed_time * 1000))

    start_time = time.time()
    print('decompressing', iname)
    decompressor = Decompressor(iname + '.huf')
    decompressor.decompress()
    elapsed_time = time.time() - start_time
    print('Decompression time       : {:.2f} ms'.format(elapsed_time * 1000))

if __name__ == "__main__":
    main()