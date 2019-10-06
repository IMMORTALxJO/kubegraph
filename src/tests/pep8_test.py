#!/usr/bin/env python3
import unittest
import pycodestyle


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """Test that we conform to PEP-8."""
        style = pycodestyle.StyleGuide(config_file="setup.cfg", quiet=False)
        style.input_dir('.')
        result = style.check_files()
        self.assertEqual(result.total_errors, 0, "Found code style errors (and warnings).")


if __name__ == '__main__':
    unittest.main()
