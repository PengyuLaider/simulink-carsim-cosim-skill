# Packaging and public delivery

## Runtime package

Preserve a working layout. Provide a clear public entry point, model(s), necessary source, configuration and redistributable data, test entry, and a short run note. Keep probes/caches outside the runtime root. Preserve rollback and useful original failures.

Find installations at the destination; do not bake developer drive letters into the package. Test binary and solver compatibility. Verify whether the chosen export is self-contained or still references a local vendor database. Document the actual import/editing workflow instead of promising every PAR/CPAR is portable.

Extract a reviewed package into a fresh location. Check file identity, public entry, version, source resolution and native interface. Run a representative bounded closed loop when software/license access permits it. Report compilation-only checks separately. Passing on one computer does not establish compatibility everywhere.

## Public Skill repository

Publish original instructions, helpers, templates and anonymized explanations. Do not bundle the original project, chat transcript, user-session logs, vehicle exports, vendor examples, installers, license files, MEX or solver DLLs by default. Establish redistribution rights separately; creating/exporting a file locally does not establish them.

Inspect tracked and untracked upload candidates for credentials, private paths and proprietary content. A `.gitignore` does not remove tracked secrets or prevent a manual browser upload. Build the public ZIP from a reviewed file list and verify its contents.

The user supplies locally licensed simulation software. Do not demand API tokens or weaken security just to use this Skill. Report unavailable capabilities without substituting a fake native result.

## Source fingerprint helper

Python 3.10 or newer; no third-party packages:

```text
python fingerprint.py snapshot --root PROJECT --include models --include src --include config --out EVIDENCE/source-before.json
python fingerprint.py verify --root PROJECT --manifest EVIDENCE/source-before.json
```

Replace relative selections with the actual necessary files. Include configuration, vehicle input and referenced dependencies deliberately; dependencies outside the root need another reviewed root/manifest. Missing, empty, symlink and Windows reparse-point selections are rejected. The manifest cannot be inside selected source directories. Freeze source writes during hashing; this helper does not provide an atomic filesystem snapshot.

Verification checks added, removed and changed files inside the original selections. Exit codes: 0 match/snapshot created, 1 drift, 2 invalid input. This detects local drift; it is not a signature system, tamper-proof provenance or a validator of physical metrics.
