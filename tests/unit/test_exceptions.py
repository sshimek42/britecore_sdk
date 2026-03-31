"""Tests for exceptions and deprecation warnings."""

import warnings

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


class TestDeprecationWarnings:
    """Tests for deprecation warnings."""

    @pytest.mark.unit
    def test_classes_import_raises_deprecation_warning(self):
        """Test that importing from classes raises DeprecationWarning."""
        # Reset the module to catch the warning
        import sys
        if "britecore_libraries.classes" in sys.modules:
            del sys.modules["britecore_libraries.classes"]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from britecore_libraries.classes import BritecoreContact  # noqa: F401
            
            # Check that a deprecation warning was raised
            assert len(w) >= 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "deprecated" in str(w[-1].message).lower()

    @pytest.mark.unit
    def test_classes_backward_compatibility(self):
        """Test that deprecated classes are still functional."""
        import sys
        if "britecore_libraries.classes" in sys.modules:
            del sys.modules["britecore_libraries.classes"]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            from britecore_libraries.classes import (
                BritecoreAddress,
                BritecoreContact,
                BritecoreEmail,
                BritecoreError,
                BritecorePhone,
                BritecorePolicy,
            )
            
            # Verify the classes are accessible
            assert BritecoreContact is not None
            assert BritecorePolicy is not None
            assert BritecoreAddress is not None
            assert BritecoreEmail is not None
            assert BritecorePhone is not None
            assert BritecoreError is not None

