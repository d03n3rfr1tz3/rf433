# Development

## Running from the repository

```
python bin/rf433 --codes examples/rf433.conf.d check
python -m rf433 --codes examples/rf433.conf.d list
```

Everything except the real sending runs on Windows and macOS as well.

## Tests

```
python -m unittest discover -s tests
```

The tests only use the standard library and made-up codes (`tests/support.py`). They need no LIRC
device, no root and no RTL-SDR stick: the sender is tested against a fake device, the commands
against a fake transmitter and recorder. Please keep recordings of real remotes out of the tests.

## Structure

```
rf433/
  cli.py              parser built from the command list, global options, errors -> exit code
  context.py          what a command works with: options, code library, transmitter, recorder
  options.py          defaults < options file < command line
  model/              Code (values, problems, duration), Remote and RemoteCode
  codefile/           parser.py (text -> remotes and problems), writer.py, library.py (code folder)
  transmit/           windows.py (packing), lirc.py (LircTransmitter), realtime.py (CPU core, SCHED_FIFO)
  receive/            rtl433.py (Rtl433Recorder), ook.py (pulse data of rtl_433)
  signal/             cluster.py (clean), frames.py (frame extraction)
  commands/           one file per command, listed in commands/__init__.py
```

`fcntl` and the `os.sched_*` functions are only used while sending, so the rest stays portable.

## Adding a command

1. Create a class derived from `commands.base.Command` with `name`, `help`, `add_arguments()` and
   `run(args, context)`, in the fitting subfolder of `commands/`.
2. Add it to `COMMANDS` in `commands/__init__.py`.
3. Add a test in `tests/test_cli.py`.

## Extension points

- **Transmitter** (`transmit/transmitter.py`): `send(code, repeat)` returns a `SendReport`. Another
  sender (e.g. a different driver) is a new class plus a factory in `cli.py`.
- **Recorder** (`receive/recorder.py`): `record(seconds)` returns packages of values. A recorder for
  a 433 MHz receiver module on `gpio-ir-recv` would set `last_pause_reliable` and could serve a
  future `receive` command that matches incoming frames against the code library.
- **Code library** (`codefile/library.py`): independent of the command line, so a long-running
  process (e.g. an MQTT client) can load it once and send through a transmitter directly.
