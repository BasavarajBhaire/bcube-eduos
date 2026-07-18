from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class PageObjectError(ValueError):
    """Raised when a Page Object Model violates deterministic layout rules."""


@dataclass(frozen=True)
class Geometry:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_region(cls, region: dict[str, Any]) -> "Geometry":
        values = (region.get("x"), region.get("y"), region.get("w"), region.get("h"))
        if not all(isinstance(value, int) for value in values):
            raise PageObjectError("region geometry must use integer x, y, w and h values")
        geometry = cls(values[0], values[1], values[2], values[3])
        if geometry.x < 0 or geometry.y < 0 or geometry.width <= 0 or geometry.height <= 0:
            raise PageObjectError("region geometry must be positive and inside the canvas")
        return geometry

    def validate_inside(self, canvas_width: int, canvas_height: int) -> None:
        if self.x + self.width > canvas_width or self.y + self.height > canvas_height:
            raise PageObjectError("component geometry exceeds canvas")


@dataclass(frozen=True)
class PageComponent:
    component_id: str
    kind: str
    region: str
    geometry: Geometry
    payload: dict[str, Any]


@dataclass(frozen=True)
class PageObject:
    prompt_id: str
    book: str
    level: str
    page_type: str
    template_id: str
    canvas_width: int
    canvas_height: int
    dpi: int
    components: tuple[PageComponent, ...]
    output_stem: str

    def validate(self) -> None:
        if (self.canvas_width, self.canvas_height, self.dpi) != (2480, 3508, 300):
            raise PageObjectError("Page Object must use locked A4 portrait geometry")
        if not self.prompt_id or not self.template_id or not self.output_stem:
            raise PageObjectError("Page Object identity is incomplete")
        component_ids = [component.component_id for component in self.components]
        if len(component_ids) != len(set(component_ids)):
            raise PageObjectError("duplicate component_id")
        for component in self.components:
            component.geometry.validate_inside(self.canvas_width, self.canvas_height)

    def component(self, component_id: str) -> PageComponent:
        matches = [component for component in self.components if component.component_id == component_id]
        if len(matches) != 1:
            raise PageObjectError(f"expected exactly one component: {component_id}")
        return matches[0]

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
