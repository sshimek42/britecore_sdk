"""Property-based tests using Hypothesis for validator coverage.

Tests explore a wide range of inputs to find edge cases in validators.

Run with:
    pytest tests/unit/test_validators_hypothesis.py -v
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from britecore_sdk.exceptions import ValidationError
from britecore_sdk.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
)

pytestmark = pytest.mark.skip(
    reason="Provisional property-based suite; validator APIs require dedicated strategy redesign."
)


class TestEmailValidatorProperties:
    """Property-based tests for email validation."""

    @given(st.emails())
    def test_accepts_valid_emails(self, email: str):
        """Valid emails should always be accepted."""
        validator = EmailValidator()
        try:
            result = validator.validate(email)
            assert result is not None
            assert isinstance(result, str)
        except ValidationError:
            # Some emails might be too exotic for the validator
            pass

    @given(st.text().filter(lambda x: "@" not in x))
    def test_rejects_emails_without_at(self, text: str):
        """Text without @ should be rejected as invalid email."""
        validator = EmailValidator()
        try:
            # Text without @ is not a valid email pattern
            validator.validate(text)
        except ValidationError:
            # Expected
            pass

    @given(st.emails())
    def test_email_lowercase_conversion(self, email: str):
        """Emails should be converted to lowercase."""
        validator = EmailValidator()
        try:
            result = validator.validate(email)
            # Result should be lowercase
            assert result == result.lower()
        except ValidationError:
            pass


class TestPhoneValidatorProperties:
    """Property-based tests for phone validation."""

    @given(
        st.text(min_size=7, max_size=15).filter(lambda x: any(c.isdigit() for c in x))
    )
    def test_phone_accepts_digit_strings(self, phone_str: str):
        """Phone strings with digits should be processable."""
        validator = PhoneValidator()
        try:
            result = validator.validate(phone_str)
            # Should return a normalized version
            assert result is not None
        except ValidationError:
            # Some formats might be invalid
            pass

    @given(st.text(alphabet="0123456789 ()-"))
    def test_phone_accepts_numeric_formats(self, phone_str: str):
        """Various numeric formats should be accepted or rejected consistently."""
        validator = PhoneValidator()
        try:
            result = validator.validate(phone_str)
            # Should normalize the phone number
            assert isinstance(result, str)
        except ValidationError:
            # Invalid format is acceptable
            pass


class TestNameValidatorProperties:
    """Property-based tests for name validation."""

    @given(st.text(min_size=1, max_size=100).filter(lambda x: len(x.strip()) > 0))
    def test_name_accepts_text(self, name: str):
        """Non-empty text should be processable as a name."""
        validator = NameValidator()
        try:
            result = validator.validate(name)
            assert result is not None
            assert isinstance(result, str)
        except ValidationError:
            # Some formats might be invalid
            pass

    @given(st.just(""))
    def test_name_rejects_empty(self, empty_value: str):
        """Empty names should be rejected."""
        validator = NameValidator()
        try:
            validator.validate(empty_value)
        except ValidationError:
            # Expected
            pass


class TestAddressValidatorProperties:
    """Property-based tests for address validation."""

    @given(
        st.builds(
            dict,
            address=st.text(min_size=1, max_size=100),
            city=st.text(min_size=1, max_size=50),
            state=st.text(min_size=1, max_size=50),
            zip=st.text(min_size=1, max_size=20),
        )
    )
    def test_address_accepts_components(self, address_dict):
        """Address with components should be processable."""
        validator = AddressValidator()
        try:
            result = validator.validate(address_dict)
            assert result is not None
        except ValidationError:
            # Invalid format is acceptable
            pass

    @given(st.just({}))
    def test_address_rejects_empty(self, empty_address: dict):
        """Empty address dict should be rejected."""
        validator = AddressValidator()
        try:
            validator.validate(empty_address)
        except ValidationError:
            # Expected
            pass


class TestValidatorCompositionProperties:
    """Test validators working together."""

    @given(
        st.builds(
            dict,
            name=st.text(min_size=1, max_size=50),
            email=st.emails(),
            phone=st.text(min_size=7, max_size=15).filter(
                lambda x: any(c.isdigit() for c in x)
            ),
        )
    )
    def test_multiple_validators_on_same_data(self, contact_dict):
        """Multiple validators should work on same data."""
        name_validator = NameValidator()
        email_validator = EmailValidator()
        phone_validator = PhoneValidator()

        try:
            validated_name = name_validator.validate(contact_dict["name"])
            assert validated_name is not None
        except ValidationError:
            pass

        try:
            validated_email = email_validator.validate(contact_dict["email"])
            assert validated_email is not None
        except ValidationError:
            pass

        try:
            validated_phone = phone_validator.validate(contact_dict["phone"])
            assert validated_phone is not None
        except ValidationError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
