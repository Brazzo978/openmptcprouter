# Nan / NanBBR kernel 6.6 integration manifest

Questo branch prepara due livelli distinti per l'altro agente:

1. `nanqinlang` vanilla: vecchio Nanqinlang portato a kernel 6.6 con sole patch di compatibilita.
2. Profili Nan-style: algoritmi/valori separati per test throughput-first.

## Patch integrate nella serie 6.6

### `9971-tcp_nanqinlang.patch`

Runtime TCP congestion-control name: `nanqinlang`.

Scopo: baseline vanilla Nanqinlang. Deve restare utile come confronto con il comportamento storico.

Valori principali:

```c
static const u32 bbr_probe_rtt_mode_ms = 100;
static const int bbr_high_gain  = BBR_UNIT * 3000 / 1000 + 1;
static const int bbr_drain_gain = BBR_UNIT * 1000 / 3000;
static const int bbr_cwnd_gain  = BBR_UNIT * 2;

static const int bbr_pacing_gain[] = {
	BBR_UNIT * 6 / 4,
	BBR_UNIT * 3 / 4,
	BBR_UNIT * 5 / 4, BBR_UNIT * 5 / 4, BBR_UNIT * 5 / 4,
	BBR_UNIT * 6 / 4, BBR_UNIT * 6 / 4, BBR_UNIT * 6 / 4
};

static const u32 bbr_lt_loss_thresh = 50;
```

### `9973-tcp_nanbbr1.patch`

Runtime TCP congestion-control name: `nanbbr1`.

Scopo: profilo BBRv1/Nanqinlang `balanced_edge`, separato dal vanilla per permettere benchmark A/B.

Valori principali:

```c
static const u32 bbr_probe_rtt_mode_ms = 150;
static const int bbr_high_gain  = BBR_UNIT * 295 / 100 + 1;
static const int bbr_drain_gain = BBR_UNIT * 100 / 295;
static const int bbr_cwnd_gain  = BBR_UNIT * 2;

static const int bbr_pacing_gain[] = {
	BBR_UNIT * 145 / 100,
	BBR_UNIT * 3 / 4,
	BBR_UNIT * 110 / 100, BBR_UNIT * 110 / 100, BBR_UNIT * 110 / 100,
	BBR_UNIT * 130 / 100, BBR_UNIT * 130 / 100, BBR_UNIT * 130 / 100
};

static const u32 bbr_lt_loss_thresh = BBR_UNIT * 5 / 100;
```

### `9972-tcp_nanbbr3.patch`

Runtime TCP congestion-control name: `nanbbr3`.

Scopo: profilo BBRv3 `balanced_edge`, da usare come candidato principale per OMR 6.6.

Valori principali:

```c
static const int bbr_startup_pacing_gain = BBR_UNIT * 295 / 100 + 1;
static const int bbr_startup_cwnd_gain = BBR_UNIT * 250 / 100;
static const int bbr_drain_gain = BBR_UNIT * 100 / 295;

static const int bbr_pacing_gain[] = {
	BBR_UNIT * 145 / 100,
	BBR_UNIT * 3 / 4,
	BBR_UNIT * 105 / 100,
	BBR_UNIT * 115 / 100,
};

static const u32 bbr_beta = BBR_UNIT * 30 / 100;
static const u32 bbr_ecn_factor = BBR_UNIT * 1 / 3;
static const u32 bbr_ecn_thresh = BBR_UNIT * 1 / 2;
static const u32 bbr_ecn_reprobe_gain = BBR_UNIT * 1 / 2;
static const u32 bbr_loss_thresh = BBR_UNIT * 3 / 100;
static const u32 bbr_full_loss_cnt = 5;
static const u32 bbr_full_ecn_cnt = 2;
static const u32 bbr_inflight_headroom = BBR_UNIT * 16 / 100;
static const u32 bbr_bw_probe_cwnd_gain = 1;
```

## NanBBR2

`nanbbr2` non e' ancora integrato come patch kernel in questa serie.

Motivo: serve prima una base BBR2 pulita e applicabile su kernel 6.6. Dopo quel port, applicare il profilo `balanced_edge` gia' calcolato in `docs/nanbbr_final_profiles.yaml` e riassunto in `docs/nanbbr_codex_final_brief.md`.

Valori da applicare quando la base BBR2 e' pronta:

```c
static const int bbr_startup_pacing_gain = BBR_UNIT * 290 / 100 + 1;
static const int bbr_startup_cwnd_gain = BBR_UNIT * 240 / 100;
static const int bbr_drain_gain = BBR_UNIT * 100 / 290;

static const int bbr_pacing_gain[] = {
	[BBR_BW_PROBE_UP]     = BBR_UNIT * 140 / 100,
	[BBR_BW_PROBE_DOWN]   = BBR_UNIT * 76 / 100,
	[BBR_BW_PROBE_CRUISE] = BBR_UNIT * 103 / 100,
	[BBR_BW_PROBE_REFILL] = BBR_UNIT * 112 / 100,
};

static const int bbr_inflight_headroom = BBR_UNIT * 18 / 100;
static const int bbr_loss_thresh = BBR_UNIT * 3 / 100;
static const int bbr_beta = BBR_UNIT * 30 / 100;
static const int bbr_ecn_factor = BBR_UNIT * 1 / 3;
static const int bbr_ecn_thresh = BBR_UNIT * 1 / 2;
static const int bbr_ecn_reprobe_gain = BBR_UNIT * 1 / 2;
static const int bbr_full_loss_cnt = 5;
static const int bbr_full_ecn_cnt = 2;
static const int bbr_bw_probe_cwnd_gain = 1;
```

## Config 6.6

`6.6/target/linux/generic/config-6.6` abilita:

```text
CONFIG_TCP_CONG_NANQINLANG=y
CONFIG_TCP_CONG_NANBBR1=y
CONFIG_TCP_CONG_NANBBR3=y
```

Le opzioni default restano disabilitate:

```text
# CONFIG_DEFAULT_NANQINLANG is not set
# CONFIG_DEFAULT_NANBBR1 is not set
# CONFIG_DEFAULT_NANBBR3 is not set
```

## Regole da non violare

- Non disabilitare loss response.
- Non disabilitare ECN response.
- Non disabilitare ProbeRTT.
- Non aumentare `bbr_bw_probe_cwnd_gain` nel primo giro.
- Non toccare TSO/GSO/send quantum inizialmente.
- Non alzare `loss_thresh` oltre 4% senza benchmark.
- Usare `nanbbr3` come candidato principale.
- Usare `nanqinlang` vanilla e `nanbbr1` come benchmark/fallback.
