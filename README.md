# rf433

Sends 433 MHz OOK codes (wireless sockets, switches, doorbells …) with a simple 433 MHz transmitter
module on a GPIO pin of a Raspberry Pi. The Linux driver `gpio-ir-tx` does the timing; rf433 runs it
with carrier 0, so the pulses switch the transmitter directly and every pulse is timed by the kernel.

- Codes are kept in small text files in a LIRC-like format: one frame per code plus a repeat count.
- As many repeats as fit are packed into one write; between the writes the pause of the code is kept,
  so the receiver sees one continuous stream.
- `learn` records a remote with an RTL-SDR stick and `rtl_433` and prints the code for the code file.
- Only the Python standard library is needed (Python 3.9 or newer).

## Hardware

A 433 MHz OOK transmitter module (e.g. FS1000A) with DATA on a GPIO pin and the overlay

```
dtoverlay=gpio-ir-tx,gpio_pin=17
```

in `/boot/firmware/config.txt`. Details, wiring and the udev rule: [docs/hardware.md](docs/hardware.md).

## Installation

```
sudo git clone https://github.com/d03n3rfr1tz3/rf433.git /opt/rf433
sudo ln -s /opt/rf433/bin/rf433 /usr/local/bin/rf433
sudo mkdir -p /etc/rf433/rf433.conf.d
sudo cp /opt/rf433/examples/rf433_options.conf /etc/rf433/
```

Update with `sudo git -C /opt/rf433 pull`. Instead of the clone, `pip install .` installs the
`rf433` command as well.

## Quick start

Write a code file, e.g. `/etc/rf433/rf433.conf.d/garden.conf`:

```
begin remote
  name    Garden
  repeat  10

  begin raw_codes
    name Light_on
      300 900 900 300 300 900 900 300 300 900 300 9300

    name Light_off
      300 900 900 300 300 900 300 900 300 900 300 9300
  end raw_codes
end remote
```

Then:

```
rf433 check
rf433 list
sudo rf433 send Garden Light_on
```

Sending needs root for the real-time scheduling and the CPU binding; the other commands do not.

## Commands

| Command | Purpose |
|---|---|
| `send REMOTE CODE [--repeat N]` | send a code of the code files |
| `raw --code VALUES [--repeat N]` | send a code given on the command line |
| `list [REMOTE] [--json]` | list remotes and codes with duration and windows |
| `check` | check all code files, exit code 1 on problems |
| `info REMOTE CODE` or `info --code VALUES` | duration and windows of a code, without sending |
| `clean --code VALUES` | suggest a cleaned code: values within 25 % get the same value |
| `frame --code VALUES` | cut one frame out of a recording with repeats |
| `learn [--seconds N] [--name NAME]` | record a remote with `rtl_433` and print its code |

Global options: `--options FILE`, `--device DEVICE`, `--codes FOLDER`. Details:
[docs/commands.md](docs/commands.md).

## Documentation

- [Code files](docs/code-files.md): format of the code files
- [Options](docs/options.md): the options file
- [Commands](docs/commands.md): all commands in detail
- [Hardware](docs/hardware.md): transmitter, overlay, udev rule, receiver for `learn`
- [Development](docs/development.md): structure, tests, extension points

Flipper Zero recordings can be converted into code files with
[f0-converter](https://github.com/d03n3rfr1tz3/f0-converter).

## License

MIT, see [LICENSE](LICENSE).
