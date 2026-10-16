"""Markdown exporter focused on business capabilities.

Renders one section per business capability. Each section carries the
capability's description followed by its logical entities grouped by the
application that persists them (linked through their physical entities).
"""

from architecture_primitives.exporters.renderers import MD
from architecture_primitives.primitives.application import (
    Application,
    PhysicalEntity,
    SoftwareModule,
)
from architecture_primitives.primitives.business import BusinessCapability
from architecture_primitives.primitives.solution import SolutionArchitecture


def _escape(text: str) -> str:
    """Make a value safe for a single Markdown table cell."""
    return text.replace("\n", " ").replace("|", "\\|").strip()


def _physical_entities(application: Application) -> list[PhysicalEntity]:
    """All physical entities persisted across an application's software modules."""
    return [
        physical
        for module in application.modules
        for storage in module.persistence.storage
        for physical in storage.entities
    ]


def _render_sub_modules(modules: list[SoftwareModule]) -> MD:
    header = (
        "| Module | Responsibilities | Git Reference | Production Code |\n"
        "| --- | --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                m.name,
                m.description,
                m.git_repo.git_reference,
                ", ".join(str(pc.location) for pc in m.production_code),
            )
        )
        + " |"
        for m in modules
    ]
    return "#### Sub-modules\n\n" + header + "\n" + "\n".join(rows)


def render_capability(
    capability: BusinessCapability, applications: list[Application]
) -> MD:
    sections = [f"## Capability: {capability.name}", _escape(capability.description)]

    grouped = False
    for application in applications:
        physical = [
            p
            for p in _physical_entities(application)
            if p.logical_entity.business_capability.name == capability.name
        ]
        if not physical:
            continue

        grouped = True
        # Group physical entities by their logical entity, preserving order.
        by_logical: dict[str, str] = {}
        for p in physical:
            logical = p.logical_entity
            by_logical.setdefault(logical.name, logical.description)

        header = (
            "| Logical Entity | Description |\n"
            "| --- | --- |"
        )
        rows = [
            f"| {_escape(name)} | {_escape(description)} |"
            for name, description in by_logical.items()
        ]
        sections.append(
            f"### Application: {application.name}\n\n"
            + f"{_escape(application.description)}\n\n"
            + _render_sub_modules(application.modules)
            + "\n\n"
            + "#### Owned Entities\n\n"
            + f"The logical entities below are owned by {_escape(application.name)}.\n\n"
            + header
            + "\n"
            + "\n".join(rows)
        )

    if not grouped:
        sections.append("_No logical entities are persisted by any application._")

    return "\n\n".join(sections)


def render_capabilities_architecture(architecture: SolutionArchitecture) -> MD:
    applications = architecture.application.applications
    sections = ["# Capabilities"]
    sections.extend(
        render_capability(capability, applications)
        for capability in architecture.business.capabilities
    )
    return "\n\n".join(sections) + "\n"
