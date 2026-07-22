"""
Example: Complete API Usage from Start to Finish

This example demonstrates:
- Configuration setup
- Client initialization
- Creating and managing policies
- Error handling
- Cleanup

Run this after setting up ~/.britecore/.secrets.toml
"""

import logging
from britecore_sdk import configure_logging
from britecore_sdk.api.api_calls import get_api_client, init_api_client
from britecore_sdk.api.api_calls.v2 import policies, contacts, quotes
from britecore_sdk.models import BritecoreContact
from britecore_sdk.exceptions import NotFoundError, ValidationError, AuthenticationError


def setup_logging():
    """Configure SDK logging for debugging."""
    configure_logging(level=logging.INFO)
    logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)


def main():
    """Main workflow."""
    print("BriteCore SDK - Complete Example\n" + "=" * 40)

    # 1. Setup logging
    setup_logging()

    # 2. Initialize client (lazy load)
    print("\n1. Initializing API client...")
    try:
        client = get_api_client()
        print("✓ Client initialized successfully")
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        return
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return

    # 3. Retrieve existing policy
    print("\n2. Retrieving existing policy...")
    try:
        policy_number = "POL-001"  # Replace with real policy
        policy = policies.retrieve_policy(policy_number=policy_number)
        print(f"✓ Policy retrieved: {policy_number}")
        print(f"  Status: {policy.get('status')}")
        print(f"  Insured: {policy.get('insured_name')}")
    except NotFoundError:
        print(f"✗ Policy {policy_number} not found")
        policy = None
    except Exception as e:
        print(f"✗ Error retrieving policy: {e}")
        policy = None

    # 4. Create a new contact
    print("\n3. Creating new contact...")
    try:
        contact_data = {
            "name": "Jane Smith",
            "email": [
                {
                    "email": "jane.smith@example.com",
                    "type": "Work"
                }
            ],
            "phone": [
                {
                    "phone": "555-123-4567",
                    "type": "Mobile"
                }
            ]
        }

        # Validate contact
        contact = BritecoreContact(**contact_data)
        validated_contact = contact.process_contact()

        # Create contact
        response = contacts.new_contact(contact=validated_contact)
        contact_id = response.get("data", {}).get("contact_id")
        print(f"✓ Contact created: {contact_id}")

    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    except Exception as e:
        print(f"✗ Error creating contact: {e}")

    # 5. List contacts (if available)
    print("\n4. Listing contacts...")
    try:
        contacts_list = contacts.list_contacts(limit=10)
        contact_count = len(contacts_list.get("data", []))
        print(f"✓ Found {contact_count} contacts")
    except Exception as e:
        print(f"✗ Error listing contacts: {e}")

    # 6. Test quote creation (dry-run for safety)
    print("\n5. Testing quote creation (dry-run)...")
    try:
        init_api_client("production", client_dry_run=True)
        quote_data = {
            "insured_name": "Test Business",
            "policy_type": "Commercial"
        }
        # This won't actually create anything, just shows the request
        response = quotes.create_quote(**quote_data)
        if response.get("dry_run"):
            print("✓ Quote request prepared (dry-run mode)")
            print(f"  Would POST to: {response.get('prepared_url', 'N/A')}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # 7. Summary
    print("\n" + "=" * 40)
    print("Example complete!")
    print("\nNext steps:")
    print("- Update configuration in ~/.britecore/.secrets.toml")
    print("- Remove dry_run=True to make real API calls")
    print("- Add your own policy numbers and data")
    print("- See docs/COMMON_PATTERNS.md for more examples")


if __name__ == "__main__":
    main()

