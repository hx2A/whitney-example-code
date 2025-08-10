# Whitney Example Code

This repo shares example Processing code demonstrating a few of the technical aspects of the The River is a Circle (2025) and The Earth Eaters (2025), both currently being shown at The Whitney. Both works were made in collaboration with [Marina Zurkow](https://o-matic.com/).

These two works use a custom software framework built on top of the open source projects [Processing](https://processing.org/) and [py5](https://py5coding.org/). The custom software is not open source but we decided to open source a few pieces of it to share our solutions to some of the unique technical challenges we faced while building these works.

## Image Compression and Decompression

The River is a Circle (2025) and The Earth Eaters (2025) are both image-heavy works with well over 100K images between the two of them. Some of the image sequences are quite large and would consume several GBs of memory each. This causes a serious problem because the computer's RAM, VRAM, and the Java Virtual Machine's heap size are all limited. It is critical to stay well within memory limits to avoid garbage collection pauses. Memory issues and garbage collection pauses cause visual stutters or brief freezes in the work. Much effort has gone into making sure visual stutters never happen.

The River is a Circle (2025) runs on a small Intel NUC computer with 32 GB of RAM. The Earth Eaters (2025) runs on a larger NUC computer with 64 GB of RAM and a NVidia 4060 GPU with only 8 GB of VRAM.

We came up with clever ideas for how to get the software to fit within these memory constraints. What we came up with are bespoke image compression algorithms that are either lossless or visually indistinguishable from the original images. These are not general purpose image compression algorithms, but they are algorithms that very effectively for our needs.

The main idea is to pre-process the source images to compress multiple source images into a single image that can later be used to display all of the source images. We use Python code to generate these compressed images that will need a custom shader to display correctly. This is effectively an on-GPU image decompression algorithm. If we compress four images into one, we can reduce memory usage by 75%.

Necessity is the mother of invention.

These algorithms met our needs but they might not be useful for you. Most importantly, all of this is a needless complication if you are not facing memory constraints from an image-heavy Processing sketch. And the compression algorithms may be far from lossless for your situation. Please look at this as an example of creative problem solving and also the possibility of using an image's RGBA color channels as four data channels that are interpreted by a shader. If you understand the concepts, you may be able to design a different algorithm that works well for you.

### Grayscale Images

Consider a grayscale image. The red, green, and blue channels are identical. We only need one of them. Storing all of them in memory is a waste of precious memory.

The [prepare-images/writers/grayscale.py](prepare-images/writers/grayscale.py) code can compress a source directory of grayscale images into a set of compressed images that each contain up to four of the originals. The code also creates a small data file that contains the number of original images. This is necessary because the number of original images may not be a multiple of four so the last compressed image can have unused channels.

A Processing Sketch can use a shader to display an image using only one an image's four color channels.

### Indexed Images

An RGB image can contain up to 16777216 unique colors. However, most images don't use that many. Marina's drawings typically use a smaller color palette. We can use that to our advantage by creating images that use a smaller color palette with color quantization.

The [prepare-images/writers/indexed.py](prepare-images/writers/indexed.py) code can compress a source directory of
images into a set of compressed images that contain 4 sets of color indices that map to a color palette. The color palette is stored in a separate JSON file.

A Processing Sketch can use a shader to display an image by mapping the indices stored in one of an image's four color channels to the colors stored in the color palette.

### Image Preparation

This repo already contains test images in the [src-images](src-images) directory, but if you want to create them yourself, use this Python script:

```bash
python prepare-images/create-test-images.py
```

You'll need to have [py5](https://py5coding.org/) installed.

The compressed images are written to the appropriate `data` directories in the [processing-sketches](processing-sketches) directory.

### Test Sketches

Open and run the Processing Sketches in [processing-sketches](processing-sketches) using the Processing Development Environment (PDE). For both you'll see a player class that manages the compressed image data and the shader. Detailed information about how the players work is contained in the source code.

## State Management

(insert State Management description)
