import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from common import load_proxy, private_json


class ProxyFileTests(unittest.TestCase):
    def parse(self, value):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'proxy.txt'
            source.write_text(value)
            return load_proxy(source)

    def test_password_colons_preserved(self):
        result = self.parse('http://proxy.example.invalid:8080:test-user:secret:with:colons')
        self.assertEqual(result['password'], 'secret:with:colons')
        self.assertEqual(result['host'], 'proxy.example.invalid')

    def test_url_and_ipv6(self):
        result = self.parse('http://test-user:pass%3Aword@[2001:db8::1]:8080')
        self.assertEqual(result['password'], 'pass:word')
        self.assertEqual(result['host'], '2001:db8::1')

    def test_errors_redacted(self):
        for value in ['proxy.example.invalid:wrong:test-user:PRIVATE_VALUE',
                      'https://proxy.example.invalid:8080:test-user:PRIVATE_VALUE',
                      'a:80:b:PRIVATE_VALUE\nc:80:d:OTHER_VALUE']:
            with self.assertRaises(ValueError) as context:
                self.parse(value)
            self.assertNotIn('PRIVATE_VALUE', str(context.exception))
            self.assertNotIn('proxy.example.invalid', str(context.exception))

    def test_private_file_permissions(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'native-policy.json'
            private_json(target, {'schema': 1})
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
