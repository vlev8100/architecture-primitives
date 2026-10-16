# architecture-primitives

The goal of this project is to provide a simple framework for capturing the architecture and known
conventions of software solutions.

Knowledge is captured in Python primitives with the help of dedicated agents, and is kept
agent/model agnostic. Exporters then provide views on this knowledge tailored to different agentic
harnesses/models: they generate harness/model specific instructions that can be easily incorporated
into Software factories.

Information captured in the solution definition should clarify:
* business capabilities implemented in the solution
* nature of integrations
* users of application, which business capabilities are utilized
* mapping of software packages to business capabilities
* nature of software package interdependencies

# Use cases
This knowledge graph should assist software developers and AI agents answering these questions:
* where to implement functionality X?
* where to find implementation of a business feature X?
* which technologies should I use for particular feature?
* is there any existing integrations with service X?
* which existing domain objects are related to my new feature? 
* what business features could be affected by making a change in package X ?

# Implementation

The framework is a Python package under `src/architecture_as_code`, organised into three parts:

## Primitives

`src/architecture_as_code/primitives/` holds the vocabulary used to describe a solution as
[Pydantic](https://docs.pydantic.dev/) models. Knowledge is captured by instantiating these
primitives, and Pydantic validation keeps the definition internally consistent (e.g. relative-only
paths, capability/entity cross-references). 

# Exporters

Exporters live in `src/architecture_as_code/exporters/` and produce harness/model-specific views on
the captured knowledge — instructions that can be incorporated into Software factories:

