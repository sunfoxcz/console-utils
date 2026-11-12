"""Regression tests for the standalone Python 3.12+ diff commands."""

import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ("inidiff", "xmldiff")


class DiffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def run_diff(self, script, left, right, *args, env=None):
        first = self.directory / "left"
        second = self.directory / "right"
        first.write_text(left, encoding="utf-8")
        second.write_text(right, encoding="utf-8")
        command = [sys.executable, str(ROOT / script), str(first), str(second)]
        if script == "xmldiff":
            command.append("//item")
        environment = os.environ.copy()
        for name in ("NO_COLOR", "FORCE_COLOR"):
            environment.pop(name, None)
        environment.update(env or {})
        return subprocess.run(
            [*command, *args], capture_output=True, text=True, env=environment, check=False
        )

    def assert_success(self, result, expected):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected)

    def test_color_priority_and_tty_detection(self):
        cases = (
            ({}, False, False, False),
            ({}, True, False, True),
            ({"NO_COLOR": ""}, True, False, True),
            ({"FORCE_COLOR": ""}, False, False, False),
            ({"NO_COLOR": "0"}, True, False, False),
            ({"NO_COLOR": "1"}, True, False, False),
            ({"FORCE_COLOR": "0"}, False, False, True),
            ({"FORCE_COLOR": "1"}, False, False, True),
            ({"NO_COLOR": "", "FORCE_COLOR": "yes"}, False, False, True),
            ({"NO_COLOR": "yes", "FORCE_COLOR": "yes"}, True, False, False),
            ({"FORCE_COLOR": "yes"}, True, True, False),
            ({"FORCE_COLOR": "yes"}, False, True, False),
            ({}, True, True, False),
        )
        for script in SCRIPTS:
            use_color = runpy.run_path(str(ROOT / script))["use_color"]
            for env, tty, flag, expected in cases:
                with self.subTest(script=script, env=env, tty=tty, flag=flag):
                    with patch.dict(os.environ, env, clear=True), patch("sys.stdout") as out:
                        out.isatty.return_value = tty
                        self.assertEqual(use_color(flag), expected)

    def test_cli_color_control(self):
        inputs = {
            "inidiff": ("[s]\nx=old", "[s]\nx=new"),
            "xmldiff": ("<item><x>old</x></item>", "<item><x>new</x></item>"),
        }
        for script, (left, right) in inputs.items():
            plain = self.run_diff(script, left, right)
            self.assertEqual(plain.returncode, 0, plain.stderr)
            self.assertNotIn("\033[", plain.stdout)
            for value in ("1", "0", "anything"):
                with self.subTest(script=script, force=value):
                    colored = self.run_diff(script, left, right, env={"FORCE_COLOR": value})
                    self.assertEqual(colored.returncode, 0, colored.stderr)
                    self.assertIn("\033[31m< x", colored.stdout)
                    self.assertIn("\033[32m> x", colored.stdout)
                    self.assertEqual(colored.stdout.count("\033[0m"), 2)
            for args, env in (
                (("--no-color",), {"FORCE_COLOR": "1"}),
                ((), {"NO_COLOR": "0", "FORCE_COLOR": "1"}),
                ((), {"NO_COLOR": "", "FORCE_COLOR": ""}),
            ):
                with self.subTest(script=script, args=args, env=env):
                    result = self.run_diff(script, left, right, *args, env=env)
                    self.assert_success(result, plain.stdout)

    def test_ini_differences_and_literal_values(self):
        result = self.run_diff(
            "inidiff",
            "[main]\nsame=yes\nchanged=a=b%\nremoved=old\n[removed]\na=1\n",
            "[main]\nsame=yes\nchanged=ab%\nadded=new\n[added]\nb=2\n",
        )
        self.assert_success(
            result,
            "[main]\n< changed = a=b%\n> changed = ab%\n- removed = old\n"
            "+ added = new\n\n- [removed]\n- a = 1\n\n+ [added]\n+ b = 2\n\n",
        )

    def test_ini_comments_order_bom_and_case(self):
        result = self.run_diff(
            "inidiff",
            "\ufeff; comment\n[s]\nKey = česky\nkey=other\n# comment\nempty\n",
            "[s]\nempty=\nkey=other\nKey=česky\n",
        )
        self.assert_success(result, "")

    def test_ini_global_keys_and_repeated_sections(self):
        result = self.run_diff(
            "inidiff", "global=old\n[s]\na=1\n[s]\nb=2", "global=new\n[s]\nb=2\na=1"
        )
        self.assert_success(result, "< global = old\n> global = new\n\n")

    def test_ini_empty_sections(self):
        self.assert_success(
            self.run_diff("inidiff", "[removed]\n[common]\n", "[common]\n[added]\n"),
            "- [removed]\n\n+ [added]\n\n",
        )

    def test_ini_invalid_content(self):
        for content in ("[broken", "[ ]", "[s]\n=value"):
            with self.subTest(content=content):
                result = self.run_diff("inidiff", content, "")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn(":1:" if content.startswith("[") and "\n" not in content else ":2:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_xml_match_by_tag_and_ignore(self):
        result = self.run_diff(
            "xmldiff",
            "<root><item><id>1</id><x>same</x><time>old</time></item>"
            "<item><id>2</id><x>old</x></item></root>",
            "<root><item><id>2</id><x>new</x></item>"
            "<item><id>1</id><time>new</time><x>same</x></item></root>",
            "-c", "id", "-i", " time, id, ",
        )
        self.assert_success(result, "id: 2\n< x: old\n> x: new\n")

    def test_xml_added_and_removed_records_and_fields(self):
        result = self.run_diff(
            "xmldiff",
            "<root><item><id>1</id><old/></item><item><id>2</id></item></root>",
            "<root><item><id>1</id><new/></item><item><id>3</id></item></root>",
            "--compare-tag", "id",
        )
        self.assert_success(
            result, "id: 1\n- old: \n+ new: \n- id: 2\n- id: 2\n+ id: 3\n+ id: 3\n"
        )

    def test_xml_default_matching_by_position(self):
        self.assert_success(
            self.run_diff(
                "xmldiff", "<root><item/><item><x>old</x></item></root>",
                "<root><item/><item><x>new</x></item></root>",
            ),
            "position: 2\n< x: old\n> x: new\n",
        )

    def test_xml_nested_unicode_and_indentation(self):
        self.assert_success(
            self.run_diff(
                "xmldiff", "<item><x>\n  <a>česky</a>\n  <b/>\n</x></item>",
                "<item><x><a>česky</a><b/></x></item>",
            ),
            "",
        )
        self.assert_success(
            self.run_diff(
                "xmldiff", "<item><x>before<a/> old</x></item>",
                "<item><x>before<a/> new</x></item>",
            ),
            "position: 1\n< x: before<a/> old\n> x: before<a/> new\n",
        )

    def test_xml_invalid_keys(self):
        for xml in (
            "<root><item/><item/></root>",
            "<root><item><id/></item></root>",
            "<root><item><id>1</id></item><item><id>1</id></item></root>",
        ):
            with self.subTest(xml=xml):
                result = self.run_diff("xmldiff", xml, xml, "-c", "id")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)

    def test_xml_invalid_xml_and_xpath(self):
        for xml, xpath in (("<broken", "//item"), ("<item/>", "["),
                           ("<item/>", "count(//item)"), ("<item/>", "//item/@id")):
            with self.subTest(xml=xml, xpath=xpath):
                if xpath == "//item/@id":
                    xml = '<item id="1"/>'
                file = self.directory / "xml"
                file.write_text(xml, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(ROOT / "xmldiff"), str(file), str(file), xpath],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)

    def test_help_and_argument_errors(self):
        for script in SCRIPTS:
            for flag in ("-h", "-?", "--help"):
                with self.subTest(script=script, flag=flag):
                    result = subprocess.run(
                        [sys.executable, str(ROOT / script), flag],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("--no-color", result.stdout)
            for args in ([], ["missing"], ["--unknown"]):
                with self.subTest(script=script, args=args):
                    result = subprocess.run(
                        [sys.executable, str(ROOT / script), *args],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn("Traceback", result.stderr)

    def test_unreadable_files(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                args = [str(self.directory / "missing"), str(self.directory)]
                if script == "xmldiff":
                    args.append("//item")
                result = subprocess.run(
                    [sys.executable, str(ROOT / script), *args],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
