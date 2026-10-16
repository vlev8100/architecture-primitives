"""Markdown exporter for the UC2 Solution Architecture.

Combines the business, data and application layer exporters into a single
Markdown document for the whole solution.
"""

from architecture_as_code.exporters.renderers import MD
from architecture_as_code.exporters.renderers.application_md import (
    render_application_architecture,
)
from architecture_as_code.exporters.renderers.business_md import (
    render_business_architecture,
)
from architecture_as_code.exporters.renderers.data_md import render_data_architecture
from architecture_as_code.primitives.solution import SolutionArchitecture


def render_solution_architecture(architecture: SolutionArchitecture) -> MD:
    sections = [
        "# Solution Architecture",
        render_business_architecture(architecture.business),
        render_data_architecture(architecture.data),
        render_application_architecture(architecture.application),
    ]
    return "\n\n".join(sections) + "\n"
