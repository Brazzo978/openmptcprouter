# Nan / NanBBR kernel 6.6 integration manifest

This branch keeps `nanqinlang` vanilla as the historical BBRv1/Nanqinlang
baseline and adds 9 separate NanBBR congestion controls. They are separate
Linux TCP congestion-control runtime names, not internal modes.

## Patch order

```text
997-BBRv3.patch
9971-tcp_nanqinlang.patch
9972-tcp_nanbbr3.patch
9973-tcp_nanbbr1.patch
9974-tcp_nanbbr2.patch
```

## Runtime names

```text
nanbbr1_light  nanbbr1_def  nanbbr1_aggr
nanbbr2_light  nanbbr2_def  nanbbr2_aggr
nanbbr3_light  nanbbr3_def  nanbbr3_aggr
```

`*_def` is the normal mobile/edge profile. `*_light` is calmer for cleaner
Starlink/FWA or lower jitter. `*_aggr` is more aggressive for dirty LTE/5G, but
keeps hard/panic loss and RTT/BW collapse guards.

## Patch contents

`9971-tcp_nanqinlang.patch` adds runtime name `nanqinlang` and is intentionally
the vanilla historical Nanqinlang-style baseline.

`9972-tcp_nanbbr3.patch` adds:

```text
CONFIG_TCP_CONG_NANBBR3_LIGHT -> tcp_nanbbr3_light.o -> nanbbr3_light
CONFIG_TCP_CONG_NANBBR3_DEF   -> tcp_nanbbr3_def.o   -> nanbbr3_def
CONFIG_TCP_CONG_NANBBR3_AGGR  -> tcp_nanbbr3_aggr.o  -> nanbbr3_aggr
```

`9973-tcp_nanbbr1.patch` adds:

```text
CONFIG_TCP_CONG_NANBBR1_LIGHT -> tcp_nanbbr1_light.o -> nanbbr1_light
CONFIG_TCP_CONG_NANBBR1_DEF   -> tcp_nanbbr1_def.o   -> nanbbr1_def
CONFIG_TCP_CONG_NANBBR1_AGGR  -> tcp_nanbbr1_aggr.o  -> nanbbr1_aggr
```

`9974-tcp_nanbbr2.patch` adds:

```text
CONFIG_TCP_CONG_NANBBR2_LIGHT -> tcp_nanbbr2_light.o -> nanbbr2_light
CONFIG_TCP_CONG_NANBBR2_DEF   -> tcp_nanbbr2_def.o   -> nanbbr2_def
CONFIG_TCP_CONG_NANBBR2_AGGR  -> tcp_nanbbr2_aggr.o  -> nanbbr2_aggr
```

## Config 6.6

`6.6/target/linux/generic/config-6.6` enables all 9 NanBBR controls and leaves
all NanBBR defaults disabled. Users can select the runtime name explicitly via
OpenWrt/OMR.

## Dynamic loss gate

For `nanbbr2_*` and `nanbbr3_*`, the loss response does not treat soft radio
loss as an unconditional collapse signal. It uses:

```text
panic_loss || hard_loss || (soft_loss && (rtt_bad || bw_bad))
```

`rtt_bad` compares the sample RTT to min RTT using the profile trigger.
`bw_bad` compares the latest delivery signal against max bandwidth using the
profile trigger. ECN response, ProbeRTT, pacing, and the normal BBR loss
machinery remain enabled.

## Data files

The profile source data for another agent is kept in:

```text
docs/nanbbr_final_profiles.yaml
docs/nanbbr_codex_final_brief.md
docs/nanbbr_9_profiles_constants_v3.h
```

## Recommended selection

Use `nanbbr3_def` as the general 4G/5G/FWA/Starlink default.
Use `nanbbr3_light` for cleaner links or lower jitter.
Use `nanbbr3_aggr` when high radio loss is normal but delivery rate remains
alive. Keep `nanbbr1_*` as BBRv1-style fallback/benchmark and `nanbbr2_*` as
BBRv2 experimental comparison.
