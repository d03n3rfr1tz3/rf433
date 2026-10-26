# Options

rf433 reads `/etc/rf433/rf433_options.conf` if it exists. `--options FILE` reads another file
instead; that file must exist. Every option is optional, a missing or empty option keeps its default.
`--device` and `--codes` on the command line override the file.

A commented example is in [examples/rf433_options.conf](../examples/rf433_options.conf).

## `[rf433]`

| Option | Default | Meaning |
|---|---|---|
| `device` | `/dev/lirc0` | LIRC device of the 433 MHz transmitter (gpio-ir-tx) |
| `codes` | `/etc/rf433/rf433.conf.d` | folder of the code files (`*.conf`) |
| `repeat` | `10` | frames sent when neither the code nor its remote sets `repeat` |
| `max_repeat` | `100` | upper limit for every repeat, protects against typos |
| `cpu_core` | highest core | CPU core rf433 runs on while sending |
| `priority` | `50` | SCHED_FIFO priority while sending (1 to 99) |

`gpio-ir-tx` blocks the interrupts of the CPU core it runs on while it sends a write. rf433 binds
itself to one core, by default the highest one, so USB and network keep working on the others.
With an `isolcpus` or IRQ affinity setup, pick the core with `cpu_core`.

## `[learn]`

Used by `rf433 learn`, which records with `rtl_433` and an RTL-SDR stick.

| Option | Default | Meaning |
|---|---|---|
| `device` | empty | `rtl_433 -d`, e.g. `0` or `:SERIAL`; empty = the default of rtl_433 |
| `frequency` | `433.92M` | `rtl_433 -f` |
| `sample_rate` | `250k` | `rtl_433 -s` |
| `seconds` | `10` | recording time |
| `service` | empty | systemd service that uses the stick; it is stopped while recording and started again afterwards |

## Example

```
[rf433]
device = /dev/lirc-433
repeat = 10
cpu_core = 3

[learn]
device = :RTLSDR01
sample_rate = 240k
service = rtl433-mqtt.service
```

Unknown sections or options and invalid numbers are errors, so typos do not go unnoticed.
