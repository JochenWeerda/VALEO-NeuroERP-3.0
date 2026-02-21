"""
UUID v7 generator (RFC 9562) — time-ordered, sortable UUIDs.

Usage:
    from app.core.uuid7 import uuid7

    new_id = uuid7()          # -> "018e1a2b-3c4d-7xxx-8xxx-xxxxxxxxxxxx"

Layout (128 bit):
    48 bit  unix_ts_ms
    4  bit  ver  (0b0111 = 7)
    12 bit  rand_a
    2  bit  var  (0b10)
    62 bit  rand_b
"""

import os
import time


def uuid7() -> str:
    """Generate a UUID v7 string (time-ordered, RFC 9562)."""
    timestamp_ms = int(time.time() * 1000)
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF

    uuid_int = (
        (timestamp_ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0x2 << 62)
        | rand_b
    )

    h = f"{uuid_int:032x}"
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
