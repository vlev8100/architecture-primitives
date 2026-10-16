"""Markdown exporter for the Application Architecture.

Renders the application architecture as Markdown tables:
* a table of applications,
* per-application tables of exposed APIs,
* per-application software modules with their production code, test suites,
  integrations, persistence, repository and local agents.
"""

from architecture_as_code.exporters.renderers import MD
from architecture_as_code.primitives.application import (
    Api,
    Application,
    ApplicationArchitecture,
    GitRepo,
    Integration,
    Persistence,
    ProductionCode,
    SoftwareModule,
    TestSuite,
)
from architecture_as_code.primitives.business import ExternalSystem


def _escape(text: str) -> str:
    """Make a value safe for a single Markdown table cell."""
    return text.replace("\n", " ").replace("|", "\\|").strip()


def _tech(tech_stack) -> str:
    return ", ".join(f"{t.name} {t.version}".strip() for t in tech_stack)


def render_applications(applications: list[Application]) -> MD:
    header = (
        "| Application | Description | Modules |\n"
        "| --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                a.name,
                a.description,
                ", ".join(m.name for m in a.modules),
            )
        )
        + " |"
        for a in applications
    ]
    return "## Applications\n\n" + header + "\n" + "\n".join(rows)


def render_production_code(production_code: list[ProductionCode]) -> MD:
    header = (
        "| Location | Tech Stack | Packages |\n"
        "| --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                str(pc.location),
                _tech(pc.tech_stack),
                ", ".join(str(p.path) for p in pc.software_packages),
            )
        )
        + " |"
        for pc in production_code
    ]
    return "#### Production Code\n\n" + header + "\n" + "\n".join(rows)


def render_test_suites(test_suites: list[TestSuite]) -> MD:
    header = (
        "| Location | Type | Tech Stack | Packages |\n"
        "| --- | --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                str(ts.location),
                ts.type.value,
                _tech(ts.core_tech_stack),
                ", ".join(str(p.path) for p in ts.software_packages),
            )
        )
        + " |"
        for ts in test_suites
    ]
    return "#### Test Suites\n\n" + header + "\n" + "\n".join(rows)


def render_apis(apis: list[Api]) -> MD:
    header = (
        "| Protocol | Authentication | Operation | Read Only | "
        "Capability | Entities |\n"
        "| --- | --- | --- | --- | --- | --- |"
    )
    rows = []
    for api in apis:
        for op in api.operations:
            rows.append(
                "| "
                + " | ".join(
                    _escape(cell)
                    for cell in (
                        api.protocol,
                        api.authentication.protocol.value,
                        op.purpose,
                        "Yes" if op.read_only else "No",
                        op.capability.name,
                        ", ".join(e.name for e in op.entities),
                    )
                )
                + " |"
            )
    return "### APIs\n\n" + header + "\n" + "\n".join(rows)


def _target_name(target: str | ExternalSystem) -> str:
    return target.name if isinstance(target, ExternalSystem) else target


def render_integrations(integrations: list[Integration]) -> MD:
    header = (
        "| Target | Protocol | Operation | Read Only | Capability |\n"
        "| --- | --- | --- | --- | --- |"
    )
    rows = []
    for integration in integrations:
        for op in integration.operations:
            rows.append(
                "| "
                + " | ".join(
                    _escape(cell)
                    for cell in (
                        _target_name(integration.target),
                        integration.protocol,
                        op.purpose,
                        "Yes" if op.read_only else "No",
                        op.capability.name,
                    )
                )
                + " |"
            )
    return "#### Integrations\n\n" + header + "\n" + "\n".join(rows)


def render_persistance(persistance: Persistence) -> MD:
    header = (
        "| Storage Type | Tech Stack | Entities |\n"
        "| --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                storage.type.value,
                _tech(storage.tech_stack),
                ", ".join(
                    f"{pe.class_name} ({pe.logical_entity.name})"
                    for pe in storage.entities
                ),
            )
        )
        + " |"
        for storage in persistance.storage
    ]
    return "#### Persistence\n\n" + header + "\n" + "\n".join(rows)


def render_agents(git_repos: list[GitRepo]) -> MD:
    header = (
        "| Repository | Agent | Path | Purpose |\n"
        "| --- | --- | --- | --- |"
    )
    rows = [
        "| "
        + " | ".join(
            _escape(cell)
            for cell in (
                repo.name,
                agent.name,
                str(agent.path),
                agent.purpose,
            )
        )
        + " |"
        for repo in git_repos
        for agent in repo.agents
    ]
    return "### Local Agents\n\n" + header + "\n" + "\n".join(rows)


def render_software_module(module: SoftwareModule) -> MD:
    sections = [
        f"### Module: {module.name}",
        _escape(module.description),
        "**Business capabilities:** "
        + ", ".join(c.name for c in module.business_capabilities),
        f"**Repository:** {_escape(module.git_repo.name)} "
        f"({_escape(module.git_repo.git_reference)})",
    ]
    sections.append(render_production_code(module.production_code))
    if module.test_suites:
        sections.append(render_test_suites(module.test_suites))
    if module.integrations:
        sections.append(render_integrations(module.integrations))
    if module.persistence.storage:
        sections.append(render_persistance(module.persistence))
    return "\n\n".join(sections)


def _unique_git_repos(application: Application) -> list[GitRepo]:
    """Distinct git repositories referenced across an application's modules."""
    seen: dict[str, GitRepo] = {}
    for module in application.modules:
        seen.setdefault(module.git_repo.git_reference, module.git_repo)
    return list(seen.values())


def render_application(application: Application) -> MD:
    sections = [f"## Application: {application.name}", _escape(application.description)]
    if application.apis:
        sections.append(render_apis(application.apis))
    git_repos = _unique_git_repos(application)
    if any(repo.agents for repo in git_repos):
        sections.append(render_agents(git_repos))
    sections.extend(render_software_module(m) for m in application.modules)
    return "\n\n".join(sections)


def render_application_architecture(architecture: ApplicationArchitecture) -> MD:
    sections = ["# Application Architecture"]
    sections.append(render_applications(architecture.applications))
    sections.extend(
        render_application(app) for app in architecture.applications
    )
    return "\n\n".join(sections) + "\n"
