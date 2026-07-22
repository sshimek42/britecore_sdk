"""
Example: Advanced Error Handling and Recovery

This example demonstrates:
- Comprehensive exception handling
- Retry logic for transient failures
- Fallback strategies
- Error logging and reporting
"""

import time
import logging
from typing import Optional, Dict, Any
from britecore_sdk.api.api_calls.v2 import policies, quotes
from britecore_sdk.exceptions import (
    NotFoundError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    BritecoreError
)

logger = logging.getLogger(__name__)


class APIWithRetry:
    """Wrapper for API calls with retry and recovery logic."""
    
    def __init__(self, max_retries: int = 3, base_backoff: float = 1.0):
        self.max_retries = max_retries
        self.base_backoff = base_backoff
    
    def retrieve_policy_with_fallback(
        self,
        policy_number: Optional[str] = None,
        policy_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve policy with multiple fallback strategies.
        
        Attempts in order:
        1. Try by policy number (if provided)
        2. Try by policy ID (if provided)
        3. Return None if both fail
        """
        # Strategy 1: Try by policy number
        if policy_number:
            try:
                return self._retrieve_with_retry(
                    lambda: policies.retrieve_policy(policy_number=policy_number),
                    f"Policy {policy_number}"
                )
            except NotFoundError:
                logger.info(f"Policy {policy_number} not found by number, trying ID...")
        
        # Strategy 2: Try by policy ID
        if policy_id:
            try:
                return self._retrieve_with_retry(
                    lambda: policies.retrieve_policy(policy_id=policy_id),
                    f"Policy {policy_id}"
                )
            except NotFoundError:
                logger.warning(f"Policy {policy_id} not found by ID either")
        
        return None
    
    def _retrieve_with_retry(self, func, description: str) -> Dict[str, Any]:
        """Execute function with exponential backoff retry."""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func()
                if attempt > 0:
                    logger.info(f"✓ {description} retrieved after {attempt + 1} attempts")
                return result
            
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries:
                    backoff = self.base_backoff * (2 ** attempt)
                    logger.warning(
                        f"Rate limited on {description}, "
                        f"backing off {backoff}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(backoff)
                else:
                    logger.error(f"Failed {description} after {self.max_retries} retries")
                    raise
            
            except AuthenticationError as e:
                # Authentication errors shouldn't be retried
                logger.error(f"Authentication failed for {description}: {e}")
                raise
            
            except ValidationError as e:
                # Validation errors shouldn't be retried
                logger.error(f"Validation error for {description}: {e}")
                raise
            
            except Exception as e:
                # Other errors might be transient
                last_error = e
                if attempt < self.max_retries:
                    backoff = self.base_backoff * (2 ** attempt)
                    logger.warning(
                        f"Error retrieving {description}: {e}, "
                        f"retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                else:
                    logger.error(f"Failed {description} after {self.max_retries} retries")
                    raise


def create_quotes_with_error_collection(
    quote_list: list[Dict[str, Any]],
    retry_handler: APIWithRetry
) -> Dict[str, Any]:
    """
    Create multiple quotes and collect errors.
    
    Returns:
        {
            "succeeded": [...],
            "failed": [...],
            "errors_summary": {...}
        }
    """
    results = {
        "succeeded": [],
        "failed": [],
        "errors_summary": {}
    }
    
    for idx, quote_data in enumerate(quote_list):
        try:
            result = quotes.create_quote(**quote_data)
            quote_id = result.get("data", {}).get("quote_id")
            
            results["succeeded"].append({
                "index": idx,
                "quote_id": quote_id,
                "insured": quote_data.get("insured_name")
            })
            logger.info(f"✓ Created quote {quote_id}")
            
        except ValidationError as e:
            results["failed"].append({
                "index": idx,
                "error": str(e),
                "type": "validation"
            })
            error_key = "validation_errors"
            results["errors_summary"][error_key] = \
                results["errors_summary"].get(error_key, 0) + 1
            logger.error(f"✗ Validation error for quote {idx}: {e}")
        
        except RateLimitError as e:
            results["failed"].append({
                "index": idx,
                "error": str(e),
                "type": "rate_limited"
            })
            error_key = "rate_limit_errors"
            results["errors_summary"][error_key] = \
                results["errors_summary"].get(error_key, 0) + 1
            logger.error(f"✗ Rate limited on quote {idx}")
        
        except BritecoreError.Base as e:
            results["failed"].append({
                "index": idx,
                "error": str(e),
                "type": "api_error"
            })
            error_key = "api_errors"
            results["errors_summary"][error_key] = \
                results["errors_summary"].get(error_key, 0) + 1
            logger.error(f"✗ API error for quote {idx}: {e}")
    
    return results


def main():
    """Example usage of error handling."""
    logging.basicConfig(level=logging.INFO)
    
    print("Advanced Error Handling Example\n" + "=" * 50)
    
    # Initialize retry handler
    handler = APIWithRetry(max_retries=3, base_backoff=1.0)
    
    # Example 1: Policy lookup with fallback
    print("\n1. Policy lookup with fallback...")
    policy = handler.retrieve_policy_with_fallback(
        policy_number="POL-123-456",
        policy_id="12345"
    )
    if policy:
        print(f"✓ Found policy: {policy.get('policy_number')}")
    else:
        print("✗ Policy not found with any method")
    
    # Example 2: Quote creation with error collection
    print("\n2. Batch quote creation with error handling...")
    quotes_to_create = [
        {"insured_name": "Business A", "policy_type": "Commercial"},
        {"insured_name": "Business B", "policy_type": "General"},
        # This one will fail validation
        {"insured_name": "", "policy_type": "Invalid"},
    ]
    
    result = create_quotes_with_error_collection(quotes_to_create, handler)
    print(f"\nResults:")
    print(f"  Succeeded: {len(result['succeeded'])}")
    print(f"  Failed: {len(result['failed'])}")
    print(f"  Errors: {result['errors_summary']}")


if __name__ == "__main__":
    main()

