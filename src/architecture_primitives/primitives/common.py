from pydantic import BaseModel


class ArchitectureEntity(BaseModel):
    """Base for all TOGAF metamodel entities. Carries the universal attributes."""

    name: str
    description: str
