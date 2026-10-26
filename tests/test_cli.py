import contextlib
import io
import json
import os
import shutil
import tempfile
import textwrap
import unittest

import support
from rf433.cli import main
from rf433.options import LearnOptions
from rf433.receive.recorder import Recorder
from rf433.receive.rtl433 import Rtl433Recorder
from rf433.transmit.transmitter import SendReport, Transmitter
from rf433.transmit.windows import plan_windows

ON = support.frame("010110")
OFF = support.frame("010101")
ALL = support.frame("111111")


class FakeTransmitter(Transmitter):
    def __init__(self, sent):
        self.sent = sent

    def send(self, code, repeat):
        self.sent.append((list(code.values), repeat))
        return SendReport(plan_windows(code, repeat), 1500000)


class FakeRecorder(Recorder):
    def __init__(self, packages):
        self.packages = packages

    def record(self, seconds):
        return self.packages


class CliTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory)
        self.codes = os.path.join(self.directory, "codes")
        os.mkdir(self.codes)
        self.options = self.write("options.conf", "")
        self.write("codes/garden.conf", support.remote_text("Garden", [
            support.code_text("On", ON), support.code_text("Off", OFF), support.code_text("All", ALL, 40)], 20))
        self.sent = []
        self.packages = []

    def write(self, name, text):
        path = os.path.join(self.directory, name)
        with open(path, "w", encoding="utf-8") as file:
            file.write(textwrap.dedent(text))
        return path

    def run_cli(self, *argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(["--options", self.options, "--codes", self.codes] + list(argv),
                        transmitter_factory=lambda options: FakeTransmitter(self.sent),
                        recorder_factory=lambda options: FakeRecorder(self.packages))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_send_uses_repeat_of_code_remote_or_option(self):
        self.assertEqual(self.run_cli("send", "Garden", "On")[0], 0)
        self.assertEqual(self.run_cli("send", "Garden", "All")[0], 0)
        self.assertEqual(self.run_cli("send", "Garden", "All", "--repeat", "3")[0], 0)
        self.assertEqual(self.sent, [(ON, 20), (ALL, 40), (ALL, 3)])

        self.write("codes/garden.conf", support.remote_text("Garden", [support.code_text("On", ON)]))
        self.options = self.write("options.conf", "[rf433]\nrepeat = 7\n")
        self.run_cli("send", "Garden", "On")
        self.assertEqual(self.sent[-1], (ON, 7))

    def test_send_output(self):
        code, stdout, stderr = self.run_cli("send", "Garden", "On")
        self.assertEqual(stdout.splitlines(), [
            " --> Sending Garden On: 16.8 ms x 20 = 1 window (20)",
            " --> Done, pauses between windows at most 1.500 ms late",
        ])
        self.assertEqual(stderr, "")

    def test_send_unknown_code_shows_problems(self):
        self.write("codes/broken.conf", "begin remote\n")
        code, stdout, stderr = self.run_cli("send", "Garden", "Nope")
        self.assertEqual(code, 1)
        self.assertIn(" --> Warning: broken.conf:1: 'end remote' is missing", stdout)
        self.assertEqual(stderr.strip(), "Error: unknown code Garden Nope (known: On, Off, All)")
        self.assertEqual(self.sent, [])

    def test_send_rejects_repeat_above_maximum(self):
        code, stdout, stderr = self.run_cli("send", "Garden", "On", "--repeat", "101")
        self.assertEqual(code, 1)
        self.assertIn("repeat must be a number from 1 to 100", stderr)
        self.assertEqual(self.sent, [])

    def test_raw(self):
        code, stdout, stderr = self.run_cli("raw", "--code", "300,900,300,9300", "--repeat", "2")
        self.assertEqual(code, 0)
        self.assertEqual(self.sent, [([300, 900, 300, 9300], 2)])

    def test_check_and_list(self):
        code, stdout, stderr = self.run_cli("check")
        self.assertEqual((code, stdout.splitlines()), (0, ["garden.conf: Garden, 3 codes", "OK"]))

        code, stdout, stderr = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertEqual(stdout.splitlines()[0], "Garden (garden.conf)")
        self.assertIn("All                  16.8 ms x 40 = 2 windows (30+10)", stdout)

    def test_check_reports_problems(self):
        self.write("codes/broken.conf", """\
            begin remote
              name Broken
              begin raw_codes
                name A
                  300 900 300
              end raw_codes
            end remote
            """)
        code, stdout, stderr = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("broken.conf:5: Broken A: code must end with a pause", stdout)

    def test_list_json(self):
        code, stdout, stderr = self.run_cli("list", "--json")
        self.assertEqual(code, 0)
        result = json.loads(stdout)
        self.assertEqual(result["problems"], [])
        remote = result["remotes"][0]
        self.assertEqual((remote["name"], remote["file"], remote["repeat"]), ("Garden", "garden.conf", 20))
        self.assertEqual(remote["codes"][2], {"name": "All", "repeat": 40, "values": ALL, "duration_us": sum(ALL)})

    def test_info(self):
        code, stdout, stderr = self.run_cli("info", "Garden", "On")
        self.assertEqual(stdout.splitlines(), [
            "Garden On: 14 values, pulse first, pause at the end 9300 µs",
            "Duration 16.8 ms, at most 30 per window",
            "16.8 ms x 20 = 1 window (20)",
        ])

    def test_clean_and_frame(self):
        code, stdout, stderr = self.run_cli("clean", "--code", ",".join(map(str, support.jitter(ON))))
        self.assertEqual(stdout.splitlines()[-1], " ".join(map(str, ON)))

        repeats = ",".join(map(str, OFF * 3))
        code, stdout, stderr = self.run_cli("frame", "--code", repeats)
        self.assertEqual(stdout.splitlines()[-1], " ".join(map(str, OFF)))

    def test_learn_prints_code_block(self):
        package = []
        for index in range(4):
            package += support.jitter(ON)
        self.packages = [package]
        code, stdout, stderr = self.run_cli("learn", "--name", "Garage")
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stdout.splitlines()[-2:], ["    name Garage", "      " + " ".join(map(str, ON))])

    def test_learn_without_signal(self):
        code, stdout, stderr = self.run_cli("learn")
        self.assertEqual((code, stderr.strip()), (1, "Error: nothing received"))

    def test_options_file_errors(self):
        self.options = self.write("options.conf", "[rf433]\nrepeats = 5\n")
        code, stdout, stderr = self.run_cli("check")
        self.assertEqual(code, 1)
        self.assertIn("unknown option repeats", stderr)


class Rtl433CommandTest(unittest.TestCase):
    def test_device_is_optional(self):
        recorder = Rtl433Recorder(LearnOptions())
        self.assertEqual(recorder.command("x.ook", 5),
                         ["rtl_433", "-f", "433.92M", "-s", "250k", "-R", "0", "-A", "-w", "x.ook", "-T", "5"])
        recorder = Rtl433Recorder(LearnOptions(device=":STICK", sample_rate="240k"))
        self.assertEqual(recorder.command("x.ook", 5)[:7], ["rtl_433", "-d", ":STICK", "-f", "433.92M", "-s", "240k"])


if __name__ == "__main__":
    unittest.main()
