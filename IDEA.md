# Future Ideas

## Force Ray for Port Forwarding

Goal:
- allow Ray-based port forwarding even when the main proxy in use is not V2Ray/XRay (for example when the client uses Shadowsocks as the main proxy)

Proposed UX:
- keep the existing `Use Ray for port forwarding` toggle
- add a second toggle such as `Force Ray enable for port forwarding`

Intended behavior:
- if a port-forward rule is marked to use Ray
- and the selected main proxy is not V2Ray/XRay
- the client still keeps a Ray backend available only for port-forward handling
- the normal client traffic path remains unchanged

Implementation direction:
- decouple `main proxy in use` from `backend used for Ray-based port forwarding`
- use a dedicated backend choice or a fixed preferred backend (XRay is the most sensible candidate)
- keep the Ray service enabled only when at least one port-forward rule requires it

Why this is feasible:
- Ray-based port forwarding is handled by separate VPS API routes (`v2rayredirect` / `xrayredirect`)
- routing-wise it does not require the main proxy path to be V2Ray/XRay
- the current limitation is in client-side logic and service enable/disable decisions, not in the transport model itself

Status:
- implemented in current 0.62.2-3KTEST tree
- new firewall rule flag: `force_xray_pf`
- backend now auto-enables XRay for those rules when main proxy is non-Ray
- transparent XRay redirect rules are flushed in forced mode to keep main traffic path unchanged
