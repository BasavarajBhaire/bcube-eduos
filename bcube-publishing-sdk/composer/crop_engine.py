from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from PIL import Image


class CropError(ValueError):
    pass


@dataclass(frozen=True)
class CropSpec:
    x: float
    y: float
    w: float
    h: float
    padding: float = 0.0

    @classmethod
    def from_mapping(cls, value: Mapping[str, float]) -> "CropSpec":
        spec = cls(
            x=float(value["x"]),
            y=float(value["y"]),
            w=float(value["w"]),
            h=float(value["h"]),
            padding=float(value.get("padding", 0.0)),
        )
        spec.validate()
        return spec

    def validate(self) -> None:
        if not (0 <= self.x <= 1 and 0 <= self.y <= 1):
            raise CropError("Crop origin must be normalised to 0..1")
        if not (0 < self.w <= 1 and 0 < self.h <= 1):
            raise CropError("Crop dimensions must be normalised and greater than zero")
        if self.x + self.w > 1.000001 or self.y + self.h > 1.000001:
            raise CropError("Crop extends outside source image")
        if not 0 <= self.padding <= 0.1:
            raise CropError("Crop padding must be between 0 and 0.1")


def crop_from_manifest(source: Image.Image, value: Mapping[str, float]) -> Image.Image:
    spec = CropSpec.from_mapping(value)
    width, height = source.size
    px = round(spec.padding * width)
    py = round(spec.padding * height)
    left = max(0, round(spec.x * width) - px)
    top = max(0, round(spec.y * height) - py)
    right = min(width, round((spec.x + spec.w) * width) + px)
    bottom = min(height, round((spec.y + spec.h) * height) + py)
    if right <= left or bottom <= top:
        raise CropError("Crop resolves to an empty image")
    return source.crop((left, top, right, bottom)).convert("RGBA")


def contain(image: Image.Image, size: tuple[int, int], background=(255, 255, 255, 0)) -> Image.Image:
    target_w, target_h = size
    if target_w <= 0 or target_h <= 0:
        raise CropError("Target size must be positive")
    source = image.copy()
    source.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (target_w, target_h), background)
    x = (target_w - source.width) // 2
    y = (target_h - source.height) // 2
    canvas.alpha_composite(source, (x, y))
    return canvas
