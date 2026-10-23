from typing import Any

from pydantic import BaseModel, Field


class ArchitectureEntity(BaseModel):
    """Base for all TOGAF metamodel entities. Carries the universal attributes."""

    name: str
    description: str
    external_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata from external systems, e.g. {'archimate_id': '...'}.",
    )
