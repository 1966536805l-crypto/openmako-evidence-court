# Expert Review Brief

Use this when asking an AI tooling maintainer, senior engineer, or open-source
reviewer to look at Evidence Court before sharing it.

## 30-Second Check

```bash
git clone https://github.com/1966536805l-crypto/openmako-evidence-court.git
cd openmako-evidence-court
python3 -m pip install .
mako evidence-court --demo bad-run
```

Expected public signal:

```text
Verdict: FAIL
```

The bad demo is intentionally simple: the supplied run record says the agent
fixed a calculator bug and tests pass, but the record also shows a protected
test edit and no reported required pytest command.

## Safe Quote

```text
OpenMako Evidence Court is a small claim-vs-evidence gate for supplied
coding-agent run records. Its v0.1 demo catches a bad run that claims tests
passed even though the supplied record lacks the required test command.
```

## Evidence To Check Before Sharing

- `README.md` shows the bad-run demo above the install path.
- `examples/evidence-court/bad-run.json` is the supplied failing run record.
- `docs/PUBLIC_PROOF.md` binds the shared claim to the tag, commit, smoke run,
  and artifact digest.
- `bash scripts/evidence_court_smoke.sh` runs the local smoke gate.
- GitHub Actions `Evidence Court Smoke` is green for the commit being shared.
- `docs/LAUNCH_POST.md` states the native-ingestion boundary.

## Do Not Share If

- The GitHub Actions smoke gate is red for the commit being shared.
- The post says native Claude/Codex/Cursor/Devin/CI log ingestion is supported.
- The post says Evidence Court proves tests really ran outside the supplied
  record.
- The post implies the broader OpenMako agent runtime ships in this public repo.

## Boundary

Evidence Court v0.1 audits supplied JSON run records, explicit marked transcript
v0 files, and explicit Evidence Court JSONL event streams. It does not natively
ingest vendor logs. It does not provide proof that tests actually ran outside the
supplied record.
