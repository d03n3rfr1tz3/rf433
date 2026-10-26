# rf433

Sends 433 MHz OOK codes (wireless sockets, switches, doorbells …) with a simple 433 MHz transmitter
module on a GPIO pin of a Raspberry Pi. The Linux driver `gpio-ir-tx` does the timing; rf433 runs it
with carrier 0, so the pulses switch the transmitter directly.

Codes are kept in small text files in a LIRC-like format, one frame per code plus a repeat count.

> Work in progress: the project structure is in place, the functionality follows.

## Documentation

- [Code files](docs/code-files.md)
- [Options](docs/options.md)
- [Commands](docs/commands.md)
- [Hardware](docs/hardware.md)
- [Development](docs/development.md)

## License

MIT, see [LICENSE](LICENSE).
