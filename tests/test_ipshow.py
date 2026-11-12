"""Regression tests for the standalone Python 3.12+ ipshow command."""

import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "ipshow"


class IpshowTests(unittest.TestCase):
    def setUp(self):
        self.main = runpy.run_path(str(SCRIPT))["main"]

    def run_ipshow(self, output="[]", error=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        result = subprocess.CompletedProcess(["ip"], 0, output, "")
        with patch("subprocess.run", return_value=result, side_effect=error) as run:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = self.main([])
        run.assert_called_once_with(
            ["ip", "-json", "address", "show"],
            capture_output=True, encoding="utf-8", check=True,
        )
        return code, stdout.getvalue(), stderr.getvalue()

    def test_interface_names_and_address_ownership(self):
        interfaces = [
            {
                "ifname": "lo", "link_type": "loopback", "address": "00:00:00:00:00:00",
                "addr_info": [
                    {"family": "inet", "local": "127.0.0.1", "prefixlen": 8},
                    {"family": "inet6", "local": "::1", "prefixlen": 128},
                ],
            },
        ]
        expected = (
            "lo         type loopback mac 00:00:00:00:00:00\n"
            "           ipv4 127.0.0.1/8\n"
            "           ipv6 ::1/128\n"
        )
        for name in ("br-012abc", "eth0.100", "veth0@if7", "VPN_1", "síť0"):
            interfaces.append({
                "ifname": name, "link_type": "ether", "address": "02:00:00:00:00:01",
                "addr_info": [
                    {"family": "inet", "local": "192.0.2.1", "prefixlen": 24},
                    {"family": "inet", "local": "192.0.2.2", "prefixlen": 32},
                    {"family": "inet6", "local": "2001:db8::1", "prefixlen": 64},
                ],
            })
            expected += (
                f"{name:<11}type ether mac 02:00:00:00:00:01\n"
                "           ipv4 192.0.2.1/24\n"
                "           ipv4 192.0.2.2/32\n"
                "           ipv6 2001:db8::1/64\n"
            )
        self.assertEqual(self.run_ipshow(json.dumps(interfaces)), (0, expected, ""))

    def test_unaddressed_and_point_to_point_interfaces(self):
        interfaces = [
            {"ifname": "eth0", "link_type": "ether", "address": "02:00:00:00:00:01", "addr_info": []},
            {"ifname": "tun0", "link_type": "none", "addr_info": [
                {"family": "inet", "local": "192.0.2.1", "peer": "192.0.2.2", "prefixlen": 32},
                {"family": "other"},
            ]},
            {"ifname": "unknown0"},
        ]
        self.assertEqual(self.run_ipshow(json.dumps(interfaces)), (
            0, "eth0      type ether mac 02:00:00:00:00:01\n"
            "tun0      type none mac -\n          ipv4 192.0.2.1/32\n"
            "unknown0  type unknown mac -\n", "",
        ))

    def test_empty_interfaces(self):
        self.assertEqual(self.run_ipshow(), (0, "", ""))

    def test_command_errors(self):
        for error, message in (
            (FileNotFoundError(), "install iproute2"),
            (PermissionError("Permission denied"), "Permission denied"),
            (subprocess.CalledProcessError(2, ["ip"], stderr="ip: error\n"), "ip: error"),
            (subprocess.CalledProcessError(3, ["ip"], stderr=""), "status 3"),
        ):
            with self.subTest(error=error):
                code, stdout, stderr = self.run_ipshow(error=error)
                self.assertEqual(code, 1)
                self.assertEqual(stdout, "")
                self.assertIn(message, stderr)
                self.assertNotIn("Traceback", stderr)

    def test_invalid_output_without_partial_listing(self):
        for output in ("", "not json", "{}", "null", '[{"ifname":"lo"}, {}]', '[{"ifname":"lo", "addr_info":null}]'):
            with self.subTest(output=output):
                code, stdout, stderr = self.run_ipshow(output)
                self.assertEqual(code, 1)
                self.assertEqual(stdout, "")
                self.assertIn("Invalid JSON output from ip", stderr)

    def test_help_and_invalid_arguments(self):
        for flag in ("-h", "-?", "--help", "--unknown", "eth0"):
            with self.subTest(flag=flag):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), flag],
                    capture_output=True, text=True, check=False,
                    env={"PATH": "/nonexistent"},
                )
                self.assertEqual(result.returncode, 0 if flag in ("-h", "-?", "--help") else 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_loading_does_not_run_ip(self):
        with patch("subprocess.run") as run:
            runpy.run_path(str(SCRIPT))
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
