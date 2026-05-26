# nanbbr final porting brief for Codex

## Design intent

Implement `nanbbr1`, `nanbbr2`, and `nanbbr3` for OpenMPTCProuter kernel 6.6.

Goal: throughput-dominant Nan-style congestion control for 4G/5G, Starlink and FWA. Fairness toward competing CUBIC/Reno/BBR flows is deliberately low priority. The hard rule is self-preservation: when sustained loss, ECN or queue pressure makes the path unusable, the algorithm must slow down instead of continuing to flood.

Fixed point: `BBR_SCALE = 8`, `BBR_UNIT = 1 << 8 = 256`.

Integer policy: Linux-kernel style integer arithmetic/flooring. Startup high gain keeps the common `+1` bias.

## Recommended defaults

Use these as the first implementation values:

- `nanbbr3`: `balanced_edge`
- `nanbbr2`: `balanced_edge`, slightly calmer than nanbbr3
- `nanbbr1`: `balanced_edge`, fallback/benchmark only; BBRv1 has fewer safety brakes

## nanbbr3 balanced_edge constants

```c
static const int bbr_startup_pacing_gain = BBR_UNIT * 295 / 100 + 1; /* 756, 2.953125x */
static const int bbr_startup_cwnd_gain   = BBR_UNIT * 250 / 100;     /* 640, 2.500000x */
static const int bbr_drain_gain          = BBR_UNIT * 100 / 295;     /*  86, 0.335938x */

static const int bbr_pacing_gain[] = {
        [BBR_BW_PROBE_UP]     = BBR_UNIT * 145 / 100, /* 371, 1.449219x */
        [BBR_BW_PROBE_DOWN]   = BBR_UNIT * 3 / 4,     /* 192, 0.750000x */
        [BBR_BW_PROBE_CRUISE] = BBR_UNIT * 105 / 100, /* 268, 1.046875x */
        [BBR_BW_PROBE_REFILL] = BBR_UNIT * 115 / 100, /* 294, 1.148438x */
};

static const int bbr_inflight_headroom = BBR_UNIT * 16 / 100; /* 40, 15.625% */
static const int bbr_loss_thresh       = BBR_UNIT * 3 / 100;  /*  7, 2.734% */
static const int bbr_beta              = BBR_UNIT * 30 / 100; /* 76, 29.688% kernel cut; keep ~=70.312% if code uses UNIT-beta */

static const int bbr_ecn_factor       = BBR_UNIT * 1 / 3; /* keep base */
static const int bbr_ecn_thresh       = BBR_UNIT * 1 / 2; /* keep base */
static const int bbr_ecn_reprobe_gain = BBR_UNIT * 1 / 2; /* keep base */
static const int bbr_full_loss_cnt    = 5;
static const int bbr_full_ecn_cnt     = 2;
static const int bbr_bw_probe_cwnd_gain = 1;
```

Probe BW mean: `(371 + 192 + 268 + 294) / 4 / 256 = 1.0986328125x`.
With 1% pacing margin: about `1.087646484x`.

## nanbbr2 balanced_edge constants

```c
static const int bbr_startup_pacing_gain = BBR_UNIT * 290 / 100 + 1; /* 743, 2.902344x */
static const int bbr_startup_cwnd_gain   = BBR_UNIT * 240 / 100;     /* 614, 2.398438x */
static const int bbr_drain_gain          = BBR_UNIT * 100 / 290;     /*  88, 0.343750x */

static const int bbr_pacing_gain[] = {
        [BBR_BW_PROBE_UP]     = BBR_UNIT * 140 / 100, /* 358, 1.398438x */
        [BBR_BW_PROBE_DOWN]   = BBR_UNIT * 76 / 100,  /* 194, 0.757812x */
        [BBR_BW_PROBE_CRUISE] = BBR_UNIT * 103 / 100, /* 263, 1.027344x */
        [BBR_BW_PROBE_REFILL] = BBR_UNIT * 112 / 100, /* 286, 1.117188x */
};

static const int bbr_inflight_headroom = BBR_UNIT * 18 / 100; /* 46, 17.969% */
static const int bbr_loss_thresh       = BBR_UNIT * 3 / 100;  /*  7, 2.734% */
static const int bbr_beta              = BBR_UNIT * 30 / 100; /* 76, 29.688% kernel cut */

static const int bbr_ecn_factor       = BBR_UNIT * 1 / 3;
static const int bbr_ecn_thresh       = BBR_UNIT * 1 / 2;
static const int bbr_ecn_reprobe_gain = BBR_UNIT * 1 / 2;
static const int bbr_full_loss_cnt    = 5;
static const int bbr_full_ecn_cnt     = 2;
static const int bbr_bw_probe_cwnd_gain = 1;
```

Probe BW mean: `(358 + 194 + 263 + 286) / 4 / 256 = 1.0751953125x`.
With 1% pacing margin: about `1.064443359x`.

## nanbbr1 balanced_edge constants

```c
static const int bbr_high_gain  = BBR_UNIT * 295 / 100 + 1; /* 756, 2.953125x */
static const int bbr_drain_gain = BBR_UNIT * 100 / 295;     /*  86, 0.335938x */
static const int bbr_cwnd_gain  = BBR_UNIT * 2;             /* 512, 2.000000x */

static const int bbr_pacing_gain[] = {
        BBR_UNIT * 145 / 100, /* 371, 1.449219x */
        BBR_UNIT * 3 / 4,     /* 192, 0.750000x */
        BBR_UNIT * 110 / 100, /* 281, 1.097656x */
        BBR_UNIT * 110 / 100, /* 281, 1.097656x */
        BBR_UNIT * 110 / 100, /* 281, 1.097656x */
        BBR_UNIT * 130 / 100, /* 332, 1.296875x */
        BBR_UNIT * 130 / 100, /* 332, 1.296875x */
        BBR_UNIT * 130 / 100, /* 332, 1.296875x */
};

static const u32 bbr_lt_loss_thresh = BBR_UNIT * 5 / 100; /* 12, 4.6875% */
static const u32 bbr_probe_rtt_mode_ms = 150;
```

Probe BW mean: `1.1728515625x`.
With 1% pacing margin: about `1.161123047x`.

## Guardrails

Do not disable loss, ECN, recovery, app-limited filtering, or ProbeRTT logic.

Do not increase `bbr_bw_probe_cwnd_gain` in the first patch.

Keep ECN base behavior initially.

For `nanbbr3` and `nanbbr2`, sustained loss above about 2.7% on balanced_edge should trigger existing BBR2/3 safety behavior. For `nanbbr1`, sustained loss around 4.7% should trigger the LT policer/loss estimator.

Full details and alternative profiles are in `nanbbr_final_profiles.yaml`.
