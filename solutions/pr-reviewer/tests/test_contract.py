import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from claude_review import cli

GOOD = """## Summary
The application now handles missing records explicitly. Existing response fields remain available.
## Risks
- The supplied patch does not show concurrent request behavior.
## Suggestions
- Add a regression test for missing records.
## Confidence
Low"""


class ContractTests(unittest.TestCase):
    def test_valid_two_and_three_sentence_review(self):
        self.assertEqual(cli.validate_review(GOOD), GOOD)
        cli.validate_review(GOOD.replace("remain available.", "remain available. Tests still need execution."))

    def test_rejects_bad_summary_lengths_and_bullets(self):
        for summary in ["A change.", "- This is a sufficiently lengthy change. It adds behavior.",
                        "First sentence adds behavior. Second sentence adds behavior. Third sentence adds behavior. Fourth sentence adds behavior."]:
            output = GOOD.replace(GOOD.split("## Summary\n")[1].split("\n## Risks")[0], summary)
            with self.subTest(summary=summary), self.assertRaises(cli.ReviewError):
                cli.validate_review(output)

    def test_rejects_prose_or_empty_findings(self):
        for output in [GOOD.replace("- The supplied", "The supplied"),
                       GOOD.replace("- Add a regression test for missing records.", "")]:
            with self.assertRaises(cli.ReviewError):
                cli.validate_review(output)

    def test_rejects_wrong_confidence_or_sections(self):
        for output in [GOOD.replace("\nLow", "\n90%"),
                       GOOD.replace("\nLow", "\n- High"),
                       GOOD + "\n## Extra\nText",
                       GOOD.replace("## Risks", "## Suggestions"),
                       "Some preamble\n" + GOOD]:
            with self.subTest(output=output), self.assertRaises(cli.ReviewError):
                cli.validate_review(output)

    def test_rejects_active_hidden_and_control_output(self):
        for extra in ["<script>alert(1)</script>", "![tracking](https://example.org)", "\x1b[31m", "\u202e", "<!--hidden-->"]:
            with self.subTest(extra=extra), self.assertRaises(cli.ReviewError):
                cli.validate_review(GOOD.replace("The application", extra+"The application"))

    def test_rejects_oversized_output(self):
        with self.assertRaises(cli.ReviewError):
            cli.validate_review("x"*(cli.MAX_CLAUDE_OUTPUT+1))

    def test_claude_is_default(self):
        pr = {"title":"Example", "head":{"sha":"abc"}, "changed_files":0}
        with patch.object(cli.GitHub, "fetch", return_value=(pr, [], False)), \
                patch.object(cli, "run_claude", return_value=Mock(returncode=0, stdout=GOOD)) as run, \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(["--pr","https://github.com/a/b/pull/1"]), 0)
        run.assert_called_once()
        self.assertIn("Head SHA: abc", output.getvalue())

    def test_real_runner_private_cwd_and_environment_filter(self):
        command = (sys.executable, "-c",
                   "import json,os,sys; data=sys.stdin.read(); print(json.dumps({'stdin':data,'cwd_empty':not os.listdir('.'),'secret_present':'UNRELATED_SECRET' in os.environ}))")
        with patch.object(cli, "CLAUDE_ARGS", command), \
                patch.dict(os.environ, {"UNRELATED_SECRET":"synthetic"}):
            result = cli.run_claude("test data")
        self.assertEqual(result.returncode, 0)
        value = json.loads(result.stdout)
        self.assertEqual(value, {"stdin":"test data","cwd_empty":True,"secret_present":False})

    def test_real_runner_caps_both_streams(self):
        for stream in ["stdout", "stderr"]:
            command = (sys.executable, "-c", "import sys; sys."+stream+".write('x'*200000)")
            with self.subTest(stream=stream), patch.object(cli, "CLAUDE_ARGS", command):
                with self.assertRaisesRegex(cli.ReviewError, "128 KiB"):
                    cli.run_claude("")

    def test_real_runner_timeout(self):
        command = (sys.executable, "-c", "import time; time.sleep(3)")
        with patch.object(cli, "CLAUDE_ARGS", command), patch.object(cli, "CLAUDE_TIMEOUT", 0.05):
            with self.assertRaises(cli.subprocess.TimeoutExpired):
                cli.run_claude("")
