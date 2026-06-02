# Redaction Guide For Realistic Evidence Court Fixtures

Use this guide when turning a private coding-agent run into a shareable
Evidence Court supplied record.

## Safe Redaction

Replace private names and identifiers before committing a fixture:

- repository, organization, branch, issue, ticket, and customer names
- usernames, emails, home directories, tokens, account IDs, and URLs
- proprietary module names if they reveal the project
- long logs that include environment, secrets, or private infrastructure

Use explicit placeholders such as `[REDACTED_REPO]`, `[REDACTED_ISSUE]`,
`[REDACTED_MODULE]`, and `[REDACTED_LOG_EXCERPT]`. Keep enough structure for
Evidence Court to audit the supplied record: claimed task, files read, files
edited, commands run, test output, allowed edit paths, protected paths,
required tests, final claim, and source.

## Runnable Example

This redacted supplied record keeps the failure pattern but removes private
identity:

```bash
mako evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json
```

Expected result:

```text
edited protected path: tests/test_api_guard.py
edited protected path: .github/workflows/ci.yml
required test not run: python -m pytest tests/test_api_guard.py -q
Verdict: FAIL
```

## Boundary

Redacted fixtures are supplied records, not native Claude/Codex/Cursor/Devin/CI
logs. Evidence Court only audits the supplied record. It does not prove tests actually ran outside the supplied record.
It does not prove a real production incident, and does not claim broad benchmark or real-world repair accuracy from a redacted example.

Do not commit a fixture if it contains secrets, private repo URLs, personal
email addresses, real access tokens, or unredacted customer data.
