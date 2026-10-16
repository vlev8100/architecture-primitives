"""Shared factory helpers for building minimal valid primitives objects."""

from architecture_primitives.primitives.application import (
    Api,
    Authentication,
    AuthenticationProtocol,
    Operation,
)
from architecture_primitives.primitives.business import (
    BusinessArchitecture,
    BusinessCapability,
    ExternalSystem,
    Integration,
    Solution,
    Stakeholder,
    ValueStream,
    ValueStreamStage,
)
from architecture_primitives.primitives.data import (
    DataArchitecture,
    LogicalEntity,
    Multiplicity,
    Relationship,
)

SOLUTION = BusinessArchitecture.SOLUTION


def make_capability(name: str) -> BusinessCapability:
    return BusinessCapability(name=name, description=f"{name} capability")


def make_external_system(name: str) -> ExternalSystem:
    return ExternalSystem(name=name, description=f"{name} system")


def make_entity(
    name: str,
    capability: BusinessCapability,
    owner: Solution | ExternalSystem = SOLUTION,
) -> LogicalEntity:
    return LogicalEntity(
        name=name,
        description=f"{name} entity",
        business_capability=capability,
        owner=owner,
    )


def make_operation(
    capability: BusinessCapability,
    entities: list[LogicalEntity],
    *,
    purpose: str = "do something",
    read_only: bool = True,
) -> Operation:
    return Operation(
        purpose=purpose,
        read_only=read_only,
        entities=entities,
        capability=capability,
    )


def make_api(operations: list[Operation], *, protocol: str = "REST") -> Api:
    return Api(
        protocol=protocol,
        documentation=[],
        operations=operations,
        authentication=Authentication(
            protocol=AuthenticationProtocol.NONE, key_details="none"
        ),
    )


def make_business_architecture(
    capabilities: list[BusinessCapability],
    *,
    external_systems: list[ExternalSystem] | None = None,
    stakeholders: list[Stakeholder] | None = None,
) -> BusinessArchitecture:
    external_systems = external_systems or []
    return BusinessArchitecture(
        value_streams=[],
        capabilities=capabilities,
        stakeholders=stakeholders or [],
        integrations=[
            Integration(system=system, reason=f"needs {system.name}")
            for system in external_systems
        ],
    )
