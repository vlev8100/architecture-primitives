from enum import Enum, StrEnum
from typing import Annotated, ClassVar, Optional

from pydantic import AfterValidator, BaseModel, Field, model_validator
from pathlib import Path

from architecture_as_code.primitives.business import (
    BusinessCapability,
    ExternalSystem,    
)
from architecture_as_code.primitives.common import ArchitectureEntity
from architecture_as_code.primitives.data import LogicalEntity


def _reject_absolute_path(path: Path) -> Path:
    if path.is_absolute():
        raise ValueError(f"path must be relative to the git repo, not absolute: '{path}'")
    return path


# A repo-relative path; absolute paths are prohibited.
RelativePath = Annotated[Path, AfterValidator(_reject_absolute_path)]


class Technology(BaseModel):
    name: str = Field(description="name of the technology e.g., .Net, Postgres")
    version: str = Field(description="name of the technology")


class TestSuiteType(StrEnum):
    """Type of tests. 
    UNIT = unit tests; 
    INTEGRATION = tests that spin up the application or its subcomponents 
    with variable injection/IoC/logging and mocked integrations. Do not require application deployment to real env.;
    END_TO_END = tests that run agains application deployed to real environment"""
    
    UNIT = "UNIT"
    INTEGRATION = "INTEGRATION"
    END_TO_END = "END_TO_END"

class LocalAgent(BaseModel):  
    """Agent definition for agentic harneses like Claude or Github Copilot"""
    
    name: str = Field(description="name of the agent")
    path: RelativePath = Field(description="location within git repo")
    purpose: str = Field(description="purpose of the agent")


class GitRepo(BaseModel):
    name: str = Field(description="name of the repo")
    git_reference: str = Field(pattern=r"\.git$", description="a git repository url, must end with '.git'")
    agents: list[LocalAgent] = Field(description="list of agents within .github or .claude dirs")
        

class SoftwarePackage(BaseModel):  
    path: RelativePath = Field(description="location within git repo")
    purpose: str = Field(description="purpose of the package. defines what resources it holds")
    business_capabilities: list[BusinessCapability] = Field(description="list of capabilities, which are fully or partially implemented or tested within this package")


class TestSuite(BaseModel):
    location: RelativePath = Field(description="directory that contains tests")
    type: TestSuiteType = Field(description="type of the tests")
    core_tech_stack: list[Technology] = Field(description="framework, supporting libraries")
    software_packages: list[SoftwarePackage] = Field(description="a list packages")    


class ProductionCode(BaseModel):
    location: RelativePath = Field(description="directory that contains production code")
    tech_stack: list[Technology] = Field(description="framework, supporting libraries")
    software_packages: list[SoftwarePackage] = Field(description="a list packages")
    
    
class Operation(BaseModel):    
    purpose: str = Field(description="Purpose of the operation e.g., read customer profile")
    read_only: bool = Field(description="True if operation doesn't modify the application's business data.")
    entities: list[LogicalEntity] = Field(description="data entities read or modified by invoking this operation")
    capability: BusinessCapability = Field(description="a relevant business capability")
    

class AuthenticationProtocol(StrEnum):
    """
    OAUTH2 = OAuth2, based on external IDP like EntraID;
    API_KEY = keys destributed to clients, validated against fixed list;
    BASIC = user and password credentials;        
    NONE = no authentication. accessible to anyone with network access;
    CUSTOM = some custom mechanism;
    """
    
    OAUTH2 = "OAUTH2"
    API_KEY = "API_KEY"
    BASIC = "BASIC"
    CUSTOM = "CUSTOM"
    NONE = "NONE"

class Authentication(BaseModel):
    protocol: AuthenticationProtocol = Field(description="definition of protocol")
    key_details: str = Field(description="key details about authentication mechanism")

class Api(BaseModel):
    """API thru which external clients can access the application. Group by protocol, documentation"""
    
    protocol: str = Field(description="definition of protocol, e.g., REST, SOAP, websockets")    
    documentation: list[RelativePath] = Field(description="docs, specs that describe the API, usage scenarios")
    operations: list[Operation] = Field(description="list of operations implemented within this api")
    authentication: Authentication = Field(description="authentication details")

    @model_validator(mode="after")
    def _check_consistency(self) -> "Api":
        problems = self._check()
        if problems:
            raise ValueError(
                "API is inconsistent:\n"
                + "\n".join(f"- {p}" for p in problems)
            )
        return self

    def _check(self) -> list[str]:
        """All operations of an API must share one business capability, and every
        data entity touched by those operations must belong to that same capability."""
        problems: list[str] = []

        operation_capabilities = {op.capability.name for op in self.operations}
        if len(operation_capabilities) > 1:
            problems.append(
                "API groups operations from multiple business capabilities: "
                + ", ".join(sorted(operation_capabilities))
            )

        for operation in self.operations:
            for entity in operation.entities:
                if entity.business_capability.name != operation.capability.name:
                    problems.append(
                        f"Data entity '{entity.name}' belongs to business capability "
                        f"'{entity.business_capability.name}' but is used by an operation "
                        f"of the API's business capability '{operation.capability.name}'."
                    )

        return problems

class Integration(BaseModel):
    """Definition of itegration with downstream systems, where the application is a client and target is a server."""
    
    target: str | ExternalSystem = Field(description="counterparty external system or one of the applications that are part of the solution, referenced by their names")
    protocol: str = Field(description="definition of protocol, e.g., REST, SOAP, websockets, messaging")
    operations: list[Operation] = Field(description="list of operations invoked by the app")
    

class StorageType(StrEnum):
    IN_MEMORY = "IN_MEMORY"
    DATABASE = "DATABASE"
    FILE_SYSTEM = "FILE_SYSTEM"    
    

class PhysicalEntity(BaseModel):
    class_name: str = Field(description="name of the class in the codebase")
    logical_entity: LogicalEntity = Field(description="logical entity represented by this object")
    

class Storage(BaseModel):
    type: StorageType = Field(description="type of storage")
    entities: list[PhysicalEntity] = Field(description="entities stored on this media")
    tech_stack: list[Technology] = Field(description="list of technologies on which the storage media is based e.g., Postgres, Blob Storage, Redis")

    
class Persistence(BaseModel):
    storage: list[Storage] = Field(description="list of storage media and data entities in scope")
    

class SoftwareModule(ArchitectureEntity):
    """A self-containing library or module managed as part of the solution"""
    
    business_capabilities: list[BusinessCapability] = Field(description="business capabilities implemented within this app")
    git_repo: GitRepo = Field(description="a git repository")
    test_suites: list[TestSuite] = Field(description="a list of test suites")
    production_code: list[ProductionCode] = Field(min_length=1, description="production code, split into multiple entities if there are multiple independent "
                                                  "parts shipped in the same container, e.g., frontend and backend compiled in single deployable app, or multy-module systems")
    persistence: Persistence = Field(description="definition of persistence layer if any")
    integrations: list[Integration] = Field(description="list of integrations")
    external_modules: list["SoftwareModule"] = Field(description="external modules")

class Application(ArchitectureEntity):
    """A self-containing, independently deployable application"""
    
    modules: list[SoftwareModule] = Field(description="Modules bundled into the application")
    apis: list[Api] = Field(description="definition of APIs exposed by the application")


class ApplicationArchitecture(BaseModel):
    """A definition of application architecture"""

    applications: list[Application] = Field(description="All independently deployable applications that make up the solution")

