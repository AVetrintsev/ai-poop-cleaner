# Host branch

## Processes and memory

On Linux use `/proc`, `ps`, `free` and, where available, proportional memory measurements. Distinguish PID/TGID from thread IDs; htop's repeated thread RSS represents the same process memory. `0 CPU` means idle, not abandoned. On macOS use `ps`, `vm_stat` and `memory_pressure`. On Windows use `Get-Process` and `Get-CimInstance Win32_Process`/`Win32_OperatingSystem`; inspect command lines only as needed and avoid storing them in reports.

Attribute candidate background processes through executable, parent, working directory, open ports, service manager and project/task evidence. Recheck PID plus start time to avoid PID reuse. Use the service's normal stop command before a targeted process stop; protect the current agent, editor, database and active builds. Check the owner that can restart a process (systemd, launchd, scheduled task, Compose), but change startup behavior only within authorization.

## Files and caches

Start with filesystem free space and bounded directory totals in the selected scope. Probe project build outputs, abandoned task directories, package caches and application logs, then deepen only the largest candidates. Avoid whole-disk recursive scans by default. Use package-manager cache commands only after inspecting their installed help and understanding their scope; a global cache is shared across projects.

For every deletion establish a regeneration method and absence of live consumers. Resolve paths, examine symlinks/junctions and reject traversal outside the authorized root. An ignored `dist`, `target`, `.scratch`, `node_modules` or temp directory may contain the only copy of an artifact or active output. Inspect Git status and worktree metadata before handling worktrees; use the agent's worktree management tool when it owns the worktree, otherwise the Git workflow. Preserve dirty or untracked work and detached work with unpreserved commits. OS-managed component stores and application data require their supported maintenance tools and a specific request.

On Windows use PowerShell `-LiteralPath` for filesystem operations; verify the resolved absolute recursive target stays inside the intended directory. Do not hand PowerShell-enumerated paths to cmd/batch deletion. Record permission failures as skipped areas. Do not empty the recycle bin or blanket-clear user temp folders as a substitute for attribution.

## WSL memory reclamation

Read guest `/proc/meminfo` (including MemAvailable, Cached, Buffers, SReclaimable), `free -h`, and Windows `vmmemWSL` working set before acting. Cache is reclaimable memory, not proof of a leak. Linux available RAM and Windows resident WSL memory measure different things.

If cache reclamation is requested and authorized, use a selected running distribution and sufficient privileges to sync filesystems, then write `3` to `/proc/sys/vm/drop_caches`. A Linux shell example is `sync && printf '3\n' > /proc/sys/vm/drop_caches`; execute the complete redirection with sufficient privilege, not just `sudo printf`. This is a guest-wide operation with possible I/O latency and temporary cache performance costs, not a routine step of disk cleanup. Do not launch an idle distribution solely to reclaim memory.

Measure guest memory and Windows working set after roughly 10 seconds and again by 30 seconds. Report the observed return, including zero if unchanged; do not promise a specific amount. Preserve services and verify their status. `wsl --shutdown` interrupts all distributions; use only with authorization covering that interruption. VHD compaction and swap changes are separate operations, not automatic fallbacks.

For prevention, inspect current WSL version and `.wslconfig`; discuss `autoMemoryReclaim` and `pageReporting` only against installed support. Preserve unrelated configuration and obtain authorization for required restart effects. [Microsoft configuration reference](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).

Disk space freed inside Linux does not prove that the Windows VHD file shrank. Report host allocation separately if measured.
