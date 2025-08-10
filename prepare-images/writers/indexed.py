import json
from pathlib import Path

import numpy as np
import numpy.typing as npt
from PIL import Image


def index_image(
    img: Image, color_count: int
) -> tuple[dict[str, list[int]], npt.NDArray[np.uint8]]:
    img = img.convert("RGB")
    img_quantized = img.quantize(color_count, method=Image.MAXCOVERAGE)

    # use remap_palette to reorder the palette and make it sorted
    palette_colors = np.array(img_quantized.getpalette()).reshape(-1, 3)
    img_quantized = img_quantized.remap_palette(
        np.argsort(
            0.299 * palette_colors[:, 0]
            + 0.587 * palette_colors[:, 1]
            + 0.114 * palette_colors[:, 2]
        )
    )

    palette = img_quantized.getpalette()
    lut = {
        "r": palette[0::3],
        "g": palette[1::3],
        "b": palette[2::3],
    }
    color_index = np.array(img_quantized)

    return lut, color_index


class IndexedImageWriter:

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.n = 0
        self.index = 0
        self.data = None
        self.luts = []

    def add_image(self, image: Image):
        lut, color_index = index_image(image, 256)

        if self.data is None:
            self.data = np.zeros((*color_index.shape, 4), dtype=np.uint8)
            self.index = 0

        self.data[:, :, self.index] = color_index
        self.luts.append(lut)
        self.index += 1

        if self.index == 4:
            self._write_data()

    def _write_data(self):
        img = Image.fromarray(self.data, mode="RGBA")
        img.save(self.output_dir / f"indexed_{self.n:04}.png")
        self.n += 1

        # prepare for next set of images
        self.data = None

    def _write_luts(self):
        with open(self.output_dir / "color_lut.json", "w") as f:
            json.dump(self.luts, f, indent=2)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.data is not None:
            self._write_data()

        self._write_luts()


def prepare_indexed_image_dir(
    input_dir: Path,
    output_dir: Path,
):
    if not output_dir.exists():
        output_dir.mkdir()

    img_files = sorted(input_dir.glob("*.png"))
    total_file_count = len(img_files)

    with IndexedImageWriter(output_dir) as iiw:
        for i, img_file in enumerate(img_files):
            print(f"{i+1}/{total_file_count}: copying and indexing image {img_file}")
            iiw.add_image(Image.open(img_file))
