from pydantic import BaseModel, Field

class ArchitectureEntity(BaseModel):
    """Base for all TOGAF metamodel entities. Carries the universal attributes."""

    name: str
    description: str