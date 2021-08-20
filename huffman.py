#!/usr/bin/env python3
import time

from PIL import Image
from PIL import ImageChops

from collections import Counter
from itertools import chain

import BitUtils
from BitUtils import OutBitStream
from BitUtils import InBitStream


class Huffman(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.bit_stream = None

    def raw_size(self, width, height):
        header_size = 2 * 16  # height and width as 16 bit values
        pixels_size = 3 * 8 * width * height  # 3 channels, 8 bits per channel
        return (header_size + pixels_size) / 8

    # Compression
    def count_symbols(self, image):
        pixels = image.getdata()
        values = chain.from_iterable(pixels)
        counts = Counter(values).items()
        return sorted(counts, key=lambda x: x[::-1])

    def build_tree(self, counts):
        nodes = [entry[::-1] for entry in counts]  # Reverse each (symbol,count) tuple
        while len(nodes) > 1:
            least_two = tuple(nodes[0:2])  # get the 2 to combine
            the_rest = nodes[2:]  # all the others
            comb_freq = least_two[0][0] + least_two[1][0]  # the branch points freq
            nodes = the_rest + [(comb_freq, least_two)]  # add branch point to the end
            nodes.sort(key=lambda t: t[0])
        return nodes[0]  # Return the single tree inside the list

    def trim_tree(self, tree):
        p = tree[1]  # Ignore freq count in [0]
        if type(p) is tuple:  # Node, trim left then right and recombine
            return self.trim_tree(p[0]), self.trim_tree(p[1])
        return p  # Leaf, just return it

    def assign_codes_impl(self, codes, node, pat):
        if type(node) == tuple:
            self.assign_codes_impl(codes, node[0], pat + [0])  # Branch point. Do the left branch
            self.assign_codes_impl(codes, node[1], pat + [1])  # then do the right branch.
        else:
            codes[node] = pat  # A leaf. set its code

    def assign_codes(self, tree):
        codes = {}
        self.assign_codes_impl(codes, tree, [])
        return codes

    def encode_header(self, image):
        height_bits = BitUtils.pad_bits(BitUtils.to_binary_list(image.height), 16)
        self.bit_stream.write_bits(height_bits)
        width_bits = BitUtils.pad_bits(BitUtils.to_binary_list(image.width), 16)
        self.bit_stream.write_bits(width_bits)

    def encode_tree(self, tree):
        if type(tree) == tuple:  # Note - write 0 and encode children
            self.bit_stream.write_bit(0)
            self.encode_tree(tree[0])
            self.encode_tree(tree[1])
        else:  # Leaf - write 1, followed by 8 bit symbol
            self.bit_stream.write_bit(1)
            symbol_bits = BitUtils.pad_bits(BitUtils.to_binary_list(tree), 8)
            self.bit_stream.write_bits(symbol_bits)

    def encode_pixels(self, image, codes):
        for pixel in image.getdata():
            for value in pixel:
                self.bit_stream.write_bits(codes[value])

    # Compress image
    def compress_image(self, in_file_name, out_file_name):
        print('Compressing "%s" => "%s"' % (in_file_name, out_file_name))
        image = Image.open(in_file_name)

        size_raw = self.raw_size(image.height, image.width)
        print('RAW image size: %d bytes' % size_raw)

        counts = self.count_symbols(image)
        tree = self.build_tree(counts)
        trimmed_tree = self.trim_tree(tree)
        codes = self.assign_codes(trimmed_tree)

        self.bit_stream = OutBitStream(out_file_name)
        self.encode_header(image)
        self.bit_stream.flush()  # make sure next chunk is byte-aligned
        self.encode_tree(trimmed_tree)
        self.bit_stream.flush()  # make sure next chunk is byte-aligned

        start_time = time.time()
        self.encode_pixels(image, codes)
        self.bit_stream.close()

        size_real = self.bit_stream.bytes_written

        print('Compression ratio: %0.2f%%' % (float(size_real * 100) / size_raw))

    # Decompression
    def decode_header(self):
        height = BitUtils.from_binary_list(self.bit_stream.read_bits(16))
        width = BitUtils.from_binary_list(self.bit_stream.read_bits(16))
        return height, width

    def decode_tree(self):
        flag = self.bit_stream.read_bits(1)[0]
        if flag == 1:  # Leaf, read and return symbol
            return BitUtils.from_binary_list(self.bit_stream.read_bits(8))
        left = self.decode_tree()
        right = self.decode_tree()
        return left, right

    def decode_value(self, tree):
        bit = self.bit_stream.read_bits(1)[0]
        node = tree[bit]
        if type(node) == tuple:
            return self.decode_value(node)
        return node

    def decode_pixels(self, height, width, tree):
        pixels = bytearray()
        for i in range(height * width * 3):
            pixels.append(self.decode_value(tree))
        return Image.frombytes('RGB', (width, height), bytes(pixels))

    # Decompress image
    def decompress_image(self, in_file_name, out_file_name):
        print('Decompressing "%s" => "%s"' % (in_file_name, out_file_name))

        self.bit_stream = InBitStream(in_file_name)
        height, width = self.decode_header()
        self.bit_stream.flush()  # make sure the next chunk is byte-aligned

        trimmed_tree = self.decode_tree()
        self.bit_stream.flush()  # make sure next chunk is byte-aligned
        image = self.decode_pixels(height, width, trimmed_tree)
        self.bit_stream.close()

        image.save(out_file_name)
