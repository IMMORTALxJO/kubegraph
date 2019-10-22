#!/usr/bin/env python3
import unittest
from src.resources import get_scheme_from_port, get_scheme_from_name, get_port_from_environment_vars


class Resources(unittest.TestCase):
    def test_get_port_from_environment_vars(self):
        """Test positive cases"""
        self.assertEqual(get_port_from_environment_vars('db_host',
                                                        [
                                                            ('db_host', False),
                                                            ('db_username', False),
                                                            ('db_port', '3306')
                                                        ]
                                                        ), '3306')
        self.assertFalse(get_port_from_environment_vars('db_host',
                                                        [
                                                            ('db_host', False),
                                                            ('db_username', False),
                                                        ]
                                                        ))

    def test_get_scheme_from_port(self):
        """Test positive cases"""
        self.assertEqual(get_scheme_from_port('3306'), 'mysql')
        self.assertEqual(get_scheme_from_port(27017), 'mongodb')
        self.assertFalse(get_scheme_from_port('0'))

    def test_get_scheme_from_name(self):
        """Test positive cases"""
        self.assertEqual(get_scheme_from_name('MYSQL_HOST'), 'mysql')
        self.assertEqual(get_scheme_from_name('HOST_MYSQL'), 'mysql')
        self.assertFalse(get_scheme_from_name('DATABASE_HOST'))


if __name__ == '__main__':
    unittest.main()
