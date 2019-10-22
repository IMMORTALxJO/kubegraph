#!/usr/bin/env python3
import unittest
import subprocess
import glob
import json
import os
from click.testing import CliRunner
from src.cli import KubeGraphCLI


class E2E(unittest.TestCase):

    def run_test_for_yaml(self, yaml_path):
        print("### Testing %s" % yaml_path)
        try:
            answer = json.load(open("%s-answer" % yaml_path, 'r'))
            yaml_applying = subprocess.Popen(["kubectl", "apply", "-f", yaml_path])
            yaml_applying.wait()
            runner = CliRunner()
            result = runner.invoke(KubeGraphCLI, [
                "--kubeconfig", os.getenv("KUBECONFIG", "~/.kube/config"),
                "--output-format", "json"
            ])
            cli_output = json.loads(result.output)
            self.assertEqual(cli_output, answer, yaml_path)
        finally:
            yaml_deleteion = subprocess.Popen(["kubectl", "delete", "-f", yaml_path])
            yaml_deleteion.wait()

    def test_hostnames_detection(self):
        """Test hostnames collecting"""
        for file in glob.glob("./src/tests/e2e/env_*_test.yaml"):
            self.run_test_for_yaml(file)

    def test_scheme_detection(self):
        """Test hostnames collecting"""
        for file in glob.glob("./src/tests/e2e/scheme_*_test.yaml"):
            self.run_test_for_yaml(file)


if __name__ == '__main__':
    unittest.main()
