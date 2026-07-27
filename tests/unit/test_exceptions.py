"""Tests for exceptions and strict import behavior."""

import pytest

from britecore_sdk.exceptions import BritecoreError


class TestBritecoreExceptions:
    """Tests for BritecoreError subclasses."""

    @pytest.mark.unit
    def test_no_data_returned_exception(self):
        """Test NoDataReturned exception."""
        with pytest.raises(BritecoreError.NoDataReturned):
            raise BritecoreError.NoDataReturned("Test error message")

    @pytest.mark.unit
    def test_no_data_returned_str(self):
        """Test NoDataReturned string representation."""
        exc = BritecoreError.NoDataReturned("Test error")
        assert "no data returned" in str(exc).lower()

    @pytest.mark.unit
    def test_no_token_returned_exception(self):
        """Test NoTokenReturned exception."""
        with pytest.raises(BritecoreError.NoTokenReturned):
            raise BritecoreError.NoTokenReturned("Token error")

    @pytest.mark.unit
    def test_no_token_returned_str(self):
        """Test NoTokenReturned string representation."""
        exc = BritecoreError.NoTokenReturned("Test error")
        assert "token" in str(exc).lower()

    @pytest.mark.unit
    def test_invalid_phone_number_exception(self):
        """Test InvalidPhoneNumber exception."""
        with pytest.raises(BritecoreError.InvalidPhoneNumber):
            raise BritecoreError.InvalidPhoneNumber("Invalid format")

    @pytest.mark.unit
    def test_invalid_email_address_exception(self):
        """Test InvalidEmailAddress exception."""
        with pytest.raises(BritecoreError.InvalidEmailAddress):
            raise BritecoreError.InvalidEmailAddress("Invalid email")

    @pytest.mark.unit
    def test_invalid_address_exception(self):
        """Test InvalidAddress exception."""
        with pytest.raises(BritecoreError.InvalidAddress):
            raise BritecoreError.InvalidAddress("Invalid address")

    @pytest.mark.unit
    def test_britecore_key_error_exception(self):
        """Test BritecoreKeyError exception."""
        with pytest.raises(BritecoreError.BritecoreKeyError):
            raise BritecoreError.BritecoreKeyError("Missing key")

    @pytest.mark.unit
    def test_no_site_error_exception(self):
        """Test NoSiteError exception."""
        with pytest.raises(BritecoreError.NoSiteError):
            raise BritecoreError.NoSiteError("No site specified")

    @pytest.mark.unit
    def test_missing_parameter_exception(self):
        """Test MissingParameter exception."""
        with pytest.raises(BritecoreError.MissingParameter):
            raise BritecoreError.MissingParameter("Required parameter missing")

    @pytest.mark.unit
    def test_conflicting_parameters_exception(self):
        """Test ConflictingParameters exception."""
        with pytest.raises(BritecoreError.ConflictingParameters):
            raise BritecoreError.ConflictingParameters("Multiple parameters specified")

    @pytest.mark.unit
    def test_all_sdk_exceptions_inherit_sdk_base(self):
        """All exposed custom exceptions should inherit BritecoreError.Base."""
        exception_types = (
            BritecoreError.NoDataReturned,
            BritecoreError.NoTokenReturned,
            BritecoreError.InvalidPhoneNumber,
            BritecoreError.InvalidEmailAddress,
            BritecoreError.InvalidAddress,
            BritecoreError.BritecoreKeyError,
            BritecoreError.NoSiteError,
            BritecoreError.MissingParameter,
            BritecoreError.ConflictingParameters,
            BritecoreError.AuthenticationError,
            BritecoreError.RateLimitError,
            BritecoreError.ServerError,
            BritecoreError.ValidationError,
            BritecoreError.NotFoundError,
            BritecoreError.ConflictError,
            BritecoreError.ConfigurationError,
            BritecoreError.RequestTimeoutError,
        )
        for exc_type in exception_types:
            assert issubclass(exc_type, BritecoreError.Base)

    @pytest.mark.unit
    def test_sdk_base_can_catch_specific_exceptions(self):
        """Consumers should be able to catch all SDK exceptions via one base class."""
        with pytest.raises(BritecoreError.Base):
            raise BritecoreError.NotFoundError("not found")

    @pytest.mark.unit
    def test_key_exception_subclasses_have_expected_inheritance(self):
        """Importer-facing exception aliases should keep stable inheritance contracts."""
        assert issubclass(BritecoreError.NotFoundError, BritecoreError.NoDataReturned)
        assert issubclass(BritecoreError.ConflictError, BritecoreError.NoDataReturned)
        assert issubclass(BritecoreError.ValidationError, BritecoreError.Base)

    @pytest.mark.unit
    def test_key_exception_subclasses_expose_message_field(self):
        """Importer-facing exception aliases should expose a stable `message` attribute."""
        exc = BritecoreError.NotFoundError("missing resource")
        assert exc.message == "missing resource"

        exc = BritecoreError.ValidationError("bad payload")
        assert exc.message == "bad payload"

        exc = BritecoreError.ConflictError("duplicate")
        assert exc.message == "duplicate"


class TestRequestContextOnExceptions:
    """Tests for request_id and sanitized_body fields on SDK exceptions."""

    # ------------------------------------------------------------------
    # BritecoreError.Base
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_base_has_request_id_field(self):
        """`Base` stores request_id when provided."""
        exc = BritecoreError.Base("msg", request_id="abc123")
        assert exc.request_id == "abc123"

    @pytest.mark.unit
    def test_base_request_id_defaults_none(self):
        """`Base` request_id defaults to None."""
        exc = BritecoreError.Base("msg")
        assert exc.request_id is None

    @pytest.mark.unit
    def test_base_has_sanitized_body_field(self):
        """`Base` stores sanitized_body when provided."""
        body = {"policy_number": "P123", "amount": 500}
        exc = BritecoreError.Base("msg", sanitized_body=body)
        assert exc.sanitized_body == body

    @pytest.mark.unit
    def test_base_sanitized_body_defaults_none(self):
        """`Base` sanitized_body defaults to None."""
        exc = BritecoreError.Base("msg")
        assert exc.sanitized_body is None

    # ------------------------------------------------------------------
    # NoDataReturned (and subclasses via inheritance)
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_no_data_returned_carries_request_id(self):
        exc = BritecoreError.NoDataReturned("error", request_id="req-001")
        assert exc.request_id == "req-001"

    @pytest.mark.unit
    def test_no_data_returned_str_includes_request_id(self):
        exc = BritecoreError.NoDataReturned("error", request_id="req-001")
        assert "req-001" in str(exc)
        assert "Request-ID" in str(exc)

    @pytest.mark.unit
    def test_no_data_returned_str_omits_request_id_when_none(self):
        exc = BritecoreError.NoDataReturned("error")
        assert "Request-ID" not in str(exc)

    @pytest.mark.unit
    def test_no_data_returned_carries_sanitized_body(self):
        body = {"name": "Alice", "api_key": "***redacted***"}
        exc = BritecoreError.NoDataReturned("error", sanitized_body=body)
        assert exc.sanitized_body == body

    @pytest.mark.unit
    def test_validation_error_inherits_request_id(self):
        exc = BritecoreError.ValidationError("bad input", request_id="v-99")
        assert exc.request_id == "v-99"
        assert "v-99" in str(exc)

    @pytest.mark.unit
    def test_not_found_error_inherits_sanitized_body(self):
        body = {"id": "999"}
        exc = BritecoreError.NotFoundError("not found", sanitized_body=body)
        assert exc.sanitized_body == body

    # ------------------------------------------------------------------
    # AuthenticationError
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_authentication_error_carries_request_id(self):
        exc = BritecoreError.AuthenticationError("unauth", request_id="auth-1")
        assert exc.request_id == "auth-1"
        assert "auth-1" in str(exc)

    @pytest.mark.unit
    def test_authentication_error_str_omits_request_id_when_none(self):
        exc = BritecoreError.AuthenticationError("unauth")
        assert "Request-ID" not in str(exc)

    @pytest.mark.unit
    def test_authentication_error_carries_sanitized_body(self):
        exc = BritecoreError.AuthenticationError("unauth", sanitized_body={"x": 1})
        assert exc.sanitized_body == {"x": 1}

    # ------------------------------------------------------------------
    # RateLimitError
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_rate_limit_error_carries_request_id(self):
        exc = BritecoreError.RateLimitError("too many", request_id="rl-7")
        assert exc.request_id == "rl-7"
        assert "rl-7" in str(exc)

    @pytest.mark.unit
    def test_rate_limit_error_str_omits_request_id_when_none(self):
        exc = BritecoreError.RateLimitError("too many")
        assert "Request-ID" not in str(exc)

    # ------------------------------------------------------------------
    # ServerError
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_server_error_carries_request_id(self):
        exc = BritecoreError.ServerError("500", request_id="srv-42")
        assert exc.request_id == "srv-42"
        assert "srv-42" in str(exc)

    @pytest.mark.unit
    def test_server_error_carries_sanitized_body(self):
        exc = BritecoreError.ServerError("500", sanitized_body={"k": "v"})
        assert exc.sanitized_body == {"k": "v"}

    # ------------------------------------------------------------------
    # RequestTimeoutError
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_request_timeout_error_carries_request_id(self):
        exc = BritecoreError.RequestTimeoutError("timed out", request_id="to-3")
        assert exc.request_id == "to-3"
        assert "to-3" in str(exc)

    @pytest.mark.unit
    def test_request_timeout_error_carries_sanitized_body(self):
        exc = BritecoreError.RequestTimeoutError("timed out", sanitized_body={"a": 1})
        assert exc.sanitized_body == {"a": 1}

    # ------------------------------------------------------------------
    # NoTokenReturned
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_no_token_returned_carries_request_id(self):
        exc = BritecoreError.NoTokenReturned("no token", request_id="tok-5")
        assert exc.request_id == "tok-5"
        assert "tok-5" in str(exc)

    # ------------------------------------------------------------------
    # Catch-all: simple Base subclasses still expose the fields
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_simple_subclass_exposes_request_id_field(self):
        """`BritecoreKeyError` inherits request_id/sanitized_body from Base."""
        exc = BritecoreError.BritecoreKeyError("missing key")
        assert exc.request_id is None
        assert exc.sanitized_body is None

    @pytest.mark.unit
    def test_sanitized_body_not_included_in_str_output(self):
        """sanitized_body is intentionally omitted from __str__ to avoid flooding logs."""
        body = {"field": "sensitive-looking-value"}
        exc = BritecoreError.NoDataReturned("error", sanitized_body=body)
        assert "sensitive-looking-value" not in str(exc)


class TestClassesModuleRemoval:
    """Tests for removed classes compatibility module."""

    @pytest.mark.unit
    def test_classes_import_raises_import_error(self):
        """Importing from classes raises ImportError with migration guidance."""
        import sys

        if "britecore_sdk.classes" in sys.modules:
            del sys.modules["britecore_sdk.classes"]

        with pytest.raises(ImportError, match="has been removed"):
            from britecore_sdk.classes import BritecoreContact  # noqa: F401

    @pytest.mark.unit
    def test_classes_import_error_mentions_replacement_modules(self):
        """Import error message points users to models/validators imports."""
        import sys

        if "britecore_sdk.classes" in sys.modules:
            del sys.modules["britecore_sdk.classes"]

        with pytest.raises(ImportError) as exc_info:
            from britecore_sdk.classes import BritecoreContact  # noqa: F401

        message = str(exc_info.value).lower()
        assert "models" in message
        assert "validators" in message
