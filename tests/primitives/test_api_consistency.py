"""Consistency checks for architecture_primitives.primitives.application.Api."""

import pytest
from pydantic import ValidationError

from .conftest import (
    make_api,
    make_capability,
    make_entity,
    make_operation,
)


def test_api_with_single_capability_and_matching_entities_is_valid():
    capability = make_capability("Billing")
    entity = make_entity("Invoice", capability)
    operation = make_operation(capability, [entity])

    api = make_api([operation])

    assert api.operations == [operation]


def test_api_without_operations_is_valid():
    api = make_api([])

    assert api.operations == []


def test_api_grouping_operations_from_multiple_capabilities_is_rejected():
    billing = make_capability("Billing")
    shipping = make_capability("Shipping")
    op_billing = make_operation(billing, [make_entity("Invoice", billing)])
    op_shipping = make_operation(shipping, [make_entity("Parcel", shipping)])

    with pytest.raises(ValidationError) as exc_info:
        make_api([op_billing, op_shipping])

    message = str(exc_info.value)
    assert "multiple business capabilities" in message
    assert "Billing" in message
    assert "Shipping" in message


def test_api_operation_touching_foreign_capability_entity_is_rejected():
    billing = make_capability("Billing")
    shipping = make_capability("Shipping")
    foreign_entity = make_entity("Parcel", shipping)
    operation = make_operation(billing, [foreign_entity])

    with pytest.raises(ValidationError) as exc_info:
        make_api([operation])

    message = str(exc_info.value)
    assert "Parcel" in message
    assert "Shipping" in message
    assert "Billing" in message
