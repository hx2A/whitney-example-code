from pathlib import Path

import numpy as np
from PIL import Image


class GrayscaleImageWriter:

    def __init__(self, output_dir):
        self.img_output_dir = Path(output_dir)
        self.img_output_dir.mkdir(parents=True, exist_ok=True)

        self.n = 0
        self.index = 0
        self.count = 0
        self.data = None

    def add_image(self, image: Image):
        image_array = np.asarray(image.convert("L").getchannel("L"), dtype=np.uint8)

        if self.data is None:
            self.data = np.zeros((*image_array.shape, 4), dtype=np.uint8)
            self.index = 0

        self.data[..., self.index] = image_array
        self.index += 1

        if self.index == 4:
            self._write_data()

    def _write_data(self):
        img = Image.fromarray(self.data, mode="RGBA")
        img.save(self.img_output_dir / f"grayscale_{self.n:04}.png")

        self.n += 1
        self.count += self.index
        self.data = None

    def _write_count(self):
        with open(self.img_output_dir / "data.txt", "w") as f:
            f.write(str(self.count))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.data is not None:
            self._write_data()

        self._write_count()


def prepare_grayscale_image_dir(
    input_dir: Path,
    output_dir: Path,
):
    if not output_dir.exists():
        output_dir.mkdir()

    img_files = sorted(input_dir.glob("*.png"))
    total_file_count = len(img_files)

    with GrayscaleImageWriter(output_dir) as giw:
        for i, img_file in enumerate(img_files):
            print(f"{i+1}/{total_file_count}: copying grayscale image {img_file}")
            giw.add_image(Image.open(img_file))
