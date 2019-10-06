#!/usr/bin/env python3
import unittest
from src.utils import compare_strings, group_similars, join_strings


class TestCompareStrings(unittest.TestCase):
    def test_positive(self):
        """
        Test positive cases
        """
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


class TestGroupSimilars(unittest.TestCase):
    def test_positive(self):
        """
        Test positive cases
        """
        self.assertEqual(group_similars('aaaa', 'aaaa'), [{'aaaa'}])
        self.assertEqual(group_similars('aaaa', 'aaaba'), [{'aaaa', 'aaaba'}])
        self.assertEqual(group_similars('aaaa', 'bbbb'), [{'aaaa'}, {'bbbb'}])
        self.assertEqual(group_similars('aaaa', 'bbbb'), [{'aaaa'}, {'bbbb'}])
        self.assertEqual(group_similars('aaaa', 'bbbb', 'aaaba'), [{'aaaa', 'aaaba'}, {'bbbb'}])


class TestJoinStrings(unittest.TestCase):
    def test_positive(self):
        """
        Test positive cases
        """
        self.assertEqual(join_strings('aaaa', 'aaaa'), 'aaaa')
        self.assertEqual(join_strings('aaaa', 'aaaba'), 'aaa{,b}a')
        self.assertEqual(join_strings('server-1.com', 'server-2.com'), 'server-{1,2}.com')
        self.assertEqual(join_strings('server-2.com', 'server-1.com'), 'server-{1,2}.com')
        self.assertEqual(join_strings('server-1.com', 'server-10.com'), 'server-1{,0}.com')
#        self.assertEqual(join_strings('server-1.com','server-2.com','server-10.com'), 'server-{1,2,10}.com')


if __name__ == '__main__':
    unittest.main()
