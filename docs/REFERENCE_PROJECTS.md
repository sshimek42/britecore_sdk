# Reference Projects

This page tracks external SDKs and generator projects worth referencing while evolving `britecore_sdk`.

## Why These Projects

The insurance-specific open-source Python SDK landscape appears limited, so this list focuses on mature Python API SDKs with strong patterns for:

- API ergonomics
- auth handling
- release/versioning discipline
- documentation quality
- generated-code boundaries

## Recommended References

### 1) `stripe/stripe-python`

- **Repo:** <https://github.com/stripe/stripe-python>
- **Why it is relevant:** High-quality Python SDK design with strong API lifecycle discipline.
- **Patterns to borrow:**
  - Clear exception taxonomy and actionable errors
  - Predictable request/response surface
  - Strong release/versioning practices

### 2) `slackapi/python-slack-sdk`

- **Repo:** <https://github.com/slackapi/python-slack-sdk>
- **Why it is relevant:** Excellent documentation and developer experience at scale.
- **Patterns to borrow:**
  - Practical docs layout for large API surfaces
  - Discoverable examples and migration guidance
  - Sync/async usability patterns

### 3) `twilio/twilio-python`

- **Repo:** <https://github.com/twilio/twilio-python>
- **Why it is relevant:** Long-running SDK with broad endpoint surface and stable packaging.
- **Patterns to borrow:**
  - Module organization for large service domains
  - Backward-compatible evolution strategy
  - Operationally stable publishing conventions

### 4) `sendgrid/sendgrid-python`

- **Repo:** <https://github.com/sendgrid/sendgrid-python>
- **Why it is relevant:** Focused API library with straightforward onboarding.
- **Patterns to borrow:**
  - Clear quick-start patterns
  - Simpler client setup narratives
  - Maintainable docs-to-code consistency

### 5) `plaid/plaid-python`

- **Repo:** <https://github.com/plaid/plaid-python>
- **Why it is relevant:** Fintech API SDK with strong auth and typed client usage patterns.
- **Patterns to borrow:**
  - Typed request/response ergonomics
  - Auth and configuration clarity
  - Useful client initialization defaults

## Generator and Spec Tooling References

### 6) `openapi-generators/openapi-python-client`

- **Repo:** <https://github.com/openapi-generators/openapi-python-client>
- **Why it is relevant:** Modern Python client generation patterns.
- **Patterns to borrow:**
  - Generated code structure and naming conventions
  - Type-hint strategy for generated clients
  - Template customization boundaries

### 7) `OpenAPITools/openapi-generator`

- **Repo:** <https://github.com/OpenAPITools/openapi-generator>
- **Why it is relevant:** Industry-standard generation ecosystem.
- **Patterns to borrow:**
  - End-to-end spec-driven workflows
  - CI integration for regeneration checks
  - Multi-language consistency principles that still improve Python DX

## Mapping to `britecore_sdk` Roadmap

These references map well to current SDK priorities:

- **Error and response UX:** Stripe, Plaid
- **Docs and examples UX:** Slack, SendGrid
- **Large surface maintainability:** Twilio
- **Spec-aligned generation strategy:** OpenAPI Generator, openapi-python-client

## Notes

- This list is intentionally practical and small.
- Prefer borrowing patterns, not implementation details.
- Revisit quarterly as the Python SDK ecosystem evolves.
