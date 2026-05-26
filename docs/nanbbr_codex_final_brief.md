# nanbbr 9-profile plan for Codex

Generated: 2026-05-26
Fixed point: `BBR_UNIT = 1 << 8 = 256`

## Goal

Create 9 separate TCP congestion-control modules/runtime names:

```text
nanbbr1_light  nanbbr1_def  nanbbr1_aggr
nanbbr2_light  nanbbr2_def  nanbbr2_aggr
nanbbr3_light  nanbbr3_def  nanbbr3_aggr
```

These are **separate congestion controls**, not sysctl modes and not replacements for upstream `bbr`.
The `*_def` profiles are the normal/default mobile-edge profiles.
The `*_light` profiles are slightly more conservative.
The `*_aggr` profiles are the most aggressive, but still guarded against collapse.

All runtime names are <= 15 characters, so they fit Linux `TCP_CA_NAME_MAX=16` with the terminating NUL.

## Implementation priority

1. `nanbbr3_*`
2. `nanbbr1_*`
3. `nanbbr2_*`

Reason: BBRv3 is already in the OMR 6.6 patch context; BBR2 needs more rebasing work.

## BBR2/3 dynamic loss gate

For `nanbbr2_*` and `nanbbr3_*`, do **not** use a single tiny static loss threshold.
LTE/5G can show high TCP-visible loss while still delivering usable bandwidth.

Use:

```c
trigger = panic_loss || hard_loss || (soft_loss && (rtt_bad || bw_bad));
```

Where:

```c
rtt_bad = sample_rtt_us >= min_rtt_us * rtt_inflation_trigger / BBR_UNIT;
bw_bad  = bw_latest <= bw_reference * bw_drop_trigger / BBR_UNIT;
```

If this dynamic gate is not implemented, use the `LOSS_THRESH_STATIC_FALLBACK` value from the C header, but note that it is less accurate.

## Quick table

| profile | startup | cwnd | drain | probe gains | probe mean | headroom/loss |
|---|---:|---:|---:|---|---:|---|
| `nanbbr3_light` | 2.801 | 2.199 | 0.355 | 1.316/0.719/1.000/1.078 | 1.028 | 29.7% / soft 5.9, hard 11.7, panic 19.9% |
| `nanbbr3_def` | 2.902 | 2.398 | 0.344 | 1.398/0.719/1.027/1.117 | 1.065 | 23.8% / soft 7.8, hard 15.6, panic 25.0% |
| `nanbbr3_aggr` | 3.004 | 2.648 | 0.332 | 1.477/0.699/1.047/1.180 | 1.101 | 19.9% / soft 9.8, hard 19.9, panic 27.7% |
| `nanbbr2_light` | 2.754 | 2.098 | 0.363 | 1.277/0.719/1.000/1.059 | 1.014 | 29.7% / soft 5.9, hard 11.7, panic 19.9% |
| `nanbbr2_def` | 2.852 | 2.297 | 0.348 | 1.348/0.727/1.020/1.098 | 1.048 | 25.8% / soft 7.8, hard 15.6, panic 25.0% |
| `nanbbr2_aggr` | 2.953 | 2.547 | 0.336 | 1.430/0.699/1.039/1.148 | 1.079 | 21.9% / soft 9.8, hard 19.9, panic 27.7% |
| `nanbbr1_light` | 2.754 | 2.000 | 0.363 | 1.297/0.719/3x1.000/3x1.117 | 1.046 | lt_loss 7.8%, probe_rtt 220ms |
| `nanbbr1_def` | 2.852 | 2.000 | 0.348 | 1.379/0.719/3x1.047/3x1.199 | 1.104 | lt_loss 11.7%, probe_rtt 200ms |
| `nanbbr1_aggr` | 2.953 | 2.000 | 0.336 | 1.449/0.699/3x1.098/3x1.297 | 1.167 | lt_loss 15.6%, probe_rtt 170ms |

## Keep unchanged initially

- Keep BBR2/3 ECN factor/threshold/reprobe behavior.
- Keep `bbr_bw_probe_cwnd_gain = 1`.
- Keep TSO/GSO/send quantum logic.
- Keep ProbeRTT logic unless the existing local patch already changed it.
- Do not convert the BBR2/3 soft loss threshold into unconditional loss reaction.

## Files

- `nanbbr_9_profiles_v3.yaml`: full machine-readable profiles.
- `nanbbr_9_profiles_constants_v3.h`: C constants and pseudocode.
