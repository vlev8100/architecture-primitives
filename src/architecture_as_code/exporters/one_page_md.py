"""One-page Markdown exporter for the Solution Architecture.

Renders the whole solution as a single Markdown document and writes it to a
file on disk.
"""

from pathlib import Path

from architecture_as_code.exporters.renderers.solution_md import (
    render_solution_architecture,
)
from architecture_as_code.primitives.solution import SolutionArchitecture


def render(destination: Path, solution_architecture: SolutionArchitecture) -> None:
    """Render the solution architecture to a single Markdown file at ``destination``."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_solution_architecture(solution_architecture), encoding="utf-8"
    )
