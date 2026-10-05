"""Offline STARTTLS boundary regression; needs aiosmtplib and openssl.

Runs an ephemeral loopback SMTP server with real TLS, never sends mail.
GHSA-vxj7-4xrp-5vr4: plaintext replies must not cross the TLS boundary.
"""
import asyncio
import ssl
import subprocess
import tempfile
import unittest
from pathlib import Path

from aiosmtplib import SMTP


class StartTLSBoundaryTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cert = Path(cls.temp.name) / "cert.pem"
        key = Path(cls.temp.name) / "key.pem"
        subprocess.run(
            ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
             "-keyout", str(key), "-out", str(cert), "-days", "1",
             "-subj", "/CN=localhost", "-addext", "subjectAltName=IP:127.0.0.1"],
            check=True, capture_output=True,
        )
        cls.server_tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        cls.server_tls.load_cert_chain(cert, key)
        cls.client_tls = ssl.create_default_context(cafile=str(cert))

    async def check_upgrade(self, inject):
        completed = asyncio.get_running_loop().create_future()

        async def serve(reader, writer):
            try:
                writer.write(b"220 localhost ready\r\n")
                await writer.drain()
                self.assertTrue((await reader.readline()).startswith(b"EHLO "))
                writer.write(b"250-localhost\r\n250 STARTTLS\r\n")
                await writer.drain()
                self.assertEqual(await reader.readline(), b"STARTTLS\r\n")
                # One write reproduces the advisory's coalesced plaintext replies.
                reply = b"220 Begin TLS\r\n"
                if inject:
                    reply += b"250 injected-plaintext\r\n"
                writer.write(reply)
                await writer.drain()
                await writer.start_tls(self.server_tls, ssl_handshake_timeout=5)
                self.assertTrue((await reader.readline()).startswith(b"EHLO "))
                writer.write(b"250 authenticated-tls-reply\r\n")
                await writer.drain()
                completed.set_result(None)
                await reader.read()
            except Exception as exc:
                if not completed.done():
                    completed.set_exception(exc)
            finally:
                writer.close()

        server = await asyncio.start_server(serve, "127.0.0.1", 0)
        async with server:
            client = SMTP(hostname="127.0.0.1", port=server.sockets[0].getsockname()[1],
                          start_tls=False, tls_context=self.client_tls, timeout=5)
            try:
                await client.connect()
                await client.starttls()
                response = await client.ehlo()
                await asyncio.wait_for(completed, 5)
                self.assertEqual(response.code, 250)
                self.assertEqual(response.message, "authenticated-tls-reply")
            finally:
                client.close()

    async def test_clean_starttls_upgrade(self):
        await self.check_upgrade(inject=False)

    async def test_plaintext_response_cannot_cross_tls_boundary(self):
        await self.check_upgrade(inject=True)


if __name__ == "__main__":
    unittest.main()
