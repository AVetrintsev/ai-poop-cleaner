# Local report

Store under a user-approved local report directory (for example `.cleanup-reports/<UTC-run-id>/`) and exclude it from version control. A concise chat report is enough for a small run; a multi-resource cleanup should retain its inventory and journal.

```text
Scope: host / OS / distro / engine identity / project or system / mode
Authorization: user's requested outcome and any explicit data/stop permission
Coverage: inspected areas; inaccessible or unsupported areas
Baseline: timestamp; disk mount and used/free bytes; RAM metric and bytes
Actions: exact identity | owner evidence | consumer check | action | result/error
Protected: identity | reason | post-check
After: timestamp; same measurements; delta; concurrent activity caveat
Remaining: preserved / unknown / failed / unverified and why
Prevention: evidenced cause and smallest durable change
```

Count containers, unique image IDs and removed tags separately. Record failures without dumping environment variables or full command lines. Share a redacted summary, not the raw machine inventory.
