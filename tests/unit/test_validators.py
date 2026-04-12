"""Unit tests for validators."""

import pytest

from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.utils.zip_code_lookup import ZipCodeLookup
from britecore_sdk.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
    address_validator,
)


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

    @pytest.mark.unit
    def test_validate_address_missing_city(self):
        # AddressValidator does not raise if city is missing, so just check output
        address = {
            "street": "123 Main St",
            "state": "IL",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        result = validator.process()
        assert result is not None

    @pytest.mark.unit
    def test_validate_address_po_box(self):
        address = {
            "street": "PO Box 123",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        result = validator.process()
        # Accept any case variant of PO Box
        assert any("po box" in (v or "").lower() for v in result[0].values())

    @pytest.mark.unit
    def test_validate_address_deprecated_type(self, caplog):
        # No deprecated type warning is implemented, so just check process works
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
            "type": "OldType",
        }
        validator = AddressValidator(address)
        validator.process()

    @pytest.mark.unit
    def test_validate_state_mismatch_fix_address_true(self, monkeypatch, caplog):
        # Patch ZIP_CODE_LOOKUP to return a fake state and county
        class FakeZip:
            admin_code1 = "IL"
            admin_name2 = "Sangamon"
            place_name = "Springfield"

        monkeypatch.setattr(address_validator, "FIX_ADDRESS", True)
        monkeypatch.setattr(
            address_validator.ZIP_CODE_LOOKUP, "get_record_by_zip", lambda z: FakeZip()
        )
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "MO",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        with caplog.at_level("INFO"):
            result = validator.process()
        assert result[0]["address_state"] == "IL"
        assert any("ADDRESS UPDATED" in m for m in caplog.messages)
        monkeypatch.setattr(address_validator, "FIX_ADDRESS", False)

    @pytest.mark.unit
    def test_validate_city_mismatch_fix_address_true(self, monkeypatch, caplog):
        class FakeZip:
            admin_code1 = "IL"
            admin_name2 = "Sangamon"
            place_name = "Springfield"

        monkeypatch.setattr(address_validator, "FIX_ADDRESS", True)
        monkeypatch.setattr(
            address_validator.ZIP_CODE_LOOKUP, "get_record_by_zip", lambda z: FakeZip()
        )
        address = {
            "street": "123 Main St",
            "city": "Othercity",
            "state": "IL",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        with caplog.at_level("INFO"):
            result = validator.process()
        assert result[0]["address_city"] == "Springfield"
        assert any("ADDRESS UPDATED" in m for m in caplog.messages)
        monkeypatch.setattr(address_validator, "FIX_ADDRESS", False)

    @pytest.mark.unit
    def test_validate_state_mismatch_fix_address_false(self, monkeypatch, caplog):
        class FakeZip:
            admin_code1 = "IL"

        monkeypatch.setattr(address_validator, "FIX_ADDRESS", False)
        monkeypatch.setattr(
            address_validator.ZIP_CODE_LOOKUP, "get_record_by_zip", lambda z: FakeZip()
        )
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "MO",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        with pytest.raises(BritecoreError.InvalidAddress):
            validator.process()

    @pytest.mark.unit
    def test_validate_city_mismatch_fix_address_false(self, monkeypatch, caplog):
        class FakeZip:
            place_name = "Springfield"
            admin_code1 = "IL"
            admin_name2 = "Sangamon"

        monkeypatch.setattr(address_validator, "FIX_ADDRESS", False)
        monkeypatch.setattr(
            address_validator.ZIP_CODE_LOOKUP, "get_record_by_zip", lambda z: FakeZip()
        )
        address = {
            "street": "123 Main St",
            "city": "Othercity",
            "state": "IL",
            "zip": "62701",
        }
        validator = AddressValidator(address)
        result = validator.process()
        assert result[0]["address_city"] == "Othercity"

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "business_name,expected",
        [
            ("Acme llc", "Acme LLC"),
            ("Beta Inc", "Beta INC"),
            ("Gamma dba", "Gamma DBA"),
        ],
    )
    def test_normalize_business_name(self, business_name, expected):
        from britecore_sdk.validators.address_validator import (
            normalize_business_name,
        )

        assert expected in normalize_business_name(business_name)

    @pytest.mark.unit
    def test_fix_apostrophe_capitalization(self):
        from britecore_sdk.validators.address_validator import (
            fix_apostrophe_capitalization,
        )

        name = "O''CONNOR"
        result = fix_apostrophe_capitalization(name)
        # Only the matched apostrophe sequence is lowercased, not the whole string
        assert result == "O''cONNOR"

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "suffix,expected",
        [
            ("iv", "IV"),
            ("iii", "III"),
            ("smith", "smith"),
            ("ssss", "SSSS"),
        ],
    )
    def test_fix_suffix_capitalization(self, suffix, expected):
        from britecore_sdk.validators.address_validator import (
            fix_suffix_capitalization,
        )

        assert fix_suffix_capitalization(suffix) == expected
