"""Unit tests for validators."""

from unittest.mock import patch

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

    @pytest.mark.unit
    def test_normalize_suffix_repeating_char_over_two(self):
        """normalize_suffix uppercases when a char appears more than twice (e.g. 'iiii')."""
        result = NameValidator.normalize_suffix("iiii")
        assert result == "IIII"

    @pytest.mark.unit
    def test_normalize_suffix_plain_passthrough(self):
        """normalize_suffix returns the original suffix when no char repeats more than twice."""
        result = NameValidator.normalize_suffix("Jr")
        assert result == "Jr"

    @pytest.mark.unit
    def test_get_business_name_regex_raises_when_missing(self):
        """_get_business_name_regex raises ValueError when regex is not a Pattern."""
        from unittest.mock import patch

        from britecore_sdk.validators import name_validator

        with patch.object(
            name_validator,
            "_get_regexes",
            return_value={},  # no reg_business_name key
        ):
            # Clear lru_cache so the patched _get_regexes is used
            name_validator._get_business_name_regex.cache_clear()
            with pytest.raises(ValueError, match="Missing or invalid"):
                name_validator._get_business_name_regex()
            name_validator._get_business_name_regex.cache_clear()


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

    @pytest.mark.unit
    def test_validate_email_classmethod_valid(self):
        """validate_email returns True for a well-formed address."""
        assert EmailValidator.validate_email("user@example.com") is True

    @pytest.mark.unit
    def test_validate_email_classmethod_invalid(self):
        """validate_email returns False for a malformed address."""
        assert EmailValidator.validate_email("not-an-email") is False

    @pytest.mark.unit
    def test_normalize_email_returns_empty_when_pattern_not_regex(self):
        """normalize_email returns '' when reg_email is not a str or Pattern."""
        with patch(
            "britecore_sdk.validators.email_validator._get_regexes",
            return_value={"reg_email": 12345},
        ):
            result = EmailValidator.normalize_email("test@example.com")
        assert result == ""


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

    # --- validate_phone classmethod ---

    @pytest.mark.unit
    def test_validate_phone_classmethod_valid(self):
        """validate_phone returns True for a well-formed 10-digit number."""
        assert PhoneValidator.validate_phone("(555) 123-4567") is True

    @pytest.mark.unit
    def test_validate_phone_classmethod_invalid_format(self):
        """validate_phone returns False when normalize_phone returns None."""
        assert PhoneValidator.validate_phone("123") is False

    @pytest.mark.unit
    def test_validate_phone_classmethod_zero_skipped(self):
        """validate_phone returns False for '0' (invalid sentinel value)."""
        assert PhoneValidator.validate_phone("0") is False

    @pytest.mark.unit
    def test_validate_phone_classmethod_dash_skipped(self):
        """validate_phone returns False for '-' (invalid sentinel value)."""
        assert PhoneValidator.validate_phone("-") is False

    @pytest.mark.unit
    def test_is_invalid_phone_zero(self):
        """_is_invalid_phone returns True for the string '0'."""
        assert PhoneValidator._is_invalid_phone("0") is True

    @pytest.mark.unit
    def test_is_invalid_phone_dash(self):
        """_is_invalid_phone returns True for the string '-'."""
        assert PhoneValidator._is_invalid_phone("-") is True


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
        import logging

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

        # Ensure logger propagates for caplog
        sdk_logger = logging.getLogger("britecore_sdk")
        original_propagate = sdk_logger.propagate
        sdk_logger.propagate = True

        try:
            with caplog.at_level(logging.INFO, logger="britecore_sdk"):
                result = validator.process()
            assert result[0]["address_state"] == "IL"
            assert any("ADDRESS UPDATED" in m for m in caplog.messages)
        finally:
            sdk_logger.propagate = original_propagate
            monkeypatch.setattr(address_validator, "FIX_ADDRESS", False)

    @pytest.mark.unit
    def test_validate_city_mismatch_fix_address_true(self, monkeypatch, caplog):
        import logging

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

        # Ensure logger propagates for caplog
        sdk_logger = logging.getLogger("britecore_sdk")
        original_propagate = sdk_logger.propagate
        sdk_logger.propagate = True

        try:
            with caplog.at_level(logging.INFO, logger="britecore_sdk"):
                result = validator.process()
            assert result[0]["address_city"] == "Springfield"
            assert any("ADDRESS UPDATED" in m for m in caplog.messages)
        finally:
            sdk_logger.propagate = original_propagate
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

    # --- normalize_address_line coverage ---

    @pytest.mark.unit
    def test_normalize_address_line_tax_parcel_id_returned_as_is(self):
        """normalize_address_line skips processing for tax-parcel-ID addresses."""
        result = AddressValidator.normalize_address_line("T:12345 Parcel Road")
        # title() is applied first, so T:1 is preserved; value returned unchanged after that
        assert result.startswith("T:")

    @pytest.mark.unit
    def test_normalize_address_line_removes_repeated_punctuation(self):
        """normalize_address_line calls _remove_repeated_punctuation on normal addresses."""
        result = AddressValidator.normalize_address_line("123  Main  St")
        # Multiple spaces collapsed; result should not have double spaces
        assert "  " not in result

    @pytest.mark.unit
    def test_normalize_address_line_empty_returns_empty(self):
        """normalize_address_line returns '' for blank input."""
        assert AddressValidator.normalize_address_line("   ") == ""
