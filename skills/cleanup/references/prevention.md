# Prevention branch

Read the selected project's launch scripts, effective Compose configuration, check commands, hooks and CI before proposing a change. An existing check that is unwired or bypassed is the defect; reuse it. Apply changes only when prevention is requested. A cleanup run may report the recommendation without editing another project's infrastructure.

## Lifecycle contract

For temporary environments, give each run a unique Compose project and explicit owner, purpose and run ID. Use `restart: "no"`; persistent services may legitimately need restart policies. Define log rotation at container creation. Existing containers keep their old logging settings until recreated. Establish expiry and retention with the team; an expiry label alone never proves inactivity.

Wrap startup and test execution in a `try/finally` (PowerShell/Python) or an exit/signal trap (shell). The finalizer must use the same exact project and Compose files as startup. Preserve the original test exit code and report teardown failure too. Teardown persistent data only when that run created it as disposable. A killed runner can bypass finalizers; a separate stale-run audit must check owner/liveness before cleanup.

CI's unconditional teardown should cover failed and cancelled jobs as far as its runner supports. Verify that a deliberately failing disposable test leaves no running resources for its run ID. Do this in isolation from real projects. Keep at most a bounded diagnostic sample; a debugging exception needs an expiry and named owner.

## Mechanical checks to wire into the existing check command

- Effective temporary-service restart policy must be `no`.
- Effective temporary-service logging must have finite size and file limits.
- Each temporary run has a distinct project identity and a teardown path.
- After the test/failure simulation, inventory by run ID has no unexpected remaining resources.

Configuration validation can cover restart/log policy; a lifecycle integration test covers teardown. A checklist cannot replace those checks. Production policies belong in a different profile, not in a blanket prohibition.

Use the bundled deterministic check for selected temporary services; feed effective Compose JSON through stdin so interpolated configuration is not saved to a report:

```text
docker compose <the project's exact options> config --format json | python <skill-dir>/scripts/check_ephemeral.py --service test-runner
```

Repeat `--service` for each temporary service. Wire this into the project's existing check command when prevention is requested. It checks restart policy, ownership labels and explicit bounded local logs, and fails for missing services or invalid input. It does not prove teardown or freshness of the deployed containers. Inspect the shell's pipeline exit status for both commands.

Example service fragment (merge explicitly into a temporary profile; it is not a universal override):

```yaml
services:
  test-runner:
    restart: "no"
    labels:
      io.ai-poop-cleaner.project: "${CLEANUP_PROJECT:?set project}"
      io.ai-poop-cleaner.purpose: "ephemeral-test"
      io.ai-poop-cleaner.run-id: "${CLEANUP_RUN_ID:?set run ID}"
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

The numbers above are an example budget, not an inferred team requirement. Custom lifecycle labels are conventions of this skill; Docker does not enforce them. For volume ownership use volume labels too.

Keep global AGENTS/CLAUDE files small. If navigation is missing, add one pointer to the actual environment start/stop commands. Judge shared-resource ownership in review; enforce mechanical lifecycle rules in checks.
