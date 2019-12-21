#!/usr/bin/env python3
import unittest
import subprocess
import glob
import yaml
import json
import tempfile
import os
from click.testing import CliRunner
from src.cli import kubegraph_cli


class E2E(unittest.TestCase):
    pass


def generator(yaml_path):
    """Test generator function which return test function"""
    def __run_test_for_yaml(self):
        print("### Testing %s" % yaml_path)
        config = tempfile.NamedTemporaryFile()
        try:
            test_data = yaml.safe_load(open("%s" % yaml_path, 'r'))
            config.write(bytes(test_data['config'], 'utf-8'))
            config.seek(0)
            yaml_applying = subprocess.Popen(["kubectl", "apply", "-f", config.name])
            yaml_applying.wait()
            runner = CliRunner()
            cli_result = runner.invoke(kubegraph_cli, [
                "--kubeconfig", os.getenv("KUBECONFIG", "~/.kube/config"),
                "--namespace", test_data['namespace'],
                "--output", "json"
            ])
            cli_output = json.loads(cli_result.output)
            print(cli_output, test_data['answer'], yaml_path)
            self.assertEqual(cli_output, test_data['answer'], yaml_path)
        finally:
            yaml_deletion = subprocess.Popen(["kubectl", "delete", "--now", "-f", config.name])
            yaml_deletion.wait()
            config.close()
    return __run_test_for_yaml


for file in glob.glob("./tests/e2e/*.yaml"):
    setattr(E2E, 'test_%s' % os.path.basename(file), generator(file))

if __name__ == '__main__':
    unittest.main()
