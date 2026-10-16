"""Consistency checks for architecture_primitives.primitives.data.DataArchitecture."""

import pytest
from pydantic import ValidationError

from architecture_primitives.primitives.data import DataArchitecture

from .conftest import (
    make_business_architecture,
    make_capability,
    make_entity,
    make_external_system,
)


def test_consistent_data_architecture_is_valid():
    billing = make_capability("Billing")
    external = make_external_system("PaymentGateway")
    business = make_business_architecture([billing], external_systems=[external])
    entities = [
        make_entity("Invoice", billing),
        make_entity("Payment", billing, owner=external),
    ]

    architecture = DataArchitecture(
        business_architecture=business,
        entities=entities,
        relationships=[],
    )

    assert architecture.entities == entities


def test_entity_referencing_unknown_capability_is_rejected():
    known = make_capability("Billing")
    unknown = make_capability("Shipping")
    business = make_business_architecture([known])
    entities = [
        make_entity("Invoice", known),
        make_entity("Parcel", unknown),
    ]

    with pytest.raises(ValidationError) as exc_info:
        DataArchitecture(
            business_architecture=business,
            entities=entities,
            relationships=[],
        )

    message = str(exc_info.value)
    assert "Parcel" in message
    assert "Shipping" in message
    assert "not defined in the business architecture" in message


def test_capability_without_entities_is_rejected():
    billing = make_capability("Billing")
    shipping = make_capability("Shipping")
    business = make_business_architecture([billing, shipping])
    entities = [make_entity("Invoice", billing)]

    with pytest.raises(ValidationError) as exc_info:
        DataArchitecture(
            business_architecture=business,
            entities=entities,
            relationships=[],
        )

    message = str(exc_info.value)
    assert "Shipping" in message
    assert "no associated data entities" in message


def test_external_system_owning_no_entity_is_rejected():
    billing = make_capability("Billing")
    external = make_external_system("PaymentGateway")
    business = make_business_architecture([billing], external_systems=[external])
    entities = [make_entity("Invoice", billing)]

    with pytest.raises(ValidationError) as exc_info:
        DataArchitecture(
            business_architecture=business,
            entities=entities,
            relationships=[],
        )

    message = str(exc_info.value)
    assert "PaymentGateway" in message
    assert "does not own any data entity" in message
