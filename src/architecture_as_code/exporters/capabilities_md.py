"""Capability-focused Markdown exporter for the Solution Architecture.

Renders the solution as a Markdown document organised by business capability and
writes it to a file on disk.
"""

from pathlib import Path

from architecture_as_code.exporters.renderers.capabilities_md import (
    render_capabilities_architecture,
)
from architecture_as_code.primitives.solution import SolutionArchitecture


def render(destination: Path, solution_architecture: SolutionArchitecture) -> None:
    """Render the capability view to a single Markdown file at ``destination``."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_capabilities_architecture(solution_architecture), encoding="utf-8"
    )
