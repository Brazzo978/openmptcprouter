# Nan / NanBBR kernel 6.6 integration manifest

Questo branch prepara due livelli distinti per l'altro agente:

1. `nanqinlang` vanilla: vecchio Nanqinlang portato a kernel 6.6 con sole patch di compatibilita.
2. Profili Nan-style: algoritmi/valori separati per test throughput-first.

## Patch integrate nella serie 6.6

Ordine patch effettivo: `997-BBRv3.patch`, `9971-tcp_nanqinlang.patch`, `9972-tcp_nanbbr3.patch`, `9973-tcp_nanbbr1.patch`, `9974-tcp_nanbbr2.patch`.

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

### `9974-tcp_nanbbr2.patch`

Runtime TCP congestion-control name: `nanbbr2`.

Scopo: profilo BBRv2 `balanced_edge`, basato sul `tcp_bbr2.c` trovato nel build tree OMR 6.6:

```text
openmptcprouter-v0.62-build/x86_64/6.6/source/build_dir/target-x86_64_musl/linux-x86_64/linux-6.6.73/net/ipv4/tcp_bbr2.c
```

La patch aggiunge una copia autonoma `tcp_nanbbr2.c`, rinominata a runtime in `nanbbr2`. L'export diagnostico usa `struct tcp_bbr_info` esteso dalla patch BBRv3 gia' presente, con `bbr_version = 2`.

Valori principali:

```c
static int bbr_high_gain = BBR_UNIT * 290 / 100 + 1;
static int bbr_startup_cwnd_gain = BBR_UNIT * 240 / 100;
static int bbr_drain_gain = BBR_UNIT * 100 / 290;

static int bbr_pacing_gain[] = {
	BBR_UNIT * 140 / 100,
	BBR_UNIT * 76 / 100,
	BBR_UNIT * 103 / 100,
	BBR_UNIT * 112 / 100,
	BBR_UNIT * 103 / 100, BBR_UNIT * 103 / 100,
	BBR_UNIT * 103 / 100, BBR_UNIT * 103 / 100
};

static u32 bbr_beta = BBR_UNIT * 30 / 100;
static u32 bbr_ecn_factor = BBR_UNIT * 1 / 3;
static u32 bbr_ecn_thresh = BBR_UNIT * 1 / 2;
static u32 bbr_ecn_reprobe_gain = BBR_UNIT * 1 / 2;
static u32 bbr_loss_thresh = BBR_UNIT * 3 / 100;
static u32 bbr_full_loss_cnt = 5;
static u32 bbr_full_ecn_cnt = 2;
static u32 bbr_inflight_headroom = BBR_UNIT * 18 / 100;
```

Nota: questa base BBRv2 usa `bbr_bw_probe_pif_gain`, non il knob BBRv3 `bbr_bw_probe_cwnd_gain`; per il primo giro `bbr_bw_probe_pif_gain` resta al default BBRv2.

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

## Config 6.6

`6.6/target/linux/generic/config-6.6` abilita:

```text
CONFIG_TCP_CONG_NANQINLANG=y
CONFIG_TCP_CONG_NANBBR1=y
CONFIG_TCP_CONG_NANBBR2=y
CONFIG_TCP_CONG_NANBBR3=y
```

Le opzioni default restano disabilitate:

```text
# CONFIG_DEFAULT_NANQINLANG is not set
# CONFIG_DEFAULT_NANBBR1 is not set
# CONFIG_DEFAULT_NANBBR2 is not set
# CONFIG_DEFAULT_NANBBR3 is not set
```

## Regole da non violare

- Non disabilitare loss response.
- Non disabilitare ECN response.
- Non disabilitare ProbeRTT.
- Non aumentare `bbr_bw_probe_cwnd_gain` nel primo giro; su `nanbbr2`, lasciare `bbr_bw_probe_pif_gain` al default BBRv2.
- Non toccare TSO/GSO/send quantum inizialmente.
- Non alzare `loss_thresh` oltre 4% senza benchmark.
- Usare `nanbbr3` come candidato principale.
- Usare `nanqinlang` vanilla, `nanbbr1`, e `nanbbr2` come benchmark/fallback.
