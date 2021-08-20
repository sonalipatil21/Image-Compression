#!/usr/bin/env python3
# Huffman binary compression and decompression
#
# Example usage:
# Compressor.Compressor(file name)
# decompressor = Decompressor(compressed file name)
# decompressor.decompress()

import sys
from math import ceil

LEFT = '1'
RIGHT = '0'


class Leaf:
    def __init__(self, data, value):
        self.data = data
        self.value = value
        self.parent = None
        self.code = ''

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()

    def update_code(self, update):
        self.code = update + self.code

class Node:
    def __init__(self, left, right, value):
        self.value = value
        self.left = left
        self.right = right
        self.code = ''
        self.left.update_code(LEFT)
        self.right.update_code(RIGHT)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()

    def update_code(self, update):
        self.code = update + self.code
        self.left.update_code(update)
        self.right.update_code(update)


def build_tree(byte_freq):
    tree = [Leaf(bf, bf[1]) for bf in byte_freq]
    leaves = []

    while len(tree) > 1:
        left, right = tree[:2]
        if type(left) is Leaf:
            leaves.append(left)
        if type(right) is Leaf:
            leaves.append(right)
        tree = tree[2:]
        node = Node(left, right, left.value + right.value)
        tree.append(node)
        tree = sorted(tree, key=lambda node: node.value)

    return leaves, tree[0]


class Compressor:
    @staticmethod
    def get_frequencies(input_bytes):
        byte_set = set(input_bytes)

        byte_freq_dict = {b: 0 for b in byte_set}

        for b in input_bytes:
            byte_freq_dict[b] = byte_freq_dict[b] + 1

        return sorted([item for item in byte_freq_dict.items()], key=lambda item:item[1])

    def compress(filename):
        input_bytes = []
        with open(filename, 'rb') as bin_file:
            input_bytes = bin_file.read()

        print('Input size (in bits)    :', len(input_bytes) * 8)
        byte_freq = Compressor.get_frequencies(input_bytes)
        leaves, _ = build_tree(byte_freq)
        symbol_map = {leaf.data[0]: leaf.code for leaf in leaves}

        output_bits = '1'
        for b in input_bytes:
            output_bits = output_bits + symbol_map[b]

        byte_count = (len(output_bits)+7) // 8
        output_int = int(output_bits, 2)
        output_bytes = output_int.to_bytes(byte_count, sys.byteorder)
        max_count_bytes = ceil(leaves[-1].data[1].bit_length()/8)

        header_bytes = len(leaves).to_bytes(2, sys.byteorder)
        header_bytes += max_count_bytes.to_bytes(8, sys.byteorder)

        for leaf in leaves:
            header_bytes += (leaf.data[0].to_bytes(1, sys.byteorder))
            header_bytes += leaf.data[1].to_bytes(max_count_bytes, sys.byteorder)

        with open(filename + '.huf', 'wb') as out_file:
            out_file.write(header_bytes)
            out_file.write(output_bytes)

        print('Compressed size (in bits):', (len(output_bytes) + len(header_bytes)) * 8)
        print('Compression Ratio        : {:.2f} %'.format(((len(output_bytes) + len(header_bytes)) / len(input_bytes)) * 100))


class Decompressor:
    def __init__(self, filename):
        self.filename = filename
        self.out_filename = '.'.join(filename.split('.')[:-1])

    # Read decompressed file
    def read_file(self):
        byte_freq = []
        input_bytes = None
        with open(self.filename, 'rb') as input_file:
            leaves_count = int.from_bytes(input_file.read(2), sys.byteorder)
            max_count_bytes = int.from_bytes(input_file.read(8), sys.byteorder)
            while leaves_count > 0:
                b = input_file.read(1)
                c = int.from_bytes(input_file.read(max_count_bytes), sys.byteorder)
                byte_freq.append((b, c))
                leaves_count -= 1
            input_bytes = input_file.read()
        return input_bytes, byte_freq

    def decompress(self):
        input_bytes, byte_freq = self.read_file()
        _, tree = build_tree(byte_freq)
        input_bits = bin(int.from_bytes(input_bytes, sys.byteorder))[3:]
        output_bytes = b''
        cur_node = tree
        for bit in input_bits:
            if bit == LEFT:
                cur_node = cur_node.left
            else:
                cur_node = cur_node.right

            if type(cur_node) is Leaf:
                output_bytes += cur_node.data[0]
                cur_node = tree

        with open(self.out_filename, 'wb') as output_file:
            output_file.write(output_bytes)
