from pydantic import BaseModel, Field, model_validator

from architecture_primitives.primitives.application import ApplicationArchitecture, SoftwareModule
from architecture_primitives.primitives.business import BusinessArchitecture
from architecture_primitives.primitives.data import DataArchitecture


class SolutionArchitecture(BaseModel):
    """A complete definition of a solution's architecture across the business, data and application layers."""

    business: BusinessArchitecture = Field(description="The business architecture of the solution")
    data: DataArchitecture = Field(description="The data architecture of the solution")
    application: ApplicationArchitecture = Field(description="The application architecture of the solution")

    @model_validator(mode="after")
    def _check_consistency(self) -> "SolutionArchitecture":
        problems = self._check()
        if problems:
            raise ValueError(
                "Solution architecture is inconsistent:\n"
                + "\n".join(f"- {p}" for p in problems)
            )
        return self

    def _check(self) -> list[str]:
        """Every business capability must be linked to at least one application
        via one of its software modules."""
        problems: list[str] = []

        linked_capabilities: set[str] = set()
        for application in self.application.applications:
            for module in application.modules:
                for capability in self._module_capabilities(module):
                    linked_capabilities.add(capability)

        for capability in self.business.capabilities:
            if capability.name not in linked_capabilities:
                problems.append(
                    f"Business capability '{capability.name}' is not linked to any application."
                )

        return problems

    def _module_capabilities(self, module: SoftwareModule) -> set[str]:
        capabilities = {capability.name for capability in module.business_capabilities}
        for external_module in module.external_modules:
            capabilities |= self._module_capabilities(external_module)
        return capabilities
