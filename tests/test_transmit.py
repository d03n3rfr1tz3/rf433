import os
import struct
import sys
import types
import unittest
from unittest import mock

import support
from rf433.errors import Rf433Error
from rf433.model import Code
from rf433.transmit import lirc
from rf433.transmit.lirc import LIRC_SET_SEND_CARRIER, LircTransmitter


class FakeDevice:
    """Replaces fcntl and the file functions of os; records what the sender does."""

    def __init__(self, short_write=False):
        self.calls = []
        self.writes = []
        self.short_write = short_write
        self.fcntl = types.SimpleNamespace(LOCK_EX=2, flock=self.flock, ioctl=self.ioctl)

    def open(self, path, flags):
        self.calls.append(("open", path, flags))
        return 42

    def flock(self, fd, operation):
        self.calls.append(("flock", fd, operation))

    def ioctl(self, fd, request, argument):
        self.calls.append(("ioctl", fd, request, argument))

    def write(self, fd, data):
        self.writes.append(list(data))
        size = len(data) * data.itemsize
        return size - 4 if self.short_write else size

    def close(self, fd):
        self.calls.append(("close", fd))

    def patch(self, test):
        for patcher in (mock.patch.dict(sys.modules, {"fcntl": self.fcntl}),
                        mock.patch.object(lirc.os, "open", self.open),
                        mock.patch.object(lirc.os, "write", self.write),
                        mock.patch.object(lirc.os, "close", self.close),
                        mock.patch.object(lirc.realtime, "prioritize", return_value=["no SCHED_FIFO"]),
                        mock.patch.object(lirc.realtime, "wait_until")):
            patcher.start()
            test.addCleanup(patcher.stop)


class LircTransmitterTest(unittest.TestCase):
    def test_send_writes_packed_windows(self):
        device = FakeDevice()
        device.patch(self)
        warnings = []
        values = support.frame("0101")
        report = LircTransmitter("/dev/lirc-433", 3, 50, warn=warnings.append).send(Code(tuple(values)), 50)

        self.assertEqual(report.windows, [35, 15])
        self.assertEqual(device.writes, [(values * 35)[:-1], (values * 15)[:-1]])
        self.assertEqual(device.calls, [
            ("open", "/dev/lirc-433", os.O_WRONLY),
            ("flock", 42, 2),
            ("ioctl", 42, LIRC_SET_SEND_CARRIER, struct.pack("I", 0)),
            ("close", 42),
        ])
        self.assertEqual(lirc.realtime.prioritize.call_args, mock.call(3, 50))
        self.assertEqual(lirc.realtime.wait_until.call_count, 1)
        self.assertEqual(warnings, ["no SCHED_FIFO"])

    def test_short_write_is_an_error_and_closes(self):
        device = FakeDevice(short_write=True)
        device.patch(self)
        with self.assertRaisesRegex(Rf433Error, "short write"):
            LircTransmitter("/dev/lirc-433", warn=lambda text: None).send(Code((300, 9300)), 1)
        self.assertEqual(device.calls[-1], ("close", 42))

    def test_invalid_code_is_not_sent(self):
        device = FakeDevice()
        device.patch(self)
        with self.assertRaises(Rf433Error):
            LircTransmitter("/dev/lirc-433").send(Code((300, 0)), 1)
        self.assertEqual(device.calls, [])


if __name__ == "__main__":
    unittest.main()
