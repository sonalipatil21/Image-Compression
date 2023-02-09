# Image-Compression
## Objective
Given a set of example images, compress them as much as possible without losing any perceptible information – upon decompression they should appear identical to the original images.

## Description
Images are essentially stored as a series of points of color, where each point is represented as a combination of red, green and blue (rgb). Each component of the rgb value ranges between 0-255, so for example: (100, 0, 200) would represent a shade of purple. Using a fixed length encoding, each component of the rgb value requires 8 bits to encode (28 = 256) meaning that the entire rgb value requires 24 bits to encode. Using a compression algorithm like Huffman encoding the number of bits needed for more common values can be reduced  thereby reducing the total number of bits needed to encode an image.

I used the Pillow library of Python to read in image files and extract the rgb values of individual points. I then computed how many bits are required for a fixed length encoding and then applied a compression algorithm to create a smaller encoding which could be saved as a sequence of bits into a text file. The code then can prompt the user for the filename of a text file containing a compressed sequence of bits and then decompress that file into the original image.

The code is also able to compute the following statistics each time the compression code is called on a file:
- Runtime in milliseconds of the compression process, including any time needed to create the data structures used to help with the compression process.
- Number of bits needed by your algorithm to encode the contents of the file.
- Number of bits needed by a fixed length encoding to encode the contents of the file.
- The compression ratio achieved.
