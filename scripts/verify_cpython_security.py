"""Offline behavior regressions for the CPython runtime security backports."""
import io
import poplib
import unittest
import urllib.request
import zipfile


class RuntimeSecurityTests(unittest.TestCase):
    def test_pop3_rejects_control_characters_before_writing(self):
        client = object.__new__(poplib.POP3)
        client._debugging = 0
        client.encoding = "utf-8"
        written = []
        client._putline = written.append
        for control in ("\r", "\n", "\x00", "\x7f"):
            with self.subTest(control=repr(control)):
                with self.assertRaises(ValueError):
                    client._putcmd("USER test" + control + "QUIT")
        self.assertEqual(written, [])
        client._putcmd("USER test")
        self.assertEqual(written, [b"USER test"])

    def test_credentials_do_not_cross_url_scheme(self):
        for manager_type in (urllib.request.HTTPPasswordMgr,
                             urllib.request.HTTPPasswordMgrWithDefaultRealm,
                             urllib.request.HTTPPasswordMgrWithPriorAuth):
            for scheme, other in (("https", "http"), ("http", "https")):
                with self.subTest(manager=manager_type.__name__, scheme=scheme):
                    manager = manager_type()
                    manager.add_password(None, scheme + "://example.com/", "test", "dummy")
                    self.assertEqual(manager.find_user_password(None, other + "://example.com/"), (None, None))
                    self.assertEqual(manager.find_user_password(None, scheme + "://example.com/"), ("test", "dummy"))

    def test_idna_uses_unicode_32_case_mapping(self):
        for value, expected in (("\u13a0\u13a0", b"xn--58da"),
                                ("\u10a0.", b"xn--7md."),
                                ("\u04c0.example", b"xn--d5a.example"),
                                ("\u2183.example.", b"xn--q5g.example.")):
            with self.subTest(value=ascii(value)):
                self.assertEqual(value.encode("idna"), expected)

    def test_zip_decompression_is_bounded_and_complete(self):
        payload = b"\0" * (4 * 1024 * 1024)
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED,
                       zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA):
            with self.subTest(compression=method):
                archive = io.BytesIO()
                with zipfile.ZipFile(archive, "w", compression=method) as writer:
                    writer.writestr("data", payload)
                with zipfile.ZipFile(io.BytesIO(archive.getvalue())) as reader:
                    with reader.open("data") as member:
                        first = member._read1(100)
                        self.assertLessEqual(len(first), member.MIN_READ_SIZE)
                        self.assertEqual(first + member.read(), payload)


if __name__ == "__main__":
    unittest.main()
