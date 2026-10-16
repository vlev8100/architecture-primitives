from enum import Enum

from pydantic import BaseModel, Field, model_validator

from architecture_primitives.primitives.business import (
    BusinessArchitecture,
    BusinessCapability,
    ExternalSystem,
    Solution,
)
from architecture_primitives.primitives.common import ArchitectureEntity


class LogicalEntity(ArchitectureEntity):
    """Data Entity"""

    business_capability: BusinessCapability = Field(description="associated business capability")
    owner: Solution | ExternalSystem = Field(
        description="Owner of the data entity. System that is responsible for it's creation, further lyfecicle"
    )


class Multiplicity(str, Enum):
    ZERO_OR_ONE = "0..1"
    EXACTLY_ONE = "1"
    ZERO_OR_MANY = "0..*"
    ONE_OR_MANY = "1..*"


class Relationship(ArchitectureEntity):
    from_entity: LogicalEntity = Field(description="The source entity type in the relationship.")
    to_entity: LogicalEntity = Field(description="The target entity type in the relationship.")
    from_multiplicity: Multiplicity = Field(
        description="How many source entity instances may participate in the relationship from the target's perspective."
    )
    to_multiplicity: Multiplicity = Field(
        description="How many target entity instances may be associated with one source entity instance."
    )


class DataArchitecture(BaseModel):
    business_architecture: BusinessArchitecture = Field(
        description="the business architecture this data architecture is anchored to"
    )
    entities: list[LogicalEntity] = Field(description="all data entities")
    relationships: list[Relationship] = Field(description="all relationships")

    @model_validator(mode="after")
    def _check_consistency(self) -> "DataArchitecture":
        problems = self._check()
        if problems:
            raise ValueError("Data architecture is inconsistent:\n" + "\n".join(f"- {p}" for p in problems))
        return self

    def _check(self) -> list[str]:
        """Every data entity must reference a business capability, every business
        capability must have at least one associated data entity, and every external
        system must own at least one data entity."""
        problems: list[str] = []

        capability_names = {c.name for c in self.business_architecture.capabilities}
        entity_capability_names = {e.business_capability.name for e in self.entities}

        for entity in self.entities:
            if entity.business_capability.name not in capability_names:
                problems.append(
                    f"Data entity '{entity.name}' references business capability "
                    f"'{entity.business_capability.name}' that is not defined in the business architecture."
                )

        for capability in self.business_architecture.capabilities:
            if capability.name not in entity_capability_names:
                problems.append(f"Business capability '{capability.name}' has no associated data entities.")

        external_systems = {
            integration.system.name: integration.system for integration in self.business_architecture.integrations
        }
        for value_stream in self.business_architecture.value_streams:
            for stage in value_stream.stages:
                for system in stage.external_systems:
                    external_systems.setdefault(system.name, system)

        owner_names = {entity.owner.name for entity in self.entities}
        for system_name in external_systems:
            if system_name not in owner_names:
                problems.append(f"External system '{system_name}' does not own any data entity.")

        return problems
