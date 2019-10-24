#!/usr/bin/env python3
import unittest
from src.utils import compare_strings, group_similars, join_strings, is_string_ignored, get_scheme_from_port, get_scheme_from_string


class Utils(unittest.TestCase):
    def test_compare_strings(self):
        """Test positive cases"""
        self.assertTrue(compare_strings("server.com", "server.com"))
        self.assertTrue(compare_strings("aserver.com", "server.com"))
        self.assertTrue(compare_strings("server.com", "aserver.com"))
        self.assertTrue(compare_strings("server.coma", "server.com"))
        self.assertTrue(compare_strings("server.com", "server.coma"))
        self.assertTrue(compare_strings("ab", "ac"))
        self.assertTrue(compare_strings("ac", "bc"))
        self.assertTrue(compare_strings("server-1.com", "server-2.com"))
        self.assertTrue(compare_strings("server-1.com", "server-10.com"))
        self.assertFalse(compare_strings("aaaaa", "a"))
        self.assertFalse(compare_strings("aaaaa", "bbbbb"))
        self.assertFalse(compare_strings("bbbbb", "aaaaa"))
        self.assertTrue(compare_strings("server-1.com", "server-10.com"))
#        self.assertTrue(compare_strings("",""))
#        self.assertFalse(compare_strings("01","10"))
#        self.assertTrue(compare_strings("abc","acd"))

    def test_group_similars(self):
        """Test positive cases"""
        self.assertEqual(group_similars(['aaaa', 'aaaa']), [{'aaaa'}])
        self.assertEqual(group_similars(['aaaa', 'aaaba']), [{'aaaa', 'aaaba'}])
        self.assertEqual(group_similars(['aaaa', 'bbbb']), [{'aaaa'}, {'bbbb'}])
        self.assertEqual(group_similars(['aaaa', 'bbbb']), [{'aaaa'}, {'bbbb'}])
        self.assertEqual(group_similars(['aaaa', 'bbbb', 'aaaba']), [{'aaaa', 'aaaba'}, {'bbbb'}])

    def test_join_strings(self):
        """Test positive cases"""
        self.assertEqual(join_strings(['aaaa', 'aaaa']), 'aaaa')
        self.assertEqual(join_strings(['aaaa', 'aaaba']), 'aaa{,b}a')
        self.assertEqual(join_strings(['server-1.com', 'server-2.com']), 'server-{1,2}.com')
        self.assertEqual(join_strings(['server-2.com', 'server-1.com']), 'server-{1,2}.com')
        self.assertEqual(join_strings(['server-1.com', 'server-10.com']), 'server-1{,0}.com')
#        self.assertEqual(join_strings('server-1.com','server-2.com','server-10.com'), 'server-{1,2,10}.com')

    def test_is_string_ignored(self):
        """Test positive cases"""
        self.assertTrue(is_string_ignored("TEST_SECRET", "secret,token,id"))
        self.assertTrue(is_string_ignored("TEST_TOKEN", "secret,token,id"))
        self.assertTrue(is_string_ignored("SERVICE_ID", "secret,token,id"))
        self.assertTrue(is_string_ignored("SERVICE_ID", "secret,token,id,"))
        self.assertFalse(is_string_ignored("SERVICE_NAME", "secret,token,id"))
        self.assertFalse(is_string_ignored("SERVICE_NAME", ""))
        self.assertFalse(is_string_ignored("SERVICE_NAME", ","))

    def test_get_scheme_from_port(self):
        """Test positive cases"""
        self.assertEqual(get_scheme_from_port('3306'), 'mysql')
        self.assertEqual(get_scheme_from_port(27017), 'mongodb')
        self.assertIsNone(get_scheme_from_port('0'))
        self.assertIsNone(get_scheme_from_port(''))

    def test_get_scheme_from_string(self):
        """Test positive cases"""
        self.assertEqual(get_scheme_from_string('MYSQL_HOST'), 'mysql')
        self.assertEqual(get_scheme_from_string('HOST_MYSQL'), 'mysql')
        self.assertIsNone(get_scheme_from_string('DATABASE_HOST'))
        self.assertIsNone(get_scheme_from_string(''))


if __name__ == '__main__':
    unittest.main()
