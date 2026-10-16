"""Markdown exporter for the UC2 Business Architecture.

Renders the business architecture as Markdown tables:
* one table per value stream (its ordered stages),
* a table of business capabilities,
* a table of stakeholders.
"""

from architecture_primitives.exporters.renderers import MD
from architecture_primitives.primitives.business import (
    BusinessArchitecture,
    BusinessCapability,
    ExternalSystem,
    Integration,
    Stakeholder,
    ValueStream,
)


def _escape(text: str) -> str:
    """Make a value safe for a single Markdown table cell."""
    return text.replace("\n", " ").replace("|", "\\|").strip()


def render_value_stream(value_stream: ValueStream) -> MD:
    header = (
        "| # | Stage | Capability | Stakeholders | External Systems | "
        "Entrance Criteria | Exit Criteria | Value Item |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |"
    )

    rows = []
    for i, stage in enumerate(value_stream.stages, start=1):
        stakeholders = ", ".join(s.name for s in stage.stakeholders)
        external_systems = ", ".join(s.name for s in stage.external_systems)
        rows.append(
            "| "
            + " | ".join(
                _escape(cell)
                for cell in (
                    str(i),
                    stage.name,
                    stage.capability.name,
                    stakeholders,
                    external_systems,
                    stage.entrance_criteria,
                    stage.exit_criteria,
                    stage.value_item,
                )
            )
            + " |"
        )

    return (
        f"## Value Stream: {value_stream.name}\n\n"
        f"{_escape(value_stream.description)}\n\n"
        + header
        + "\n"
        + "\n".join(rows)
    )


def render_capabilities(capabilities: list[BusinessCapability]) -> MD:
    header = "| Capability | Description |\n| --- | --- |"
    rows = [
        f"| {_escape(c.name)} | {_escape(c.description)} |"
        for c in capabilities
    ]
    return "## Business Capabilities\n\n" + header + "\n" + "\n".join(rows)


def render_stakeholders(stakeholders: list[Stakeholder]) -> MD:
    header = "| Stakeholder | Description |\n| --- | --- |"
    rows = [
        f"| {_escape(s.name)} | {_escape(s.description)} |"
        for s in stakeholders
    ]
    return "## Stakeholders\n\n" + header + "\n" + "\n".join(rows)


def render_external_systems(external_systems: list[ExternalSystem]) -> MD:
    header = "| External System | Description |\n| --- | --- |"
    rows = [
        f"| {_escape(s.name)} | {_escape(s.description)} |"
        for s in external_systems
    ]
    return "## External Systems\n\n" + header + "\n" + "\n".join(rows)


def render_integrations(integrations: list[Integration]) -> MD:
    header = "| External System | Reason |\n| --- | --- |"
    rows = [
        f"| {_escape(i.system.name)} | {_escape(i.reason)} |"
        for i in integrations
    ]
    return "## Integrations\n\n" + header + "\n" + "\n".join(rows)


def _collect_external_systems(
    architecture: BusinessArchitecture,
) -> list[ExternalSystem]:
    """Collect the unique external systems referenced across all stages."""
    seen: dict[str, ExternalSystem] = {}
    for value_stream in architecture.value_streams:
        for stage in value_stream.stages:
            for system in stage.external_systems:
                seen.setdefault(system.name, system)
    return list(seen.values())


def render_business_architecture(architecture: BusinessArchitecture) -> MD:
    sections = ["# Business Architecture"]
    sections.extend(render_value_stream(vs) for vs in architecture.value_streams)
    sections.append(render_capabilities(architecture.capabilities))
    sections.append(render_stakeholders(architecture.stakeholders))
    sections.append(render_external_systems(_collect_external_systems(architecture)))
    sections.append(render_integrations(architecture.integrations))
    return "\n\n".join(sections) + "\n"
