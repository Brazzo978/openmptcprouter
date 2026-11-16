# 3K migration preparation for upstream 0.65

Status: **preparation only, 2026-11-16**. This branch does not yet rebase the
client or change the frozen 0.64 build lock. Complete and validate the final
compatible VPS monitoring dashboard before migrating the build base.

## Release policy

- `v0.64.2-3K` is the current stable/latest client on GitHub.
- `v0.64.3-3K` is a pre-release while profile-switching instability is
  investigated. Its existing images and checksums remain available.
- Earlier successful profile tests do not supersede reported instability.
  The profile acceptance gate must be reopened before stable promotion.
- A dashboard-only VPS update must remain compatible with both clients.

## Exact upstream preparation targets

Verified against remote tags, not moving branches:

| Component | Tag | Peeled source commit |
| --- | --- | --- |
| Build root | `v0.65` | `4352253893dcb0de1519ceac286c8259ea28d722` |
| OMR feed | `v0.65` | `6090047d1f2e25c82fb40a6de381d3f3717cf3f8` |
| VPS baseline | `v0.1097` | `c90143c8c996109fe9d6de24bb11c374d0085882` |

See `port-0.65-plan.json` for provenance. These are migration inputs; they
are not a completed materialization lock. Resolve and pin every OpenWrt,
LuCI and package feed dependency before compiling a 0.65 candidate.

## Preserve the complete 3K inventory

[3K-MODIFICATIONS.md](3K-MODIFICATIONS.md) remains the authoritative feature
inventory. Every existing identifier must receive an explicit disposition:
ported, superseded by verified upstream behavior, or retained experimentally.
Keep evidence and test identifiers rather than silently deleting entries.

In particular preserve congestion controls and BBRv3 defaults, schedulers,
SQM ratios, advanced diagnostics/logs, custom bandwidth/monitoring, the
single-page wizard, independent Xray forwarding, MQVPN native LAN routing,
RTH peer/global LAN controls, server DNAT destination scope, LAN subnet
synchronization, package exclusions, English-only images and the hardware
maintenance policy. Preserve the VPS monitoring dashboard as an independent
read-only feature. Do not reintroduce VPS backups or modem management.

## Work sequence and acceptance gates

1. Finish the 0.64-compatible VPS dashboard package, authentication/privacy
   tests, UI review and an installed test-VPS run. Keep shipped artifacts
   separate from previews and source-only checks.
2. Freeze separate 0.65 source checkouts. Compare each inventory item against
   actual upstream implementation before replaying custom patches.
3. Reconcile MQVPN 0.19 with native LAN/routing and recovery patches. Account
   for its socket API changes, strict true/false config and log-format changes.
   Validate both client and server, FEC, forwarding and first-start recovery.
4. Port the kernel/congestion/BPF set as a matched client/VPS pair. Validate
   scheduler loading and live behavior; inspect the reported MPTCP receive
   stall/memory issue before selecting the final kernel.
5. Reconcile runtime state under `/var/state`, API pinning and the 3K API-path
   helper. Preserve no-replay behavior for uncertain mutation delivery.
6. Keep profiles experimental until repeated apply/rollback, timeout/reboot,
   DNS, tunnel, RTH and forwarding acceptance succeeds on physical WANs.
7. Start build acceptance on x86_64 and Flint 2, then the maintained ARM set.
   Require real install/boot and WAN-loss recovery evidence before promotion.

No 0.65 firmware is compiled or published by this preparation change.
