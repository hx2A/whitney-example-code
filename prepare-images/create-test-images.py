"""
Create test images with py5, then prepare them for the indexed and grayscale players.
"""

from pathlib import Path

import py5
from writers.grayscale import prepare_grayscale_image_dir
from writers.indexed import prepare_indexed_image_dir

SOURCE_DIR = Path("src-images")
COLOR_TEST_SOURCE_DIR = SOURCE_DIR / "color"
GRAYSCALE_TEST_SOURCE_DIR = SOURCE_DIR / "grayscale"

INDEXED_TEST_PROCESSED_DIR = Path(
    "processing-sketches/test_indexed_player/data/indexed-image-data"
)
GRAYSCALE_TEST_PROCESSED_DIR = Path(
    "processing-sketches/test_grayscale_player/data/grayscale-image-data"
)


TEST_IMAGE_COUNT = 25
SAMPLE_COUNT = 20

# Functions for rendering test images using py5


@py5.render_sequence(500, 500, limit=TEST_IMAGE_COUNT)
def color_test_images(s: py5.Sketch):
    s.color_mode(py5.HSB, 360, 100, 100)
    s.rect_mode(py5.CENTER)
    s.text_size(300)
    s.text_align(py5.CENTER, py5.CENTER)

    s.background(0, 0, 100)

    s.translate(s.width / 2, s.height / 2)

    s.fill(s.frame_count / TEST_IMAGE_COUNT * 360, 80, 80)
    s.text(f"{s.frame_count}", 0, 0)

    for i in range(SAMPLE_COUNT):
        with s.push():
            val = (i + s.frame_count) % SAMPLE_COUNT / SAMPLE_COUNT * 360
            s.fill(val, 80, 80)
            s.rotate(py5.TWO_PI / SAMPLE_COUNT * i)
            s.translate(0, 200)
            s.rect(0, 0, 40, 40)


@py5.render_sequence(500, 500, limit=TEST_IMAGE_COUNT)
def grayscale_test_images(s: py5.Sketch):
    s.rect_mode(py5.CENTER)
    s.text_size(300)
    s.text_align(py5.CENTER, py5.CENTER)

    s.background(255)

    s.translate(s.width / 2, s.height / 2)

    s.fill(s.frame_count / TEST_IMAGE_COUNT * 255)
    s.text(f"{s.frame_count}", 0, 0)

    for i in range(SAMPLE_COUNT):
        with s.push():
            val = (i + s.frame_count) % SAMPLE_COUNT / SAMPLE_COUNT * 255
            s.fill(val)
            s.rotate(py5.TWO_PI / SAMPLE_COUNT * i)
            s.translate(0, 200)
            s.rect(0, 0, 40, 40)


# Create the test images

COLOR_TEST_SOURCE_DIR.mkdir(exist_ok=True, parents=True)
for i, frame in enumerate(color_test_images()):
    frame.save(COLOR_TEST_SOURCE_DIR / f"color-test-{i:04d}.png")


GRAYSCALE_TEST_SOURCE_DIR.mkdir(exist_ok=True, parents=True)
for i, frame in enumerate(grayscale_test_images()):
    frame.save(GRAYSCALE_TEST_SOURCE_DIR / f"grayscale-test-{i:04d}.png")


# Prepare the indexed and grayscale image directories for the Processing sketches

GRAYSCALE_TEST_PROCESSED_DIR.mkdir(exist_ok=True, parents=True)
prepare_grayscale_image_dir(
    GRAYSCALE_TEST_SOURCE_DIR,
    GRAYSCALE_TEST_PROCESSED_DIR,
)

INDEXED_TEST_PROCESSED_DIR.mkdir(exist_ok=True, parents=True)
prepare_indexed_image_dir(
    COLOR_TEST_SOURCE_DIR,
    INDEXED_TEST_PROCESSED_DIR,
)
