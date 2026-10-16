from typing import ClassVar, Optional

from pydantic import BaseModel, Field

from architecture_as_code.primitives.common import ArchitectureEntity

class Solution(ArchitectureEntity):
    """The solution being designed by this architecture"""
    pass


class ExternalSystem(ArchitectureEntity):
    """A system wich will be integrated with the solution"""
    pass

class Stakeholder(ArchitectureEntity):
    """Actor who receive measurable value from the value stream stage, or who contribute to creating or delivering that value"""
    pass


class BusinessCapability(ArchitectureEntity):
    """“A business capability is a particular ability or capacity that a business may possess or exchange to achieve a specific purpose or outcome.”"""


class ValueStreamStage(ArchitectureEntity):
    stakeholders: list[Stakeholder] = Field(description="stakeholders that participate in this stage")
    external_systems: list[ExternalSystem] = Field(description="list of external systems, engaged in this stage.")
    capability: BusinessCapability = Field(description="associated business capability")
    entrance_criteria: str = Field(
        description="The starting condition or state change that either triggers the value stream stage or enables it to be activated"
    )
    exit_criteria: str = Field(
        description="The end state condition that denotes the completion of the value stream stage; "
                    "i.e., when the required value has been created or delivered to the stakeholders. "
                    "This information becomes the entry criteria for the next value stream stage.")
    value_item: str = Field(description="The incremental value that is created or delivered to the participating stakeholder(s) by the value stream stage")


class ValueStream(ArchitectureEntity):
    """A value stream describes the value-creating activities"""

    stages: list[ValueStreamStage] = Field(description="Ordered list of stages")


class Integration(BaseModel):
    """A definition of integration with external system"""

    system: ExternalSystem = Field(description="A system on which the solution depends")
    reason: str = Field(description="A definition on why this integration is necessary")


class BusinessArchitecture(BaseModel):
    """A definition of business architecture"""

    SOLUTION: ClassVar[Solution] = Solution(name="Solution", description="The solution itself")

    value_streams: list[ValueStream] = Field(description="List of streams")
    capabilities: list[BusinessCapability] = Field(description="List of business capabilities")
    stakeholders: list[Stakeholder] = Field(description="List of business stakeholders")
    integrations: list[Integration] = Field(description="List of integrations")
    
