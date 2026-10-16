"""Markdown exporter for the UC2 Data Architecture.

Renders the data architecture as Markdown tables:
* a table of data entities (with owner and business capability),
* a table of relationships (with multiplicities).
"""

from architecture_as_code.exporters.renderers import MD
from architecture_as_code.primitives.data import (
    DataArchitecture,
    LogicalEntity,
    Relationship,
)


def _escape(text: str) -> str:
    """Make a value safe for a single Markdown table cell."""
    return text.replace("\n", " ").replace("|", "\\|").strip()


def render_entities(entities: list[LogicalEntity]) -> MD:
    header = (
        "| Entity | Business Capability | Owner | Description |\n"
        "| --- | --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                e.name,
                e.business_capability.name,
                e.owner.name,
                e.description,
            )
        )
        + " |"
        for e in entities
    ]
    return "## Data Entities\n\n" + header + "\n" + "\n".join(rows)


def render_relationships(relationships: list[Relationship]) -> MD:
    header = (
        "| From | Multiplicity | To | Multiplicity | Description |\n"
        "| --- | --- | --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                r.from_entity.name,
                r.from_multiplicity.value,
                r.to_entity.name,
                r.to_multiplicity.value,
                r.description,
            )
        )
        + " |"
        for r in relationships
    ]
    return "## Relationships\n\n" + header + "\n" + "\n".join(rows)


def render_data_architecture(architecture: DataArchitecture) -> MD:
    sections = ["# Data Architecture"]
    sections.append(render_entities(architecture.entities))
    sections.append(render_relationships(architecture.relationships))
    return "\n\n".join(sections) + "\n"
