"""Tests for exceptions and strict import behavior."""

import pytest

from britecore_libraries.exceptions import BritecoreError


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


class TestClassesModuleRemoval:
    """Tests for removed classes compatibility module."""

    @pytest.mark.unit
    def test_classes_import_raises_import_error(self):
        """Importing from classes raises ImportError with migration guidance."""
        import sys

        if "britecore_libraries.classes" in sys.modules:
            del sys.modules["britecore_libraries.classes"]

        with pytest.raises(ImportError, match="has been removed"):
            from britecore_libraries.classes import BritecoreContact  # noqa: F401

    @pytest.mark.unit
    def test_classes_import_error_mentions_replacement_modules(self):
        """Import error message points users to models/validators imports."""
        import sys

        if "britecore_libraries.classes" in sys.modules:
            del sys.modules["britecore_libraries.classes"]

        with pytest.raises(ImportError) as exc_info:
            from britecore_libraries.classes import BritecoreContact  # noqa: F401

        message = str(exc_info.value).lower()
        assert "models" in message
        assert "validators" in message
