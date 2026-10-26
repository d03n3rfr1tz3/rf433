from __future__ import annotations

import argparse
import sys
from typing import Callable, Sequence

from . import __version__
from .commands import COMMANDS
from .context import Context
from .errors import Rf433Error
from .options import DEFAULT_OPTIONS_FILE, Options
from .receive.recorder import Recorder
from .receive.rtl433 import Rtl433Recorder
from .transmit.lirc import LircTransmitter
from .transmit.transmitter import Transmitter


def create_transmitter(options: Options) -> Transmitter:
    return LircTransmitter(options.device, options.cpu_core, options.priority,
                           warn=lambda text: print(" --> Warning: " + text))


def create_recorder(options: Options) -> Recorder:
    return Rtl433Recorder(options.learn, log=lambda text: print(" --> " + text))


def build_parser(commands) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rf433", description="433 MHz OOK sender via gpio-ir-tx (carrier 0)")
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
    parser.add_argument("--options", metavar="FILE", help="options file (default %s)" % DEFAULT_OPTIONS_FILE)
    parser.add_argument("--device", help="LIRC device of the sender, overrides the options file")
    parser.add_argument("--codes", metavar="FOLDER", help="folder of the code files, overrides the options file")
    subparsers = parser.add_subparsers(dest="command", metavar="command", required=True)
    for command in commands:
        subparser = subparsers.add_parser(command.name, help=command.help, description=command.help)
        command.add_arguments(subparser)
        subparser.set_defaults(handler=command)
    return parser


def main(argv: Sequence[str] | None = None,
         transmitter_factory: Callable[[Options], Transmitter] = create_transmitter,
         recorder_factory: Callable[[Options], Recorder] = create_recorder) -> int:
    args = build_parser([command() for command in COMMANDS]).parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        options = Options.load(args.options, device=args.device, codes=args.codes)
        return args.handler.run(args, Context(options, transmitter_factory, recorder_factory)) or 0
    except (Rf433Error, OSError) as error:
        sys.stdout.flush()
        print("Error: %s" % error, file=sys.stderr)
        return 1
