# Documentation Build Troubleshooting

*Last updated: July 22, 2026*
*Document type: Developer guide*

For developers working on SDK documentation: understand common Sphinx/MyST build errors and how to fix them.

---

## Quick diagnostic checklist

Before pushing documentation changes:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# One-command docs QA (strict HTML + linkcheck)
python scripts/docs_qa.py

# Test 1: Run full pre-commit suite (runs locally before commits)
pre-commit run --all-files

# Test 2: Build documentation in strict mode (matches RTD)
python -m sphinx -W --keep-going -b html ./docs ./docs/_build/html-strict

# Test 3: Check markdown syntax
pymarkdown --config .pymarkdown scan README.md GETTING_STARTED.md

# Test 4: Quick validation of key files
python src/britecore_sdk/utils/check_markdown_structure.py

# Test 5: Validate links across all documentation pages
python -m sphinx -b linkcheck ./docs ./docs/_build/linkcheck
```

If all tests pass, your changes are ready to commit and push.

---

## Common documentation build errors

### Error: "adjacent transitions are not allowed"

**Cause:** Two or more `---` (docutils transition markers) are adjacent with no content between them.

**Example (❌ WRONG):**
```markdown
Some paragraph.

---

---

Next section.
```

**Fix:**
```markdown
Some paragraph.

---

Next section.
```

**Prevention:**
- Review markdown structure visually — each `---` should have content both before and after it
- Run Sphinx build locally before committing: `python -m sphinx -W --keep-going -b html ./docs ./docs/_build/html-strict`

---

### Error: "Unknown substitution referenced"

**Cause:** Reference to a MyST substitution that isn't defined in `docs/conf.py`.

**Example (❌ WRONG):**
```markdown
Built on {{ unknown_substitution }}
```

**Fix:**
Add the substitution to `docs/conf.py`:
```python
myst_substitutions = {
    "docs_version": release,
    "unknown_substitution": "value",  # ← Add here
}
```

**Prevention:**
- Only use substitutions defined in `docs/conf.py`
- Current substitutions: `docs_version`, `docs_commit`, `docs_commit_date`, `docs_build_date`

---

### Error: "Inline code cannot contain MyST substitutions"

**Cause:** MyST substitutions don't expand inside backtick inline code spans.

**Example (❌ WRONG):**
```markdown
See `{{ docs_commit }}`
```

**Fix (bare text or separate from code):**
```markdown
See {{ docs_commit }}

Or in code blocks:
\`\`\`
commit: {{ docs_commit }}
\`\`\`
```

**Prevention:**
- Never wrap MyST substitutions in backticks
- Keep substitutions as bare text or inside code fences, not inline code

---

### Error: "Incomplete markup constructs"

**Cause:** Markdown table syntax is malformed or incomplete.

**Example (❌ WRONG):**
```markdown
| Column 1 | Column 2
| --- | ---
| Value 1 | Value 2
```

**Fix:**
```markdown
| Column 1 | Column 2 |
| --- | --- |
| Value 1 | Value 2 |
```

**Prevention:**
- All table rows must have the same number of columns
- Closing `|` is required on each row
- Test markdown syntax with: `pymarkdown --config .pymarkdown scan FILENAME.md`

---

### Error: "Unknown role/directive"

**Cause:** Using a Sphinx directive or role that isn't enabled or recognized.

**Example (❌ WRONG):**
```markdown
:::{unknown-directive}
Content
:::
```

**Fix:**
Check if the directive is:
1. **Built-in:** Use correct syntax (e.g., `note`, `warning`, `code-block`)
2. **Extension-based:** Verify extension is loaded in `docs/conf.py`
3. **Custom:** Define in `docs/conf.py` or use existing ones

**Prevention:**
- Check `.rst`/MyST documentation for valid directives
- Verify extensions in `docs/conf.py`: `extensions = [...]`

---

### Error: "Document title underline too short/too long"

**Cause:** RST title underlines don't match the title length.

**Example (❌ WRONG):**
```markdown
# Main Title
===
```

**Fix:**
```markdown
# Main Title
=============
```

Or use markdown-style headings in `.md` files (MyST handles this automatically):
```markdown
# Main Title

## Subsection
```

**Prevention:**
- Use markdown heading syntax (`#`, `##`) in `.md` files
- MyST converts these properly to RST for Sphinx

---

## Prevention: Git hooks and pre-commit

### Enable pre-commit hooks

Pre-commit hooks automatically validate your changes before committing:

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks from config
pre-commit install

# (Optional) Test hooks on all files
pre-commit run --all-files
```

### What the hooks check

1. **markdown-structure** — Python-based markdown validation
2. **pymarkdown** — Markdown linting (MD001-MD047 rules)
3. **sphinx-build** — Full documentation build with `-W` (treat warnings as errors)
4. **ruff + black** — Code formatting and linting
5. **mypy** — Type checking
6. **pytest-unit** — Quick unit test smoke check

### Bypassing hooks (not recommended)

```bash
# Skip all pre-commit checks for one commit
git commit --no-verify

# Run specific hook manually to debug
pre-commit run sphinx-build --verbose
```

---

## Best practices for documentation changes

1. **Make incremental changes** — Edit one section at a time, test with Sphinx build after each section.

2. **Validate before committing** — Run full pre-commit suite locally:
   ```bash
   pre-commit run --all-files
   ```

3. **Structure matters** — Review markdown structure visually:
   - Headings are hierarchical (`#`, `##`, `###`)
   - Transitions (`---`) have content before and after
   - Tables have matching column counts
   - Code blocks are properly closed

4. **Test locally = test in CI** — If it passes locally, it passes CI:
   - CI runs the same pre-commit hooks
   - CI runs Sphinx with the same flags (`-W --keep-going`)

5. **Use examples from working files** — Copy patterns from:
   - `README.md` — top-level documentation
   - `GETTING_STARTED.md` — guide-style documentation
   - `docs/ASYNC_CACHING.md` — detailed technical documentation

6. **Document your assumptions** — If adding new substitutions, integration points, or event types, update this file too.

---

## Running pre-commit in different scenarios

### Before commit (automatic if hooks installed)

```bash
git commit -m "message"
# pre-commit runs automatically
```

### Before push (also automatic)

```bash
git push origin master
# pre-commit run --hook-stage pre-push runs (release compliance check)
```

### Manual validation (for debugging)

```bash
# Check all files
pre-commit run --all-files

# Check specific hook
pre-commit run sphinx-build --all-files

# Dry-run to see what would change
pre-commit run --all-files --verbose
```

### In CI/GitHub Actions

```bash
# Runs the same as local: --all-files by default
python -m pre_commit run --all-files
```

---

## Related documentation

- Main documentation: `docs/`
- Configuration: `docs/conf.py`
- Pre-commit config: `.pre-commit-config.yaml`
- Git hooks: `.githooks/`
- Sphinx documentation: https://www.sphinx-doc.org/
- MyST documentation: https://myst-parser.readthedocs.io/
