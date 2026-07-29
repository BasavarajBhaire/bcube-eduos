from __future__ import annotations

from collections.abc import Callable
from typing import Any

Renderer = Callable[[dict[str, Any], Any], Any]
_RENDERERS: dict[str, Renderer] = {}


class RendererRegistrationError(ValueError):
    pass


def register(render_kind: str):
    def decorator(func: Renderer) -> Renderer:
        if render_kind in _RENDERERS:
            raise RendererRegistrationError(f"Renderer already registered: {render_kind}")
        _RENDERERS[render_kind] = func
        return func
    return decorator


def get_renderer(render_kind: str) -> Renderer:
    try:
        return _RENDERERS[render_kind]
    except KeyError as exc:
        raise RendererRegistrationError(f"No renderer registered: {render_kind}") from exc


def registered_renderers() -> set[str]:
    return set(_RENDERERS)
