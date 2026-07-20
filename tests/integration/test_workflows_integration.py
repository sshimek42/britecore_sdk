"""Workflow and property tests for validators, models, and API endpoint patterns.

These tests replace the former skip-guarded template suite with always-on
coverage across three layers:

  1. **Validator property tests** – PhoneValidator, EmailValidator, NameValidator
     normalization logic exercised without any HTTP calls.
  2. **Model serialization tests** – BritecoreQuote.to_dict() and
     BritecoreContact.process_contact() output shape and field handling.
  3. **Endpoint workflow tests** – Policy, Contact, and Quote wrappers are
     called with a patched ``API_CLIENT`` (same pattern as test_endpoints.py)
     to verify path routing, payload building, and error guard behaviour.

Run the full suite:
    pytest tests/integration/ -v

Run only workflow tests:
    pytest tests/integration/test_workflows_integration.py -v
"""

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.integration


# ===========================================================================
# Validator property tests
# ===========================================================================


class TestPhoneValidatorProperties:
    """Property tests for PhoneValidator normalization and type mapping."""

    @pytest.mark.unit
    def test_10_digit_plain_number_formats_correctly(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.normalize_phone("9205551234") == "1-920-555-1234"

    @pytest.mark.unit
    def test_parenthetical_us_format_normalizes(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.normalize_phone("(920) 555-1234") == "1-920-555-1234"

    @pytest.mark.unit
    def test_dashes_stripped_before_format(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.normalize_phone("920-555-1234") == "1-920-555-1234"

    @pytest.mark.unit
    def test_short_number_returns_none(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.normalize_phone("555-1234") is None

    @pytest.mark.unit
    def test_empty_phone_is_invalid(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.validate_phone("") is False

    @pytest.mark.unit
    def test_zero_sentinel_is_invalid(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.validate_phone("0") is False

    @pytest.mark.unit
    def test_dash_sentinel_is_invalid(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.validate_phone("-") is False

    @pytest.mark.unit
    def test_valid_10_digit_passes_validation(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        assert PhoneValidator.validate_phone("9205551234") is True

    @pytest.mark.unit
    def test_invalid_sentinels_produce_empty_list(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        validator = PhoneValidator(
            [{"phone": "0", "type": "Home"}, {"phone": "-", "type": "Home"}]
        )
        assert validator.process() == []

    @pytest.mark.unit
    def test_type_mobile_maps_to_cell(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        result = PhoneValidator([{"phone": "9205551234", "type": "mobile"}]).process()
        assert result[0]["type"] == "Cell"

    @pytest.mark.unit
    def test_type_cellular_maps_to_cell(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        result = PhoneValidator([{"phone": "9205551234", "type": "cellular"}]).process()
        assert result[0]["type"] == "Cell"

    @pytest.mark.unit
    def test_type_business_maps_to_work(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        result = PhoneValidator([{"phone": "9205551234", "type": "business"}]).process()
        assert result[0]["type"] == "Work"

    @pytest.mark.unit
    def test_type_office_maps_to_work(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        result = PhoneValidator([{"phone": "9205551234", "type": "office"}]).process()
        assert result[0]["type"] == "Work"

    @pytest.mark.unit
    def test_invalid_phone_in_list_raises(self):
        from britecore_sdk.exceptions import BritecoreError
        from britecore_sdk.validators.phone_validator import PhoneValidator

        with pytest.raises(BritecoreError.InvalidPhoneNumber):
            PhoneValidator([{"phone": "123", "type": "Home"}]).process()

    @pytest.mark.unit
    def test_multiple_valid_phones_all_normalized(self):
        from britecore_sdk.validators.phone_validator import PhoneValidator

        entries = [
            {"phone": "9205551234", "type": "home"},
            {"phone": "(414) 555-9876", "type": "work"},
        ]
        result = PhoneValidator(entries).process()
        assert len(result) == 2
        assert result[0]["phone"] == "1-920-555-1234"
        assert result[1]["phone"] == "1-414-555-9876"


class TestEmailValidatorProperties:
    """Property tests for EmailValidator normalization and type mapping."""

    @pytest.mark.unit
    def test_valid_email_normalizes_to_lowercase(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        assert (
            EmailValidator.normalize_email("  User@Example.COM  ") == "user@example.com"
        )

    @pytest.mark.unit
    def test_invalid_email_returns_empty_string(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        assert EmailValidator.normalize_email("not-an-email") == ""

    @pytest.mark.unit
    def test_validate_true_for_valid_address(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        assert EmailValidator.validate_email("valid@example.com") is True

    @pytest.mark.unit
    def test_validate_false_for_invalid_address(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        assert EmailValidator.validate_email("bad-email") is False

    @pytest.mark.unit
    def test_validate_false_for_empty_string(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        assert EmailValidator.validate_email("") is False

    @pytest.mark.unit
    def test_type_home_maps_to_personal(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        result = EmailValidator(
            [{"email": "test@example.com", "type": "home"}]
        ).process()
        assert result[0]["type"] == "Personal"

    @pytest.mark.unit
    def test_type_personal_maps_to_personal(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        result = EmailValidator(
            [{"email": "test@example.com", "type": "personal"}]
        ).process()
        assert result[0]["type"] == "Personal"

    @pytest.mark.unit
    def test_type_business_maps_to_work(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        result = EmailValidator(
            [{"email": "test@example.com", "type": "business"}]
        ).process()
        assert result[0]["type"] == "Work"

    @pytest.mark.unit
    def test_type_work_maps_to_work(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        result = EmailValidator(
            [{"email": "test@example.com", "type": "work"}]
        ).process()
        assert result[0]["type"] == "Work"

    @pytest.mark.unit
    def test_invalid_email_in_list_raises(self):
        from britecore_sdk.exceptions import BritecoreError
        from britecore_sdk.validators.email_validator import EmailValidator

        with pytest.raises(BritecoreError.InvalidEmailAddress):
            EmailValidator([{"email": "not-an-email", "type": "Work"}]).process()

    @pytest.mark.unit
    def test_empty_email_entry_is_silently_skipped(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        result = EmailValidator([{"email": "", "type": "Work"}]).process()
        assert result == []

    @pytest.mark.unit
    def test_multiple_valid_emails_all_normalized(self):
        from britecore_sdk.validators.email_validator import EmailValidator

        entries = [
            {"email": "A@Example.COM", "type": "work"},
            {"email": "  B@EXAMPLE.ORG  ", "type": "home"},
        ]
        result = EmailValidator(entries).process()
        assert result[0]["email"] == "a@example.com"
        assert result[1]["email"] == "b@example.org"
        assert result[1]["type"] == "Personal"


class TestNameValidatorProperties:
    """Property tests for NameValidator normalization helpers."""

    @pytest.mark.unit
    def test_apostrophe_uppercase_after_apostrophe_lowercased(self):
        from britecore_sdk.validators.name_validator import NameValidator

        assert NameValidator.normalize_apostrophe("Karen'S") == "Karen's"

    @pytest.mark.unit
    def test_apostrophe_no_uppercase_after_apostrophe_unchanged(self):
        from britecore_sdk.validators.name_validator import NameValidator

        # "o'brien" has no uppercase char after the apostrophe → unchanged
        assert NameValidator.normalize_apostrophe("o'brien") == "o'brien"

    @pytest.mark.unit
    def test_apostrophe_uppercase_after_apostrophe_lowercased_result(self):
        from britecore_sdk.validators.name_validator import NameValidator

        # The regex lowercases ANY uppercase char immediately after '
        # so "O'Brien" → "O'brien"
        assert NameValidator.normalize_apostrophe("O'Brien") == "O'brien"

    @pytest.mark.unit
    def test_suffix_iv_uppercased(self):
        from britecore_sdk.validators.name_validator import NameValidator

        assert NameValidator.normalize_suffix("iv") == "IV"

    @pytest.mark.unit
    def test_suffix_iv_already_upper_unchanged(self):
        from britecore_sdk.validators.name_validator import NameValidator

        assert NameValidator.normalize_suffix("IV") == "IV"

    @pytest.mark.unit
    def test_suffix_iii_uppercased(self):
        from britecore_sdk.validators.name_validator import NameValidator

        # "iii" has three 'i' characters (count > 2) → full uppercase
        assert NameValidator.normalize_suffix("iii") == "III"

    @pytest.mark.unit
    def test_suffix_jr_not_uppercased_by_repeat_rule(self):
        from britecore_sdk.validators.name_validator import NameValidator

        # "Jr" — no character repeats more than twice → returned as-is
        assert NameValidator.normalize_suffix("Jr") == "Jr"


# ===========================================================================
# Model serialization tests
# ===========================================================================


class TestBritecoreQuoteModel:
    """Tests for BritecoreQuote.to_dict() output shape and field handling."""

    @pytest.mark.unit
    def test_to_dict_contains_all_required_fields(self):
        from britecore_sdk.models.quote import BritecoreQuote

        result = BritecoreQuote(
            number="Q-123",
            policy_type_id="pt-456",
            agency_id="ag-789",
            named_insureds=["John Doe"],
            risks=["risk-001"],
        ).to_dict()
        assert result["number"] == "Q-123"
        assert result["policy_type_id"] == "pt-456"
        assert result["agency_id"] == "ag-789"
        assert result["named_insureds"] == ["John Doe"]
        assert result["risks"] == ["risk-001"]

    @pytest.mark.unit
    def test_empty_description_auto_generated_from_number(self):
        from britecore_sdk.models.quote import BritecoreQuote

        result = BritecoreQuote(
            number="Q-MYREF",
            policy_type_id="pt-1",
            agency_id="ag-1",
            named_insureds=[],
            risks=[],
            description="",
        ).to_dict()
        # description="" → "From Policy {number[3:]}"
        # "Q-MYREF"[3:] == "YREF"
        assert "YREF" in result["description"]

    @pytest.mark.unit
    def test_explicit_description_preserved(self):
        from britecore_sdk.models.quote import BritecoreQuote

        result = BritecoreQuote(
            number="Q-001",
            policy_type_id="pt-1",
            agency_id="ag-1",
            named_insureds=[],
            risks=[],
            description="Custom description",
        ).to_dict()
        assert result["description"] == "Custom description"

    @pytest.mark.unit
    def test_none_inspection_dates_excluded_from_dict(self):
        from britecore_sdk.models.quote import BritecoreQuote

        result = BritecoreQuote(
            number="Q-001",
            policy_type_id="pt-1",
            agency_id="ag-1",
            named_insureds=[],
            risks=[],
        ).to_dict()
        assert "next_inspection_date" not in result
        assert "previous_inspection_date" not in result

    @pytest.mark.unit
    def test_set_inspection_dates_included_in_dict(self):
        from britecore_sdk.models.quote import BritecoreQuote

        result = BritecoreQuote(
            number="Q-001",
            policy_type_id="pt-1",
            agency_id="ag-1",
            named_insureds=[],
            risks=[],
            next_inspection_date="2025-06-01",
            previous_inspection_date="2024-06-01",
        ).to_dict()
        assert result["next_inspection_date"] == "2025-06-01"
        assert result["previous_inspection_date"] == "2024-06-01"

    @pytest.mark.unit
    def test_invalid_underwriting_questions_reset_to_empty_list(self):
        from britecore_sdk.models.quote import BritecoreQuote

        quote = BritecoreQuote(
            number="Q-001",
            policy_type_id="pt-1",
            agency_id="ag-1",
            named_insureds=[],
            risks=[],
        )
        quote.underwriting_questions = "bad-value"  # type: ignore[assignment]
        result = quote.to_dict()
        assert result["underwriting_questions"] == []


class TestBritecoreContactModel:
    """Tests for BritecoreContact.process_contact() output shape."""

    @pytest.mark.unit
    def test_process_contact_name_normalized(self):
        from britecore_sdk.models.contact import BritecoreContact

        with (
            patch("britecore_sdk.models.contact.AddressValidator") as mock_av,
            patch("britecore_sdk.models.contact.PhoneValidator") as mock_pv,
            patch("britecore_sdk.models.contact.EmailValidator") as mock_ev,
            patch("britecore_sdk.models.contact.NameValidator") as mock_nv,
        ):
            mock_nv.normalize_business_name.return_value = "Acme LLC"
            mock_av.return_value.process.return_value = [{"city": "Testville"}]
            mock_pv.return_value.process.return_value = []
            mock_ev.return_value.process.return_value = []

            result = BritecoreContact(
                name="acme llc", address={"city": "Testville"}
            ).process_contact()

        assert result["name"] == "Acme LLC"

    @pytest.mark.unit
    def test_process_contact_defaults_to_individual_type(self):
        from britecore_sdk.models.contact import BritecoreContact

        with (
            patch("britecore_sdk.models.contact.AddressValidator") as mock_av,
            patch("britecore_sdk.models.contact.PhoneValidator") as mock_pv,
            patch("britecore_sdk.models.contact.EmailValidator") as mock_ev,
            patch("britecore_sdk.models.contact.NameValidator") as mock_nv,
        ):
            mock_nv.normalize_business_name.return_value = "Bob Smith"
            mock_av.return_value.process.return_value = []
            mock_pv.return_value.process.return_value = []
            mock_ev.return_value.process.return_value = []

            result = BritecoreContact(name="Bob Smith", address={}).process_contact()

        assert result["type"] == "individual"

    @pytest.mark.unit
    def test_process_contact_organization_type_preserved(self):
        from britecore_sdk.models.contact import BritecoreContact

        with (
            patch("britecore_sdk.models.contact.AddressValidator") as mock_av,
            patch("britecore_sdk.models.contact.PhoneValidator") as mock_pv,
            patch("britecore_sdk.models.contact.EmailValidator") as mock_ev,
            patch("britecore_sdk.models.contact.NameValidator") as mock_nv,
        ):
            mock_nv.normalize_business_name.return_value = "Corp Inc"
            mock_av.return_value.process.return_value = []
            mock_pv.return_value.process.return_value = []
            mock_ev.return_value.process.return_value = []

            result = BritecoreContact(
                name="Corp Inc", address={}, contact_type="organization"
            ).process_contact()

        assert result["type"] == "organization"

    @pytest.mark.unit
    def test_process_contact_policy_number_included(self):
        from britecore_sdk.models.contact import BritecoreContact

        with (
            patch("britecore_sdk.models.contact.AddressValidator") as mock_av,
            patch("britecore_sdk.models.contact.PhoneValidator") as mock_pv,
            patch("britecore_sdk.models.contact.EmailValidator") as mock_ev,
            patch("britecore_sdk.models.contact.NameValidator") as mock_nv,
        ):
            mock_nv.normalize_business_name.return_value = "Bob Smith"
            mock_av.return_value.process.return_value = []
            mock_pv.return_value.process.return_value = []
            mock_ev.return_value.process.return_value = []

            result = BritecoreContact(
                name="Bob Smith", address={}, policy_number="POL-999"
            ).process_contact()

        assert result["policy_number"] == "POL-999"

    @pytest.mark.unit
    def test_process_contact_result_has_all_expected_keys(self):
        from britecore_sdk.models.contact import BritecoreContact

        with (
            patch("britecore_sdk.models.contact.AddressValidator") as mock_av,
            patch("britecore_sdk.models.contact.PhoneValidator") as mock_pv,
            patch("britecore_sdk.models.contact.EmailValidator") as mock_ev,
            patch("britecore_sdk.models.contact.NameValidator") as mock_nv,
        ):
            mock_nv.normalize_business_name.return_value = "Test"
            mock_av.return_value.process.return_value = []
            mock_pv.return_value.process.return_value = []
            mock_ev.return_value.process.return_value = []

            result = BritecoreContact(name="Test", address={}).process_contact()

        for key in ("name", "contact_id", "addresses", "phones", "emails", "type"):
            assert key in result, f"Missing key: {key}"


# ===========================================================================
# Endpoint workflow tests (patched transport)
# ===========================================================================


class TestPolicyWorkflows:
    """Policy endpoint workflow tests with patched API_CLIENT."""

    def test_retrieve_policy_by_number_routes_to_correct_path(self):
        with patch("britecore_sdk.api.api_calls.v2.policies.API_CLIENT") as mock:
            mock.multiple_parameter_verification.return_value = {
                "policy_number": "POL-001"
            }
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {
                "policy_id": "123",
                "policy_number": "POL-001",
            }

            from britecore_sdk.api.api_calls.v2.policies import retrieve_policy

            result = retrieve_policy(policy_number="POL-001")

        assert result["policy_number"] == "POL-001"
        mock.do_request.assert_called_once()
        assert (
            mock.do_request.call_args.kwargs["path"]
            == "/api/v2/policies/retrieve_policy"
        )

    def test_retrieve_policy_by_id_passes_id_in_payload(self):
        with patch("britecore_sdk.api.api_calls.v2.policies.API_CLIENT") as mock:
            mock.multiple_parameter_verification.return_value = {"policy_id": "pid-999"}
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"policy_id": "pid-999"}

            from britecore_sdk.api.api_calls.v2.policies import retrieve_policy

            result = retrieve_policy(policy_id="pid-999")

        assert result["policy_id"] == "pid-999"
        assert mock.do_request.call_args.kwargs["json"].get("policy_id") == "pid-999"

    def test_retrieve_policy_with_revision_state_appended(self):
        with patch("britecore_sdk.api.api_calls.v2.policies.API_CLIENT") as mock:
            mock.multiple_parameter_verification.return_value = {
                "policy_number": "POL-777"
            }
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {}

            from britecore_sdk.api.api_calls.v2.policies import retrieve_policy

            retrieve_policy(policy_number="POL-777", revision_state="published")

        call_json = mock.do_request.call_args.kwargs["json"]
        assert call_json.get("revision_state") == "published"


class TestContactWorkflows:
    """Contact endpoint workflow tests with patched API_CLIENT."""

    def test_new_contact_routes_to_correct_path(self):
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {
                "contact_id": "con-001",
                "name": "Jane Smith",
            }

            from britecore_sdk.api.api_calls.v2.contacts import new_contact

            _, contact_id = new_contact(
                name="Jane Smith",
                address=[
                    {
                        "address": "123 Main St",
                        "city": "Springfield",
                        "state": "IL",
                        "zip": "62701",
                        "type": "mailing",
                    }
                ],
            )

        assert contact_id == "con-001"
        assert (
            mock.do_request.call_args.kwargs["path"] == "/api/v2/contacts/new_contact"
        )

    def test_new_contact_normalizes_address_type(self):
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"contact_id": "con-002"}

            from britecore_sdk.api.api_calls.v2.contacts import new_contact

            new_contact(
                name="Alice",
                address=[{"address": "5 Oak Ave", "type": "home"}],
            )

        sent_json = mock.do_request.call_args.kwargs["json"]
        # Raw "home" must be mapped to the BC canonical value (not left as "home")
        assert sent_json["addresses"][0]["type"] != "home"

    def test_new_contact_missing_name_raises_missing_parameter(self):
        from britecore_sdk.api.api_calls.v2.contacts import new_contact
        from britecore_sdk.exceptions import BritecoreError

        with pytest.raises(BritecoreError.MissingParameter):
            new_contact(name="", address=[{"address": "123 Main", "type": "mailing"}])

    def test_new_contact_missing_address_raises_missing_parameter(self):
        from britecore_sdk.api.api_calls.v2.contacts import new_contact
        from britecore_sdk.exceptions import BritecoreError

        with pytest.raises(BritecoreError.MissingParameter):
            new_contact(name="Jane Smith", address=[])

    def test_new_contact_normalizes_phone_type(self):
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"contact_id": "con-003"}

            from britecore_sdk.api.api_calls.v2.contacts import new_contact

            new_contact(
                name="Bob",
                address=[{"address": "1 Test Rd", "type": "mailing"}],
                phone=[{"phone": "9205551234", "type": "mobile"}],
            )

        sent_json = mock.do_request.call_args.kwargs["json"]
        # "mobile" → "Cell"
        assert sent_json["phones"][0]["type"] == "Cell"

    def test_new_contact_normalizes_email_type(self):
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"contact_id": "con-004"}

            from britecore_sdk.api.api_calls.v2.contacts import new_contact

            new_contact(
                name="Carol",
                address=[{"address": "2 Oak Ave", "type": "mailing"}],
                email=[{"email": "carol@example.com", "type": "home"}],
            )

        sent_json = mock.do_request.call_args.kwargs["json"]
        # "home" → "Personal"
        assert sent_json["emails"][0]["type"] == "Personal"


class TestQuoteWorkflows:
    """Quote endpoint workflow tests with patched API_CLIENT."""

    def test_create_full_quote_returns_data_and_id_tuple(self):
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "q-001", "number": "Q001"}

            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            data, quote_id = create_full_quote(
                {"number": "Q001", "policy_type_id": "pt-1"}
            )

        assert quote_id == "q-001"
        assert data["number"] == "Q001"

    def test_create_full_quote_routes_to_correct_path(self):
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "q-002"}

            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            create_full_quote({"number": "Q002", "policy_type_id": "pt-1"})

        assert (
            mock.do_request.call_args.kwargs["path"]
            == "/api/v2/quotes/create_full_quote"
        )

    def test_create_full_quote_empty_dict_raises_missing_parameter(self):
        from britecore_sdk.api.api_calls.v2.quotes import create_full_quote
        from britecore_sdk.exceptions import BritecoreError

        with pytest.raises(BritecoreError.MissingParameter):
            create_full_quote({})

    def test_create_full_quote_none_raises_missing_parameter(self):
        from britecore_sdk.api.api_calls.v2.quotes import create_full_quote
        from britecore_sdk.exceptions import BritecoreError

        with pytest.raises(BritecoreError.MissingParameter):
            create_full_quote(None)  # type: ignore[arg-type]

    def test_create_full_quote_none_response_returns_none_tuple(self):
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = None

            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            data, quote_id = create_full_quote(
                {"number": "Q003", "policy_type_id": "pt-1"}
            )

        assert data is None
        assert quote_id is None

    def test_explicit_client_overrides_module_level_client(self):
        """create_full_quote(client=…) must use the provided client, not API_CLIENT."""
        explicit_client = MagicMock()
        explicit_client.do_request.return_value = MagicMock()
        explicit_client.process_result.return_value = {"id": "q-explicit"}

        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as module_mock:
            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            data, quote_id = create_full_quote(
                {"number": "Q-EX", "policy_type_id": "pt-1"},
                client=explicit_client,
            )

        module_mock.do_request.assert_not_called()
        explicit_client.do_request.assert_called_once()
        assert quote_id == "q-explicit"


# ===========================================================================
# Exception / error handling tests
# ===========================================================================


class TestErrorHandlingWorkflows:
    """Tests for SDK exception metadata and hierarchy."""

    def test_not_found_error_carries_404_status(self):
        from britecore_sdk.exceptions import NotFoundError

        err = NotFoundError("Resource not found", status_code=404)
        assert err.status_code == 404

    def test_authentication_error_carries_401_status(self):
        from britecore_sdk.exceptions import AuthenticationError

        # AuthenticationError takes http_status (not status_code); always resolves to 401
        err = AuthenticationError("Unauthorized", http_status=401)
        assert err.status_code == 401

    def test_rate_limit_error_carries_429_status(self):
        from britecore_sdk.exceptions import RateLimitError

        # RateLimitError always hard-codes 429; no status_code kwarg needed
        err = RateLimitError("Too many requests")
        assert err.status_code == 429

    def test_base_error_str_includes_request_id(self):
        from britecore_sdk.exceptions import BritecoreError

        err = BritecoreError.Base("Test error", request_id="abc123", status_code=500)
        assert "abc123" in str(err)

    def test_base_error_str_includes_error_code(self):
        from britecore_sdk.exceptions import BritecoreError

        err = BritecoreError.Base(
            "Test error", error_code="validation_failed", status_code=400
        )
        assert "validation_failed" in str(err)

    def test_missing_parameter_is_base_exception_subclass(self):
        from britecore_sdk.exceptions import BritecoreError

        err = BritecoreError.MissingParameter("required param missing")
        assert isinstance(err, BritecoreError.Base)
        assert isinstance(err, Exception)

    def test_flat_alias_is_same_class_as_nested(self):
        """Flat aliases (e.g. NotFoundError) must be the same object as BritecoreError.NotFoundError."""
        from britecore_sdk.exceptions import BritecoreError, NotFoundError

        assert NotFoundError is BritecoreError.NotFoundError

    def test_invalid_phone_number_is_base_subclass(self):
        from britecore_sdk.exceptions import BritecoreError

        err = BritecoreError.InvalidPhoneNumber("bad phone")
        assert isinstance(err, BritecoreError.Base)


# ===========================================================================
# Multi-environment / client management tests
# ===========================================================================


class TestMultiEnvironmentWorkflows:
    """Tests for multi-environment client management patterns."""

    def test_use_api_client_is_callable(self):
        from britecore_sdk.api.api_calls import use_api_client

        assert callable(use_api_client)

    def test_use_api_client_yields_the_provided_client(self):
        """use_api_client should yield the exact client inside the with-block."""
        from britecore_sdk.api.api_calls import use_api_client

        fake_client = MagicMock()
        with use_api_client(fake_client) as active:
            assert active is fake_client

    def test_init_api_client_returns_non_none(self):
        """init_api_client is patched by the autouse fixture; confirms non-None result."""
        from britecore_sdk.api.api_calls import init_api_client

        result = init_api_client("test_site")
        assert result is not None

    def test_get_api_client_returns_patched_mock(self):
        """The autouse fixture makes get_api_client() return the shared mock."""
        from britecore_sdk.api.api_calls import get_api_client

        client = get_api_client()
        assert client is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
