#!/usr/bin/env python3
"""Convert images by removing red-green chroma in Lab space."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pillow_heif
from PIL import Image

pillow_heif.register_heif_opener()

_D65 = np.array([0.95047, 1.0, 1.08883], dtype=np.float64)
_RGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ],
    dtype=np.float64,
)
_XYZ_TO_RGB = np.array(
    [
        [3.2404542, -1.5371385, -0.4985314],
        [-0.9692660, 1.8760108, 0.0415560],
        [0.0556434, -0.2040259, 1.0572252],
    ],
    dtype=np.float64,
)
_LAB_EPSILON = 216 / 24389
_LAB_KAPPA = 24389 / 27


def _srgb_to_linear(channel: np.ndarray) -> np.ndarray:
    return np.where(
        channel <= 0.04045,
        channel / 12.92,
        ((channel + 0.055) / 1.055) ** 2.4,
    )


def _rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    linear = _srgb_to_linear(rgb / 255.0)
    xyz = linear @ _RGB_TO_XYZ.T
    xyz = xyz / _D65

    f = np.where(xyz > _LAB_EPSILON, np.cbrt(xyz), (_LAB_KAPPA * xyz + 16) / 116)

    lab = np.empty_like(rgb)
    lab[..., 0] = 116 * f[..., 1] - 16
    lab[..., 1] = 500 * (f[..., 0] - f[..., 1])
    lab[..., 2] = 200 * (f[..., 1] - f[..., 2])
    return lab


def _lab_f_to_xyz(f: np.ndarray) -> np.ndarray:
    f3 = f**3
    return np.where(f3 > _LAB_EPSILON, f3, (116 * f - 16) / _LAB_KAPPA)


def _lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200

    xyz = np.stack(
        (_lab_f_to_xyz(fx), _lab_f_to_xyz(fy), _lab_f_to_xyz(fz)),
        axis=-1,
    )
    xyz *= _D65

    linear = np.maximum(xyz @ _XYZ_TO_RGB.T, 0.0)
    rgb = np.where(
        linear <= 0.0031308,
        linear * 12.92,
        1.055 * np.power(linear, 1 / 2.4) - 0.055,
    )
    return np.clip(np.rint(rgb * 255), 0, 255).astype(np.uint8)


def _drop_red_green_chroma(rgb: np.ndarray) -> np.ndarray:
    """Convert to Lab, zero the a* (red-green) axis, and convert back to RGB."""
    lab = _rgb_to_lab(rgb.astype(np.float64))
    lab[..., 1] = 0.0
    return _lab_to_rgb(lab)


def dichromatic(image: Image.Image) -> Image.Image:
    """Remove red-green chroma while keeping lightness and blue-yellow chroma."""
    if image.mode == "RGBA":
        rgba = np.array(image, dtype=np.uint8)
        rgb = _drop_red_green_chroma(rgba[..., :3])
        return Image.fromarray(np.dstack((rgb, rgba[..., 3])), mode="RGBA")

    rgb = np.array(image.convert("RGB"), dtype=np.uint8)
    return Image.fromarray(_drop_red_green_chroma(rgb), mode="RGB")


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_dichromatic{input_path.suffix}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an image by removing red-green chroma in Lab space.",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input image path (JPEG, PNG, HEIF, HEIC, etc.)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output image path (default: <name>_dichromatic.<ext>)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = args.input
    output_path = args.output or default_output_path(input_path)

    if not input_path.is_file():
        print(f"error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        with Image.open(input_path) as image:
            result = dichromatic(image)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            result.save(output_path)
    except OSError as exc:
        print(f"error: failed to process image: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
