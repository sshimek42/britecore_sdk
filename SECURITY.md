# Security Policy

*Last updated: April 6, 2026*

This document describes how `britecore_libraries` handles security vulnerabilities and the expectations for reporting and patching.

## Reporting a Vulnerability

If you discover a security vulnerability, **please do NOT open a public GitHub issue**. Instead:

### Step 1: Contact the maintainers privately

Send an email to: **[security@example.com](mailto:security@example.com)**  
(Contact: Repository owner via GitHub)

Include:

- **Vulnerability description** — Clear explanation of the issue
- **Affected version(s)** — Which version(s) of the package are vulnerable
- **Proof of concept** — Minimal example that demonstrates the issue
- **Impact** — Potential harm (e.g., unauthorized API access, data exposure)
- **Suggested fix** (optional)

### Step 2: Wait for acknowledgment

- We will acknowledge receipt within **48 hours**
- We will provide an estimated timeline for patching
- We will keep you updated on progress

### Step 3: Responsible disclosure

- We will work to fix the vulnerability before public disclosure
- We will credit you in the release notes (unless you prefer anonymity)
- We ask that you do not disclose publicly until we have released a patch

## Patching Timeline

### Critical severity (e.g., authentication bypass, data leak)

- **Target patch release** — Within 7 days
- **Severity level** — Immediate action
- **Minimum notice** — All supported versions patched; advisory issued

### High severity (e.g., denial of service, privilege escalation)

- **Target patch release** — Within 14 days
- **Severity level** — High priority
- **Minimum notice** — Patched in next release

### Medium severity (e.g., API key exposure in logs, unvalidated input)

- **Target patch release** — Within 30 days
- **Severity level** — Regular priority
- **Minimum notice** — Next minor release

### Low severity (e.g., deprecated crypto, missing deprecation warnings)

- **Target patch release** — Next scheduled release
- **Severity level** — Normal priority
- **Minimum notice** — Included in next release notes

## Supported Versions

Security patches are provided for:

| Version | Status | Support Ends |
|---------|--------|--------------|
| 1.x | Active | October 2025 (12 months from 1.0.0) |
| 0.x | Deprecated | No new patches |

- **Active versions** — All security patches
- **Deprecated versions** — Critical security issues only (at maintainers' discretion)

## Security Best Practices

### For Users

1. **Keep dependencies up to date**

   ```powershell

   pip install --upgrade britecore_libraries

   ```

2. **Never commit `.secrets.toml`**
   - File is gitignored; verify before committing
   - Regenerate credentials if accidentally exposed

3. **Use environment variables for secrets**

   ```powershell

   $env:BRITECORE_LIBRARIES_API_KEY = "your_key_here"

   ```

4. **Report suspected vulnerabilities privately**
   - Don't post credentials or API keys to issues
   - Use private security contacts

### For Contributors

1. **Code review**
   - All changes reviewed before merge
   - Security-sensitive code gets extra scrutiny

2. **Dependency updates**
   - Regular updates to dependencies
   - CVE scanning via Dependabot

3. **No hardcoded secrets**
   - All credentials externalized
   - `.secrets.toml` is gitignored

4. **Input validation**
   - API inputs validated before use
   - Error messages don't leak sensitive info

## Known Vulnerabilities

As of April 6, 2026: **None known**

See `CHANGELOG.md` for list of resolved security issues.

## Security Features

This SDK includes:

✅ **Lazy initialization** — Avoids import-time failures if config is missing  
✅ **OAuth token refresh** — Automatic expiration handling  
✅ **API key + OAuth support** — Flexible auth modes  
✅ **Config validation** — Required keys checked before use  
✅ **Error masking** — Sensitive data redacted from error messages  
✅ **Type hints** — Helps catch misuse at type-check time  
✅ **Dependency scanning** — DeepSource + Dependabot  
✅ **Secrets detection** — DeepSource flags credential-like patterns  

## CVE Disclosure

Security vulnerabilities follow [CVE](https://www.cve.org/) guidelines:

- **Disclosure timeline** — Coordinated disclosure (not responsible; see Patching Timeline above)
- **CVE numbering** — Requested for critical/high severity issues
- **Advisory** — Published with release notes and patch instructions

## Questions?

For security concerns or questions about this policy:
- Email security contact (see above)
- Do not open public issues for suspected vulnerabilities
- See [STABILITY.md](STABILITY.md) for other support channels

---

**Last reviewed:** April 6, 2026
**Next review:** October 2026 (after first public release)
