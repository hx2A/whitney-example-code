# Whitney Example Code

This repo shares example Processing code demonstrating a few of the technical aspects of The River is a Circle (2025) and The Earth Eaters (2025), both currently being shown at The Whitney. Both works were made in collaboration with [Marina Zurkow](https://o-matic.com/).

These two works use a custom software framework built on top of the open source projects [Processing](https://processing.org/) and [py5](https://py5coding.org/). The custom software is not open source but we decided to open source a few pieces of it to share our solutions to some of the unique technical challenges we faced while building these works.

## Image Compression and Decompression

The River is a Circle (2025) and The Earth Eaters (2025) are both image-heavy works with well over 100K images between the two of them. Some of the image sequences are quite large and would consume several GBs of memory each. This causes a serious problem because the computer's RAM, VRAM, and the Java Virtual Machine's heap size are all limited. It is critical to stay well within memory limits to avoid garbage collection pauses. Memory issues and garbage collection pauses cause visual stutters or brief freezes in the work. Much effort has gone into making sure visual stutters never happen.

The River is a Circle (2025) runs on a small Intel NUC computer with 32 GB of RAM. The Earth Eaters (2025) runs on a larger NUC computer with 64 GB of RAM and a NVidia 4060 GPU with only 8 GB of VRAM.

We came up with clever ideas for how to get the software to fit within these memory constraints. What we came up with are bespoke image compression algorithms that are either lossless or visually indistinguishable from the original images. These are not general purpose image compression algorithms, but they are algorithms that are precisely effective for our needs.

The main idea is to pre-process the source images to compress multiple source images into a single image that can later be used to display all of the source images. We use Python code to generate these compressed images that will need a custom shader to display correctly. This is effectively an on-GPU image decompression algorithm. If we compress four images into one, we can reduce memory usage by 75%.

Necessity is the mother of invention.

These algorithms meet our needs but they might not be useful for you. Most importantly, all of this is a needless complication if you are not facing memory constraints from an image-heavy Processing sketch. And the compression algorithms may be far from lossless for your situation. Please look at this as an example of creative problem solving and also consider the possibility of using an image's RGBA color channels as four data channels that are interpreted by a shader. If you understand the concepts, you may be able to design a different algorithm that works well for you.

### Grayscale Images

Consider a grayscale image. The red, green, and blue channels are identical. We only need one of them. Storing all of them in memory is a waste of precious memory.

The [prepare-images/writers/grayscale.py](prepare-images/writers/grayscale.py) code can compress a source directory of grayscale images into a set of compressed images that each contain up to four of the originals. The code also creates a small data file that contains the number of original images. This is necessary because the number of original images may not be a multiple of four so the last compressed image can have unused channels.

A Processing Sketch can use a shader to display an image using only one of an image's four color channels.

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

You'll observe the shaders are quite simple. That's actually the point. The interesting part is the Python code. The goal of all of this is to use Python to reorient the image data so that a simple, fast, and efficient shader can render the images while using as little memory as possible. Arcane shader code isn't helpful here.

### Images with Alpha Channels

These algorithms do not support images with transparent pixels. It can be expanded to support transparency, and in fact does so, successfully, in both The River is a Circle and The Earth Eaters. The Python code for that is quite a bit more complicated. If there's sufficient interest I will update this repository to add an explanation of that as well.

## State Management

The River is a Circle (2025) and The Earth Eaters (2025) both involve complex interactions between different parts of the code. In particular, some events in The River is a Circle (2025) are triggered by rules that could combine the current weather, tides, time of day, or season. Internally there is a State Manager that keeps track of state and evaluates state expressions. All components in the software can connect to the same State Manager to coordinate activities. All components in the software can set state values that are later consumed by other software components. This coordination vastly simplifies the code and makes it easier to maintain.

A specific example of how this is used in The River is a Circle (2025) is with the weather. One component in the work is responsible for processing weather data. It sets weather states with the State Manager to communicate if it is raining or snowing. Other components in the work will check in with the State Manager to evaluate relevant boolean expressions and may take action based on the results of a boolean expression. For example, a certain actor may only appear on the screen during the summer at nighttime when it is not raining.

### States

The State Manager maintains the true and false values of named states. You define the state by first setting the state to `true` or `false`. Any state that is unknown the the State Manager is assumed to be false.

```java
StateManager stateManager = StateManager.getInstance();

stateManager.setState("hot", true);
stateManager.setState("cold", false);
stateManager.setState("raining", false);
stateManager.setState("snowing", false);
```

A valid state name can contain any alphanumeric character or underscores.

### Boolean Expressions

Boolean expressions are statements that the State Manager will evaluate to true or false. The expressions use state names and the boolean operators `AND`, `OR`, `XOR`, and `NOT`. You may also use parentheses.

Below are some possible boolean expressions and what they evaluate to, given the above statements.

| Expression                       | Value |
| -------------------------------- | ----- |
| hot AND raining                  | false |
| hot OR cold                      | true  |
| hot AND (raining OR snowing)     | false |
| NOT hot AND (raining OR snowing) | false |
| hot XOR raining                  | true  |
| cold OR sleet                    | false |

### Builtin Time States

Much of the value of the State Manager comes from the builtin time states. The builtin time states are:

* `daytime`: true between sunrise and sunset
* `nighttime`: true between sunset and the next day's sunrise
* `january`, `february`, `march`, ..., `december`: true if the current date falls within the given month
* `august11`, `august12`, `august13`, etc: true when the current date is the given month and day
* `monday`, `tuesday`, `wednesday`, ..., `sunday`: true when the current date falls on the given day of the week
* `summer`, `fall`, `winter`, `spring`: true when the current season falls in the given season.
* `summer_solstice`, `winter_solstice`, `vernal_equinox`, `autumnal_equinox`: true when the current date is on a solstice or equinox
* `hour0`, ..., `hour22`, `hour23`: true when the current hour of the day is equal to the given hour
* `hour13_22`: true when the current hour of the day is between the two given hours

These can be combined with each other to form complex boolean expressions.

### Test Sketch

Open and run the test state manager Processing Sketch in [processing-sketches](processing-sketches) using the Processing Development Environment (PDE). Look at the output in the console for the results of the boolean expressions. Experiment by adding new state expressions and see if you can figure out if they are true or false.

## AIS Data

The River is a Circle (2025) monitors marine traffic in the immediate vicinity of The Whitney museum. When ships traveling along the Hudson River are viewable from The Whitney's terrace, the work will detect their presence and respond by displaying related animations on the screen.

### Data Source

The work uses data from the free real-time data source [aisstream.io/](https://aisstream.io/) to obtain [AIS data](https://en.wikipedia.org/wiki/Automatic_identification_system). To use this data and the example code, you'll need to sign up for an account to get an API key.

### Data Resources

Here are resources that will be helpful to you as you work with AIS data and write your code.

* [aisstream.io documentation](https://aisstream.io/documentation)
* [US Coast Guard AIS Data documentation](https://www.navcen.uscg.gov/ais-messages)
* [Vessel Finder Map](https://www.vesselfinder.com/)

### Run Example Code

The example code is written in Python. You'll need to install the Python libraries websockets, py5, and Pandas. Add your API key to the file `ais-data/main.py`.

```bash
python ais-data/main.py
```

### Understanding the Code

#### stream.py

Subscribes to messages
Uses websockets, missed messages are lost
Reports static and position data

#### state.py

Interprets static and position data
Data classes, use current_position() and future_position() methods for projected positions
