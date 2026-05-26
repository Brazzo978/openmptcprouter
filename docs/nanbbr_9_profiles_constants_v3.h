/* SPDX-License-Identifier: GPL-2.0 */
/* nanbbr 9-profile constants for BBR_UNIT = 256. Generated for OpenMPTCProuter Linux 6.6. */

/*
 * Runtime names:
 *   nanbbr1_light nanbbr1_def nanbbr1_aggr
 *   nanbbr2_light nanbbr2_def nanbbr2_aggr
 *   nanbbr3_light nanbbr3_def nanbbr3_aggr
 *
 * For BBR2/3 prefer dynamic loss gate:
 *   panic_loss || hard_loss || (soft_loss && (rtt_bad || bw_bad))
 * Do not use SOFT loss as unconditional bbr_loss_thresh unless you intentionally want a cleaner/less LTE-tolerant profile.
 */

/* nanbbr1_light: startup=2.753906x, probe_mean=1.045898x */
#define NANBBR1_LIGHT_HIGH_GAIN        (BBR_UNIT * 275 / 100 + 1) /* 705, 2.753906x */
#define NANBBR1_LIGHT_DRAIN_GAIN       (BBR_UNIT * 100 / 275) /* 93, 0.363281x */
#define NANBBR1_LIGHT_CWND_GAIN        (BBR_UNIT * 200 / 100) /* 512, 2.000000x */
#define NANBBR1_LIGHT_LT_LOSS_THRESH   (BBR_UNIT * 8 / 100) /* 20, 7.812500% */
#define NANBBR1_LIGHT_PROBE_RTT_MS     (220)
static const int nanbbr1_light_pacing_gain[] = {
	(BBR_UNIT * 130 / 100), /* 332, 1.296875x */
	(BBR_UNIT * 72 / 100), /* 184, 0.718750x */
	(BBR_UNIT * 100 / 100), /* 256, 1.000000x */
	(BBR_UNIT * 100 / 100), /* 256, 1.000000x */
	(BBR_UNIT * 100 / 100), /* 256, 1.000000x */
	(BBR_UNIT * 112 / 100), /* 286, 1.117188x */
	(BBR_UNIT * 112 / 100), /* 286, 1.117188x */
	(BBR_UNIT * 112 / 100), /* 286, 1.117188x */
};
/* mean=1.045898438x, mean_with_1pct_margin=1.035439453x */

/* nanbbr1_def: startup=2.851562x, probe_mean=1.104492x */
#define NANBBR1_DEF_HIGH_GAIN        (BBR_UNIT * 285 / 100 + 1) /* 730, 2.851562x */
#define NANBBR1_DEF_DRAIN_GAIN       (BBR_UNIT * 100 / 285) /* 89, 0.347656x */
#define NANBBR1_DEF_CWND_GAIN        (BBR_UNIT * 200 / 100) /* 512, 2.000000x */
#define NANBBR1_DEF_LT_LOSS_THRESH   (BBR_UNIT * 12 / 100) /* 30, 11.718750% */
#define NANBBR1_DEF_PROBE_RTT_MS     (200)
static const int nanbbr1_def_pacing_gain[] = {
	(BBR_UNIT * 138 / 100), /* 353, 1.378906x */
	(BBR_UNIT * 72 / 100), /* 184, 0.718750x */
	(BBR_UNIT * 105 / 100), /* 268, 1.046875x */
	(BBR_UNIT * 105 / 100), /* 268, 1.046875x */
	(BBR_UNIT * 105 / 100), /* 268, 1.046875x */
	(BBR_UNIT * 120 / 100), /* 307, 1.199219x */
	(BBR_UNIT * 120 / 100), /* 307, 1.199219x */
	(BBR_UNIT * 120 / 100), /* 307, 1.199219x */
};
/* mean=1.104492188x, mean_with_1pct_margin=1.093447266x */

/* nanbbr1_aggr: startup=2.953125x, probe_mean=1.166504x */
#define NANBBR1_AGGR_HIGH_GAIN        (BBR_UNIT * 295 / 100 + 1) /* 756, 2.953125x */
#define NANBBR1_AGGR_DRAIN_GAIN       (BBR_UNIT * 100 / 295) /* 86, 0.335938x */
#define NANBBR1_AGGR_CWND_GAIN        (BBR_UNIT * 200 / 100) /* 512, 2.000000x */
#define NANBBR1_AGGR_LT_LOSS_THRESH   (BBR_UNIT * 16 / 100) /* 40, 15.625000% */
#define NANBBR1_AGGR_PROBE_RTT_MS     (170)
static const int nanbbr1_aggr_pacing_gain[] = {
	(BBR_UNIT * 145 / 100), /* 371, 1.449219x */
	(BBR_UNIT * 70 / 100), /* 179, 0.699219x */
	(BBR_UNIT * 110 / 100), /* 281, 1.097656x */
	(BBR_UNIT * 110 / 100), /* 281, 1.097656x */
	(BBR_UNIT * 110 / 100), /* 281, 1.097656x */
	(BBR_UNIT * 130 / 100), /* 332, 1.296875x */
	(BBR_UNIT * 130 / 100), /* 332, 1.296875x */
	(BBR_UNIT * 130 / 100), /* 332, 1.296875x */
};
/* mean=1.166503906x, mean_with_1pct_margin=1.154838867x */

/* nanbbr2_light: startup=2.753906x, probe_mean=1.013672x */
#define NANBBR2_LIGHT_STARTUP_PACING_GAIN (BBR_UNIT * 275 / 100 + 1) /* 705, 2.753906x */
#define NANBBR2_LIGHT_STARTUP_CWND_GAIN   (BBR_UNIT * 210 / 100) /* 537, 2.097656x */
#define NANBBR2_LIGHT_DRAIN_GAIN          (BBR_UNIT * 100 / 275) /* 93, 0.363281x */
#define NANBBR2_LIGHT_INFLIGHT_HEADROOM   (BBR_UNIT * 30 / 100) /* 76, 29.687500% */
#define NANBBR2_LIGHT_SOFT_LOSS_THRESH    (BBR_UNIT * 6 / 100) /* 15, 5.859375% */
#define NANBBR2_LIGHT_HARD_LOSS_THRESH    (BBR_UNIT * 12 / 100) /* 30, 11.718750% */
#define NANBBR2_LIGHT_PANIC_LOSS_THRESH   (BBR_UNIT * 20 / 100) /* 51, 19.921875% */
#define NANBBR2_LIGHT_RTT_INFLATE_TRIG    (BBR_UNIT * 155 / 100) /* 396, 1.546875x */
#define NANBBR2_LIGHT_BW_DROP_TRIG        (BBR_UNIT * 88 / 100) /* 225, 87.890625% */
#define NANBBR2_LIGHT_BETA_CUT            (BBR_UNIT * 40 / 100) /* 102, cut 39.843750% */
#define NANBBR2_LIGHT_LOSS_THRESH_STATIC_FALLBACK (BBR_UNIT * 8 / 100) /* 20, 7.812500% */
static const int nanbbr2_light_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = (BBR_UNIT * 128 / 100), /* 327, 1.277344x */
	[BBR_BW_PROBE_DOWN]   = (BBR_UNIT * 72 / 100), /* 184, 0.718750x */
	[BBR_BW_PROBE_CRUISE] = (BBR_UNIT * 100 / 100), /* 256, 1.000000x */
	[BBR_BW_PROBE_REFILL] = (BBR_UNIT * 106 / 100), /* 271, 1.058594x */
};
/* mean=1.013671875x, mean_with_1pct_margin=1.003535156x */

/* nanbbr2_def: startup=2.851562x, probe_mean=1.047852x */
#define NANBBR2_DEF_STARTUP_PACING_GAIN (BBR_UNIT * 285 / 100 + 1) /* 730, 2.851562x */
#define NANBBR2_DEF_STARTUP_CWND_GAIN   (BBR_UNIT * 230 / 100) /* 588, 2.296875x */
#define NANBBR2_DEF_DRAIN_GAIN          (BBR_UNIT * 100 / 285) /* 89, 0.347656x */
#define NANBBR2_DEF_INFLIGHT_HEADROOM   (BBR_UNIT * 26 / 100) /* 66, 25.781250% */
#define NANBBR2_DEF_SOFT_LOSS_THRESH    (BBR_UNIT * 8 / 100) /* 20, 7.812500% */
#define NANBBR2_DEF_HARD_LOSS_THRESH    (BBR_UNIT * 16 / 100) /* 40, 15.625000% */
#define NANBBR2_DEF_PANIC_LOSS_THRESH   (BBR_UNIT * 25 / 100) /* 64, 25.000000% */
#define NANBBR2_DEF_RTT_INFLATE_TRIG    (BBR_UNIT * 175 / 100) /* 448, 1.750000x */
#define NANBBR2_DEF_BW_DROP_TRIG        (BBR_UNIT * 85 / 100) /* 217, 84.765625% */
#define NANBBR2_DEF_BETA_CUT            (BBR_UNIT * 37 / 100) /* 94, cut 36.718750% */
#define NANBBR2_DEF_LOSS_THRESH_STATIC_FALLBACK (BBR_UNIT * 12 / 100) /* 30, 11.718750% */
static const int nanbbr2_def_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = (BBR_UNIT * 135 / 100), /* 345, 1.347656x */
	[BBR_BW_PROBE_DOWN]   = (BBR_UNIT * 73 / 100), /* 186, 0.726562x */
	[BBR_BW_PROBE_CRUISE] = (BBR_UNIT * 102 / 100), /* 261, 1.019531x */
	[BBR_BW_PROBE_REFILL] = (BBR_UNIT * 110 / 100), /* 281, 1.097656x */
};
/* mean=1.047851562x, mean_with_1pct_margin=1.037373047x */

/* nanbbr2_aggr: startup=2.953125x, probe_mean=1.079102x */
#define NANBBR2_AGGR_STARTUP_PACING_GAIN (BBR_UNIT * 295 / 100 + 1) /* 756, 2.953125x */
#define NANBBR2_AGGR_STARTUP_CWND_GAIN   (BBR_UNIT * 255 / 100) /* 652, 2.546875x */
#define NANBBR2_AGGR_DRAIN_GAIN          (BBR_UNIT * 100 / 295) /* 86, 0.335938x */
#define NANBBR2_AGGR_INFLIGHT_HEADROOM   (BBR_UNIT * 22 / 100) /* 56, 21.875000% */
#define NANBBR2_AGGR_SOFT_LOSS_THRESH    (BBR_UNIT * 10 / 100) /* 25, 9.765625% */
#define NANBBR2_AGGR_HARD_LOSS_THRESH    (BBR_UNIT * 20 / 100) /* 51, 19.921875% */
#define NANBBR2_AGGR_PANIC_LOSS_THRESH   (BBR_UNIT * 28 / 100) /* 71, 27.734375% */
#define NANBBR2_AGGR_RTT_INFLATE_TRIG    (BBR_UNIT * 190 / 100) /* 486, 1.898438x */
#define NANBBR2_AGGR_BW_DROP_TRIG        (BBR_UNIT * 80 / 100) /* 204, 79.687500% */
#define NANBBR2_AGGR_BETA_CUT            (BBR_UNIT * 40 / 100) /* 102, cut 39.843750% */
#define NANBBR2_AGGR_LOSS_THRESH_STATIC_FALLBACK (BBR_UNIT * 16 / 100) /* 40, 15.625000% */
static const int nanbbr2_aggr_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = (BBR_UNIT * 143 / 100), /* 366, 1.429688x */
	[BBR_BW_PROBE_DOWN]   = (BBR_UNIT * 70 / 100), /* 179, 0.699219x */
	[BBR_BW_PROBE_CRUISE] = (BBR_UNIT * 104 / 100), /* 266, 1.039062x */
	[BBR_BW_PROBE_REFILL] = (BBR_UNIT * 115 / 100), /* 294, 1.148438x */
};
/* mean=1.079101562x, mean_with_1pct_margin=1.068310547x */

/* nanbbr3_light: startup=2.800781x, probe_mean=1.028320x */
#define NANBBR3_LIGHT_STARTUP_PACING_GAIN (BBR_UNIT * 280 / 100 + 1) /* 717, 2.800781x */
#define NANBBR3_LIGHT_STARTUP_CWND_GAIN   (BBR_UNIT * 220 / 100) /* 563, 2.199219x */
#define NANBBR3_LIGHT_DRAIN_GAIN          (BBR_UNIT * 100 / 280) /* 91, 0.355469x */
#define NANBBR3_LIGHT_INFLIGHT_HEADROOM   (BBR_UNIT * 30 / 100) /* 76, 29.687500% */
#define NANBBR3_LIGHT_SOFT_LOSS_THRESH    (BBR_UNIT * 6 / 100) /* 15, 5.859375% */
#define NANBBR3_LIGHT_HARD_LOSS_THRESH    (BBR_UNIT * 12 / 100) /* 30, 11.718750% */
#define NANBBR3_LIGHT_PANIC_LOSS_THRESH   (BBR_UNIT * 20 / 100) /* 51, 19.921875% */
#define NANBBR3_LIGHT_RTT_INFLATE_TRIG    (BBR_UNIT * 155 / 100) /* 396, 1.546875x */
#define NANBBR3_LIGHT_BW_DROP_TRIG        (BBR_UNIT * 88 / 100) /* 225, 87.890625% */
#define NANBBR3_LIGHT_BETA_CUT            (BBR_UNIT * 40 / 100) /* 102, cut 39.843750% */
#define NANBBR3_LIGHT_LOSS_THRESH_STATIC_FALLBACK (BBR_UNIT * 8 / 100) /* 20, 7.812500% */
static const int nanbbr3_light_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = (BBR_UNIT * 132 / 100), /* 337, 1.316406x */
	[BBR_BW_PROBE_DOWN]   = (BBR_UNIT * 72 / 100), /* 184, 0.718750x */
	[BBR_BW_PROBE_CRUISE] = (BBR_UNIT * 100 / 100), /* 256, 1.000000x */
	[BBR_BW_PROBE_REFILL] = (BBR_UNIT * 108 / 100), /* 276, 1.078125x */
};
/* mean=1.028320312x, mean_with_1pct_margin=1.018037109x */

/* nanbbr3_def: startup=2.902344x, probe_mean=1.065430x */
#define NANBBR3_DEF_STARTUP_PACING_GAIN (BBR_UNIT * 290 / 100 + 1) /* 743, 2.902344x */
#define NANBBR3_DEF_STARTUP_CWND_GAIN   (BBR_UNIT * 240 / 100) /* 614, 2.398438x */
#define NANBBR3_DEF_DRAIN_GAIN          (BBR_UNIT * 100 / 290) /* 88, 0.343750x */
#define NANBBR3_DEF_INFLIGHT_HEADROOM   (BBR_UNIT * 24 / 100) /* 61, 23.828125% */
#define NANBBR3_DEF_SOFT_LOSS_THRESH    (BBR_UNIT * 8 / 100) /* 20, 7.812500% */
#define NANBBR3_DEF_HARD_LOSS_THRESH    (BBR_UNIT * 16 / 100) /* 40, 15.625000% */
#define NANBBR3_DEF_PANIC_LOSS_THRESH   (BBR_UNIT * 25 / 100) /* 64, 25.000000% */
#define NANBBR3_DEF_RTT_INFLATE_TRIG    (BBR_UNIT * 175 / 100) /* 448, 1.750000x */
#define NANBBR3_DEF_BW_DROP_TRIG        (BBR_UNIT * 85 / 100) /* 217, 84.765625% */
#define NANBBR3_DEF_BETA_CUT            (BBR_UNIT * 35 / 100) /* 89, cut 34.765625% */
#define NANBBR3_DEF_LOSS_THRESH_STATIC_FALLBACK (BBR_UNIT * 12 / 100) /* 30, 11.718750% */
static const int nanbbr3_def_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = (BBR_UNIT * 140 / 100), /* 358, 1.398438x */
	[BBR_BW_PROBE_DOWN]   = (BBR_UNIT * 72 / 100), /* 184, 0.718750x */
	[BBR_BW_PROBE_CRUISE] = (BBR_UNIT * 103 / 100), /* 263, 1.027344x */
	[BBR_BW_PROBE_REFILL] = (BBR_UNIT * 112 / 100), /* 286, 1.117188x */
};
/* mean=1.065429688x, mean_with_1pct_margin=1.054775391x */

/* nanbbr3_aggr: startup=3.003906x, probe_mean=1.100586x */
#define NANBBR3_AGGR_STARTUP_PACING_GAIN (BBR_UNIT * 300 / 100 + 1) /* 769, 3.003906x */
#define NANBBR3_AGGR_STARTUP_CWND_GAIN   (BBR_UNIT * 265 / 100) /* 678, 2.648438x */
#define NANBBR3_AGGR_DRAIN_GAIN          (BBR_UNIT * 100 / 300) /* 85, 0.332031x */
#define NANBBR3_AGGR_INFLIGHT_HEADROOM   (BBR_UNIT * 20 / 100) /* 51, 19.921875% */
#define NANBBR3_AGGR_SOFT_LOSS_THRESH    (BBR_UNIT * 10 / 100) /* 25, 9.765625% */
#define NANBBR3_AGGR_HARD_LOSS_THRESH    (BBR_UNIT * 20 / 100) /* 51, 19.921875% */
#define NANBBR3_AGGR_PANIC_LOSS_THRESH   (BBR_UNIT * 28 / 100) /* 71, 27.734375% */
#define NANBBR3_AGGR_RTT_INFLATE_TRIG    (BBR_UNIT * 190 / 100) /* 486, 1.898438x */
#define NANBBR3_AGGR_BW_DROP_TRIG        (BBR_UNIT * 80 / 100) /* 204, 79.687500% */
#define NANBBR3_AGGR_BETA_CUT            (BBR_UNIT * 40 / 100) /* 102, cut 39.843750% */
#define NANBBR3_AGGR_LOSS_THRESH_STATIC_FALLBACK (BBR_UNIT * 16 / 100) /* 40, 15.625000% */
static const int nanbbr3_aggr_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = (BBR_UNIT * 148 / 100), /* 378, 1.476562x */
	[BBR_BW_PROBE_DOWN]   = (BBR_UNIT * 70 / 100), /* 179, 0.699219x */
	[BBR_BW_PROBE_CRUISE] = (BBR_UNIT * 105 / 100), /* 268, 1.046875x */
	[BBR_BW_PROBE_REFILL] = (BBR_UNIT * 118 / 100), /* 302, 1.179688x */
};
/* mean=1.100585938x, mean_with_1pct_margin=1.089580078x */


/*
 * Pseudocode for BBR2/3 dynamic loss gate.
 * Adapt field names to the exact tcp_bbr.c/tcp_nanbbr*.c port.
 *
 * static bool nanbbr_loss_gate(u32 loss_scaled, u32 sample_rtt_us,
 *                              u32 min_rtt_us, u64 bw_latest, u64 bw_ref)
 * {
 *     bool soft_loss  = loss_scaled >= NANBBR*_SOFT_LOSS_THRESH;
 *     bool hard_loss  = loss_scaled >= NANBBR*_HARD_LOSS_THRESH;
 *     bool panic_loss = loss_scaled >= NANBBR*_PANIC_LOSS_THRESH;
 *     bool rtt_bad = sample_rtt_us &&
 *                    min_rtt_us &&
 *                    sample_rtt_us >= div_u64((u64)min_rtt_us * NANBBR*_RTT_INFLATE_TRIG, BBR_UNIT);
 *     bool bw_bad = bw_latest &&
 *                   bw_ref &&
 *                   bw_latest <= div_u64(bw_ref * NANBBR*_BW_DROP_TRIG, BBR_UNIT);
 *
 *     return panic_loss || hard_loss || (soft_loss && (rtt_bad || bw_bad));
 * }
 */
