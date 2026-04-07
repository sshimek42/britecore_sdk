"""Unit tests for validators."""

import pytest

from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.utils.zip_code_lookup import ZipCodeLookup
from britecore_libraries.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
)
from britecore_libraries.validators import address_validator


class TestNameValidator:
    """Tests for NameValidator."""

    @pytest.mark.unit
    def test_normalize_business_name_llc(self):
        """Test normalizing LLC suffix."""
        name = "ABC Company llc"
        result = NameValidator.normalize_business_name(name)

        assert "LLC" in result

    @pytest.mark.unit
    def test_normalize_business_name_inc(self):
        """Test normalizing Inc suffix."""
        name = "Tech Corp inc"
        result = NameValidator.normalize_business_name(name)

        assert "INC" in result

    @pytest.mark.unit
    def test_normalize_business_name_dba(self):
        """Test normalizing DBA suffix."""
        name = "Trading as dba Partners"
        result = NameValidator.normalize_business_name(name)

        assert "DBA" in result

    @pytest.mark.unit
    def test_normalize_apostrophe(self):
        """Test apostrophe normalization."""
        name = "Karen'S Store"
        result = NameValidator.normalize_apostrophe(name)

        # Should lowercase the letter after apostrophe
        assert "'" in result

    @pytest.mark.unit
    def test_normalize_suffix_iv(self):
        """Test suffix normalization for IV."""
        suffix = "iv"
        result = NameValidator.normalize_suffix(suffix)

        assert result == "IV"

    @pytest.mark.unit
    def test_normalize_suffix_iii(self):
        """Test suffix normalization for III."""
        suffix = "iii"
        result = NameValidator.normalize_suffix(suffix)

        assert result == "III"


class TestEmailValidator:
    """Tests for EmailValidator."""

    @pytest.mark.unit
    def test_validate_email_valid(self):
        """Test valid email address."""
        email = [{"email": "test@example.com", "type": "Home"}]
        validator = EmailValidator(email)
        result = validator.process()

        assert result is not None
        assert len(result) > 0

    @pytest.mark.unit
    def test_validate_email_invalid(self):
        """Test invalid email address."""
        email = [{"email": "not_an_email", "type": "Home"}]
        validator = EmailValidator(email)

        with pytest.raises(BritecoreError.InvalidEmailAddress):
            validator.process()

    @pytest.mark.unit
    def test_validate_email_empty_list(self):
        """Test with empty email list."""
        email = []
        validator = EmailValidator(email)
        result = validator.process()

        assert result is not None


class TestPhoneValidator:
    """Tests for PhoneValidator."""

    @pytest.mark.unit
    def test_validate_phone_valid_format(self):
        """Test valid phone number."""
        phone = [{"phone": "5551234567", "type": "Home"}]
        validator = PhoneValidator(phone)
        result = validator.process()

        assert result is not None

    @pytest.mark.unit
    def test_validate_phone_with_formatting(self):
        """Test phone number with formatting."""
        phone = [{"phone": "(555) 123-4567", "type": "Home"}]
        validator = PhoneValidator(phone)
        result = validator.process()

        assert result is not None

    @pytest.mark.unit
    def test_validate_phone_invalid(self):
        """Test invalid phone number."""
        phone = [{"phone": "123", "type": "Home"}]
        validator = PhoneValidator(phone)

        with pytest.raises(BritecoreError.InvalidPhoneNumber):
            validator.process()

    @pytest.mark.unit
    def test_validate_phone_empty_list(self):
        """Test with empty phone list."""
        phone = []
        validator = PhoneValidator(phone)
        result = validator.process()

        assert result is not None


class TestAddressValidator:
    """Tests for AddressValidator."""

    @pytest.mark.unit
    def test_validate_address_complete(self):
        """Test address with all fields."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
            "type": "Mailing/Billing",
        }
        validator = AddressValidator(address)
        result = validator.process()

        assert result is not None

    @pytest.mark.unit
    def test_validate_address_minimal(self):
        """Test address with minimal fields."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        result = validator.process()

        assert result is not None

    @pytest.mark.unit
    def test_validate_address_invalid_state(self):
        """Test address with invalid state."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "XX",  # Invalid state
            "zip": "62701",
        }
        validator = AddressValidator(address)

        with pytest.raises(BritecoreError.InvalidAddress):
            validator.process()

    @pytest.mark.unit
    def test_validate_address_invalid_zip(self):
        """Test address with invalid zip code."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "invalid",
        }
        validator = AddressValidator(address)

        with pytest.raises(BritecoreError.InvalidAddress):
            validator.process()

    @pytest.mark.unit
    def test_validate_address_missing_zip_uses_lookup(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Test missing ZIP is resolved from state/city lookup."""
        lookup = ZipCodeLookup(
            [
                {
                    "postal code": "62701",
                    "place name": "Springfield",
                    "admin code1": "IL",
                    "admin name2": "Sangamon",
                }
            ]
        )
        monkeypatch.setattr(address_validator, "ZIP_CODE_LOOKUP", lookup)

        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
        }
        result = AddressValidator(address).process()

        assert result[0]["address_zip"] == "62701"

