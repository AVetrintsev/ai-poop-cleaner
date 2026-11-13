---
name: cleanup
description: Clean up project or system development leftovers, investigate duplicate processes and RAM use, retire local service environments, or reclaim WSL memory. Use for requested resource cleanup, not source-code refactoring.
---

# Cleanup

One entry point for reclaiming resources without losing ownership context. Respond in the user's language. This skill needs shell access to the target machine; a cloud sandbox can only clean its own environment unless an authorized remote connection exists.

## 1. Resolve scope and intent

Read the request and existing authorization. Support natural language and these shorthand modes (they are agent instructions, not shell flags):

| Mode | Outcome |
| --- | --- |
| `audit` | Inventory and proposed actions; no resource mutations |
| `clean` | Remove proven disposable, inactive leftovers within scope |
| `retire <project>` | Decommission the named project's local environments |
| `memory` | Diagnose RAM and, when requested, reclaim WSL cache |
| `prevent` | Add lifecycle checks to the explicitly selected project |

Bare invocation means `clean`: use the current project when inside one; otherwise inspect system-wide development resources. An explicit `system` scope includes discovery across projects, but does not establish that their data is disposable. `project <path>` selects a project from any directory. A missing path or ambiguous service name is a scope question; perform independent read-only discovery while resolving it.

Record host, OS, project root (or system scope), WSL distribution, container engine/context, protected running work, and mode. Inspect the effective Docker endpoint including environment overrides; remote endpoints require explicit remote scope. Complete when the target environment and mutation boundary are unambiguous. Do not switch to another Docker daemon to work around an access error.

## 2. Inventory and attribute

Read only the relevant branch:

- Containers, Compose, images, volumes, networks, build cache: [Docker](references/docker.md).
- Windows, WSL, Linux or macOS processes, files and memory: [Host](references/host.md).
- Requested lifecycle prevention: [Prevention](references/prevention.md).

Record baseline disk and memory measurements with timestamps and measurement layer. Classify each candidate as **disposable**, **protected**, or **unknown** using ownership, consumers and live activity. Age, an idle CPU, a stopped container, an ignored file, or an image without tags is only a discovery clue. An expired label is a clue too, not deletion permission.

Complete when every proposed action has an exact target, ownership evidence, current consumers, why it is unused, and whether it destroys data. Record inaccessible areas as unknown, not empty. Protect active tests, their dependencies, shared resources and user files. Inspect sibling projects only as needed to establish shared ownership.

## 3. Apply within authorization

Show a compact action summary. A cleanup request authorizes removal of established disposable leftovers in scope; continue without asking again. Preserve sources, uncommitted work, persistent application data, backups and secrets. Stopping active work, deleting persistent data, changing startup settings, or restarting WSL needs authorization covering that consequence. If absent, ask once about the concrete targets and consequence while completing independent authorized work. `retire` alone does not authorize erasing databases; an existing explicit instruction to erase those data does.

Before each batch, recheck identity, ownership and consumers against live state. Skip and explain changed targets. Resolve paths to absolute paths and verify containment and symlinks/junctions before recursive filesystem operations; use one native shell end to end. For shared daemon access, serialize cleaners when possible; a lock does not protect against builders that ignore it.

Use explicit IDs/paths and normal, non-forced deletion. Broad `prune`, process-name-wide kills, wildcard recursive removal, direct Docker storage deletion, and WSL unregister are outside this workflow. Stop containers gracefully first when their shutdown is authorized. Logs may be the only useful diagnostic evidence: preserve a bounded relevant sample before removing a failed environment when needed, without copying credentials.

Write a local action journal containing target, reason, outcome and errors. Keep raw command lines, environment variables and inspect dumps out of shared reports. On conflict, refresh and skip; do not escalate to force. A confirmed already-absent target is an idempotent success. An inspect failure alone does not prove absence.

## 4. Verify and finish

Re-inventory exact targets and preserved workloads. Check images by immutable ID as well as tags. Compare before/after at the same layer: Linux filesystem space, Windows disk allocation, Linux available RAM, or Windows WSL working set. Shared image sizes cannot be summed as reclaimed bytes. Concurrent cleanup means a disk delta belongs to the combined interval, not exclusively this run.

Do at most one fresh pass for newly discovered leftovers within the same authorization. If resources keep appearing, report the producer and remaining items; avoid an endless delete/recreate race. Every target must end as removed, preserved, already absent, failed, or unverified. Partial coverage or failed verification means partial completion.

Return: what changed; measured effect and attribution limits; what was preserved; unresolved items; the relevant prevention action. Use [report format](references/report.md) when saving a report. Keep machine-specific reports local, outside the public skill repository.
