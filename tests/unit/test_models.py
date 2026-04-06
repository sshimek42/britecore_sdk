"""Tests for domain models."""

import pytest

from britecore_libraries.models import BritecoreContact, BritecorePolicy, BritecoreQuote


class TestBritecoreContact:
    """Tests for BritecoreContact model."""

    @pytest.mark.unit
    def test_contact_init_individual(self):
        """Test creating an individual contact."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        }

        contact = BritecoreContact(
            name="John Doe",
            address=address,
            contact_type="individual",
        )

        assert contact.name == "John Doe"
        assert contact.contact_type == "individual"
        assert contact.address == address

    @pytest.mark.unit
    def test_contact_init_organization(self):
        """Test creating an organization contact."""
        address = {
            "street": "456 Business Ave",
            "city": "Chicago",
            "state": "IL",
            "zip": "60601",
        }

        contact = BritecoreContact(
            name="Acme Corp",
            address=address,
            contact_type="organization",
        )

        assert contact.name == "Acme Corp"
        assert contact.contact_type == "organization"

    @pytest.mark.unit
    def test_contact_with_phone_and_email(self):
        """Test contact with phone and email."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        }
        phone = [{"phone": "5551234567", "type": "Home"}]
        email = [{"email": "john@example.com", "type": "Home"}]

        contact = BritecoreContact(
            name="John Doe",
            address=address,
            phone_number=phone,
            email=email,
        )

        assert contact.phone_number == phone
        assert contact.email == email

    @pytest.mark.unit
    def test_contact_process_contact(self):
        """Test contact processing."""
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
        }

        contact = BritecoreContact(
            name="John Doe",
            address=address,
            policy_number="POL001",
        )

        result = contact.process_contact()

        assert "name" in result
        assert "addresses" in result
        assert "phones" in result
        assert "emails" in result
        assert result["policy_number"] == "POL001"


class TestBritecorePolicy:
    """Tests for BritecorePolicy model."""

    @pytest.mark.unit
    def test_policy_init(self):
        """Test creating a policy."""
        from datetime import datetime

        contacts = []

        policy = BritecorePolicy(
            policy_number="POL001",
            contacts=contacts,
            effective_date=datetime.now(),
            policy_type_id="type_1",
        )

        assert policy.policy_number == "POL001"
        assert policy.policy_type_id == "type_1"
        assert policy.contacts == contacts

    @pytest.mark.unit
    def test_policy_defaults(self):
        """Test policy default values."""
        from datetime import datetime

        policy = BritecorePolicy(
            policy_number="POL001",
            contacts=[],
            effective_date=datetime.now(),
            policy_type_id="type_1",
        )

        assert policy.term_type == "1 Year"
        assert policy.renewal_term_type == "1 Year"
        assert policy.is_renewal is True
        assert policy.as_agent is False
        assert policy.manual_policy_number is True

    @pytest.mark.unit
    def test_policy_to_dict(self):
        """Test converting policy to dictionary."""
        from datetime import datetime

        policy = BritecorePolicy(
            policy_number="POL001",
            contacts=[],
            effective_date=datetime.now(),
            policy_type_id="type_1",
        )

        result = policy.to_dict()

        assert isinstance(result, dict)
        assert "policy_number" in result
        assert result["policy_number"] == "POL001"


class TestBritecoreQuote:
    """Tests for BritecoreQuote model."""

    @pytest.mark.unit
    def test_quote_init(self):
        """Test creating a quote."""
        quote = BritecoreQuote(
            number="Q001",
            policy_type_id="type_1",
            agency_id="agency_1",
            named_insureds=["John Doe"],
            risks=["Building"],
        )

        assert quote.number == "Q001"
        assert quote.policy_type_id == "type_1"
        assert quote.agency_id == "agency_1"

    @pytest.mark.unit
    def test_quote_defaults(self):
        """Test quote default values."""
        quote = BritecoreQuote(
            number="Q001",
            policy_type_id="type_1",
            agency_id="agency_1",
            named_insureds=["John Doe"],
            risks=["Building"],
        )

        assert quote.number_origin == "manual"
        assert quote.transaction_type == "renewal"
        assert quote.term_type == "1 Year"
        assert quote.underwriting_questions == []

    @pytest.mark.unit
    def test_quote_to_dict(self):
        """Test converting quote to dictionary."""
        quote = BritecoreQuote(
            number="Q001",
            policy_type_id="type_1",
            agency_id="agency_1",
            named_insureds=["John Doe"],
            risks=["Building"],
        )

        result = quote.to_dict()

        assert isinstance(result, dict)
        assert "number" in result
        assert "description" in result  # Should be auto-generated

    @pytest.mark.unit
    def test_quote_to_dict_removes_empty_dates(self):
        """Test that empty date fields are removed from dict."""
        quote = BritecoreQuote(
            number="Q001",
            policy_type_id="type_1",
            agency_id="agency_1",
            named_insureds=["John Doe"],
            risks=["Building"],
            next_inspection_date=None,
            previous_inspection_date=None,
        )

        result = quote.to_dict()

        assert "next_inspection_date" not in result
        assert "previous_inspection_date" not in result
