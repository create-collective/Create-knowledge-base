# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Create-knowledge-base contributors
"""Offline tests for naya_cdc.py: vendor frames, captured shapes, and a fake port.
No keyboard, no pyserial needed. Run: python test_naya_cdc.py"""
import struct
import unittest

import naya_cdc as n

H = bytes.fromhex


class FakeSerial:
    """Answers each written frame with a scripted reply (bytes), one byte per read call,
    the way a USB capture shows the IN endpoint."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.written = []
        self.pending = bytearray()

    @property
    def in_waiting(self):
        return 1 if self.pending else 0

    def write(self, data):
        self.written.append(bytes(data))
        if self.replies:
            self.pending += self.replies.pop(0)

    def read(self, k=1):
        out = bytes(self.pending[:1])
        del self.pending[:1]
        return out

    def close(self):
        pass


def reply(category, subcmd, status, payload=b"", sender=0x50, remaining=0):
    data = bytes([subcmd >> 8, subcmd & 0xFF, status]) + payload
    return bytes([0xAA, sender, 0x00, remaining, category, len(data)]) + data + bytes([n.xor8(data), 0x04])


class Vectors(unittest.TestCase):
    def test_vendor_opener_and_version_request(self):
        # NayaCore's own port-detector frames (strings of NayaCore 6.11.0)
        self.assertEqual(n.build_frame(n.LEFT, 0xFE, 0x1001), H("aa 00 50 00 fe 03 10 01 00 11 04"))
        self.assertEqual(n.build_frame(n.RIGHT, 0xFE, 0x1001), H("aa 00 51 00 fe 03 10 01 00 11 04"))
        self.assertEqual(n.build_frame(n.LEFT, 0xFE, 0x1002), H("aa 00 50 00 fe 03 10 02 00 12 04"))

    def test_vendor_reply_left_detected(self):
        f = n.parse_frame(H("aa 50 00 00 fe 03 10 01 00 11 04"))
        self.assertEqual((f.sender, f.dest, f.category, f.subcmd, f.status), (0x50, 0x00, 0xFE, 0x1001, 0x00))

    def test_checksum_excludes_size(self):
        self.assertEqual(n.xor8(H("10 01 00")), 0x11)          # vendor frame
        self.assertEqual(n.xor8(H("03 10 01 00")), 0x12)       # what a sum over the size byte gives

    def test_version_reply_341(self):
        raw = H("aa 50 00 00 fe 07 10 02 00 00 03 29 00 38 04")
        f = n.parse_frame(raw)
        self.assertEqual(f.status, 0x00)
        self.assertEqual(f.payload, H("00 03 29 00"))
        self.assertEqual(n.fw_version(f), "3.41.0")
        self.assertEqual(raw[-2], 0x38)

    def test_read_layer_requests(self):
        self.assertEqual(n.build_frame(n.LEFT, 0x30, 0x1003, b"\x00"), H("aa 00 50 00 30 04 10 03 00 00 13 04"))
        self.assertEqual(n.build_frame(n.LEFT, 0x30, 0x1003, b"\x00", flags=0x01), H("aa 00 50 00 30 04 10 03 01 00 12 04"))

    def test_key_write(self):
        frame = n.build_frame(n.LEFT, 0x30, 0x1004, b"\x00" + n.key_press(0x20, 0x05))
        self.assertEqual(frame, H("aa 00 50 00 30 0b 10 04 00 00 20 01 04 05 00 07 00 33 04"))

    def test_stock_timeouts(self):
        self.assertEqual(struct.pack("<3I", 90000, 300000, 30000), H("90 5f 01 00 e0 93 04 00 30 75 00 00"))

    def test_split_stream_resync(self):
        good = H("aa500000fe07100200000329003804")
        buf = bytearray(b"\x00\xaa\x13" + good + good[:5])
        frames = n.split_stream(buf)
        self.assertEqual(frames, [good])
        self.assertEqual(bytes(buf), good[:5])

    def test_records_and_led_entries(self):
        body = n.key_press(0x20, 0x05) + H("2e0700")
        self.assertEqual(list(n.keymap_records(body)), [(0x20, 0x01, H("05000700")), (0x2e, 0x07, b"")])
        self.assertEqual(list(n.led_entries(H("20780064") + H("219600") + b"\x96")), [(0x20, 120, 100), (0x21, 150, 150)])

    def test_split_on_records_two_frames(self):
        recs = b"".join(n.key_press(i, 0x04 + (i % 20)) for i in range(0x4a))  # 74 x 7 bytes = 518
        parts = n.split_on_records(recs, n.keymap_rec_len)
        self.assertTrue(all(len(p) <= 482 and len(p) % 7 == 0 for p in parts))
        self.assertEqual(b"".join(parts), recs)


class FakePort(unittest.TestCase):
    def test_full_led_map_write_three_frames(self):
        records = b"".join(n.led_entry(i, 0, 150) for i in range(136))       # 544 bytes
        ser = FakeSerial([reply(0x30, 0x100E, 0x01), reply(0x30, 0x100E, 0x01), reply(0x30, 0x100E, 0x00)])
        n.write_store(n.Link("fake", ser=ser), 0x100E, 0, records)
        self.assertEqual([w[3] for w in ser.written], [2, 1, 0])               # byte 3 counts down
        self.assertEqual([w[5] for w in ser.written], [0xF5, 0xF5, 0x42])      # 241, 241, 62 record bytes

    def test_three_frame_guard(self):
        with self.assertRaises(ValueError):
            n.write_store(n.Link("fake", ser=FakeSerial([])), 0x100E, 0, bytes(544), max_frames=2)

    def test_read_store_continue(self):
        ser = FakeSerial([reply(0x30, 0x1003, 0x01, b"\x00" + H("200104")),
                          reply(0x30, 0x1003, 0x00, b"\x00" + H("05000700"))])
        body = n.read_store(n.Link("fake", ser=ser), 0x1003, 0)
        self.assertEqual(body, H("20010405000700"))
        self.assertEqual(ser.written[0][8], 0x00)      # first request: flags 00
        self.assertEqual(ser.written[1][8], 0x01)      # then continue

    def test_read_store_nothing_stored(self):
        ser = FakeSerial([reply(0x30, 0x1001, 0x16, b"\x00")])
        self.assertIsNone(n.read_store(n.Link("fake", ser=ser), 0x1001, 0))

    def test_led_setting_guard_and_framing(self):
        with self.assertRaises(ValueError):
            n.led_setting(n.Link("fake", ser=FakeSerial([])), 0x1013, 0)
        ser = FakeSerial([reply(0xED, 0x1013, 0x00)])
        n.led_setting(n.Link("fake", ser=ser), 0x1013, 100)
        self.assertEqual(ser.written[0][6:11], H("1013000064"))  # sub, flags 00, target 00, value 100

    def test_right_version_through_left(self):
        ser = FakeSerial([reply(0xFE, 0x1002, 0x00, H("00032304"), sender=0x51)])
        f = n.Link("fake", ser=ser).send(n.CAT_SYSTEM, 0x1002, dest=n.RIGHT)
        self.assertEqual(ser.written[0][2], 0x51)
        self.assertEqual(n.fw_version(f), "3.35.4")


if __name__ == "__main__":
    unittest.main(verbosity=1)
