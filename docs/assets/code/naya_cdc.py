# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Create-knowledge-base contributors
"""Minimal Naya Create CDC client (the binary "ProtocolCDC" channel).

Frame layout, both directions:
    AA <b1> <b2> <b3> <category> <size> <sub_hi> <sub_lo> <flags> <payload...> <xor> 04
  request:  b1 = 00, b2 = destination (0x50 left, 0x51 right; the version read also reaches
            the right half through the left port), b3 = frames still to come in a chunked
            write (00 otherwise)
  reply:    b1 = the answering half's address, b2 = 00, b3 = frames still to come in a
            multi-part read; flags = status (00 last, 01 more, 11 unimplemented,
            16/18 nothing stored, EA value refused)
  size = 3 + len(payload)   (sub_hi, sub_lo, flags, payload)
  xor  = XOR of sub_hi .. last payload byte (the size byte is NOT included)

The site's params / reply strings start at the flags / status byte: params "00 01"
is flags=0x00, payload=bytes([0x01]) here.

Tested offline against vendor and captured frames (test_naya_cdc.py); not a flasher.
Read the safety notes on the knowledge base's "Python recipes" page (tools/recipes-python)
before writing anything to a keyboard.
"""
import struct
import time
from typing import Callable, Iterator, List, NamedTuple, Optional

SOF, EOT = 0xAA, 0x04
LEFT, RIGHT = 0x50, 0x51
MAX_PAYLOAD = 242          # payload bytes per frame after the flags byte
SLICE = 241                # record bytes per frame in a chunked write (index byte first)

ST_LAST, ST_MORE = 0x00, 0x01
ST_UNIMPLEMENTED = 0x11
ST_NOTHING_STORED, ST_NOTHING_STORED_CONT = 0x16, 0x18
ST_VALUE_REFUSED = 0xEA

CAT_REMAP, CAT_MODULE, CAT_LED, CAT_FLASH, CAT_SYSTEM = 0x30, 0xDE, 0xED, 0xFA, 0xFE


def xor8(data: bytes) -> int:
    x = 0
    for b in data:
        x ^= b
    return x


def build_frame(dest: int, category: int, subcmd: int, payload: bytes = b"",
                flags: int = 0x00, remaining: int = 0x00) -> bytes:
    payload = bytes(payload)
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("payload over 242 bytes: split it (see write_store)")
    data = bytes([(subcmd >> 8) & 0xFF, subcmd & 0xFF, flags]) + payload
    header = bytes([SOF, 0x00, dest, remaining, category, len(data)])
    return header + data + bytes([xor8(data), EOT])


class Frame(NamedTuple):
    sender: int
    dest: int
    remaining: int
    category: int
    subcmd: int
    status: int
    payload: bytes


def parse_frame(frame: bytes) -> Frame:
    if len(frame) < 11 or frame[0] != SOF or frame[-1] != EOT:
        raise ValueError("not a frame")
    size = frame[5]
    if size < 3 or len(frame) != size + 8:
        raise ValueError("length does not match the size byte")
    data = frame[6:6 + size]
    if xor8(data) != frame[6 + size]:
        raise ValueError("checksum mismatch")
    return Frame(frame[1], frame[2], frame[3], frame[4],
                 (data[0] << 8) | data[1], data[2], bytes(data[3:]))


def split_stream(buf: bytearray) -> List[bytes]:
    """Remove and return every complete frame at the front of buf; resync on 0xAA."""
    out = []
    while True:
        start = buf.find(bytes([SOF]))
        if start < 0:
            buf.clear()
            return out
        del buf[:start]
        if len(buf) < 6:
            return out
        total = buf[5] + 8
        if len(buf) < total:
            return out
        candidate = bytes(buf[:total])
        if candidate[-1] == EOT and xor8(candidate[6:-2]) == candidate[-2]:
            out.append(candidate)
            del buf[:total]
        else:
            del buf[:1]          # a stray 0xAA; look for the next start


class Link:
    """One open CDC port. Hold it for the whole job; do not reopen per request."""

    def __init__(self, port: str, dest: int = LEFT, ser=None):
        self.dest = dest
        if ser is None:
            import serial  # pyserial
            # dsrdtr=False and a write timeout: with DSR flow control Windows blocks the
            # first write forever, because the keyboard never asserts DSR.
            ser = serial.Serial(port, 115200, timeout=0.05,
                                write_timeout=2.0, dsrdtr=False)
            ser.dtr = True
            ser.rts = True
        self.ser = ser
        self.buf = bytearray()

    def close(self) -> None:
        self.ser.close()

    def write(self, frame: bytes) -> None:
        self.ser.write(frame)

    def send(self, category: int, subcmd: int, payload: bytes = b"", flags: int = 0,
             remaining: int = 0, timeout: float = 1.0, dest: Optional[int] = None) -> Frame:
        """Send one frame and wait for the reply with the same category and subcommand.
        dest=RIGHT on the left half's port reaches the right half for the version read;
        Bluetooth reads sent that way answer for the left half. Read the rest on the
        right half's own port."""
        to = self.dest if dest is None else dest
        self.write(build_frame(to, category, subcmd, payload, flags, remaining))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if not chunk:
                continue
            self.buf += chunk
            for raw in split_stream(self.buf):
                f = parse_frame(raw)
                if f.category == category and f.subcmd == subcmd:
                    return f
                # anything else (a late reply, a keyscan event) is dropped here
        raise TimeoutError(f"no reply to {category:02x}/{subcmd:04x}")

    def open_session(self) -> Frame:
        """The opener NayaCore and nayactl use: fe/1001 (media id) then fe/1002 (version)."""
        for wait in (0.3, 0.7, 1.0):
            self.write(build_frame(self.dest, CAT_SYSTEM, 0x1001))
            time.sleep(wait)
            try:
                return self.send(CAT_SYSTEM, 0x1002, timeout=0.5)
            except TimeoutError:
                continue
        raise TimeoutError("no answer to fe/1001 + fe/1002")


def fw_version(reply: Frame) -> str:
    """fe/1002 reply 00 00 03 29 00: status 00, payload 00 major minor patch -> '3.41.0'."""
    major, minor, patch = reply.payload[-3:]
    return f"{major}.{minor}.{patch}"


def kb_battery_mv(link: Link) -> int:
    """fe/1006: the half's own cell in millivolts, big-endian."""
    return int.from_bytes(link.send(CAT_SYSTEM, 0x1006).payload[:2], "big")


MODULE_TYPES = {0x10: "Touch", 0x20: "Track", 0x40: "Tune", 0x80: "Float (unconfirmed)"}


def module_on_dock(link: Link) -> Optional[dict]:
    """de/1001 reply 00 01 <address> (bit 0 = side, high nibble = type, 0xF0/0xF1 = not
    booted); 00 00 f0 when nothing booted answers (returns None)."""
    p = link.send(CAT_MODULE, 0x1001, timeout=1.5).payload
    if len(p) < 2 or p[0] != 0x01:
        return None
    addr = p[1]
    kind = "not booted" if addr & 0xF0 == 0xF0 else MODULE_TYPES.get(addr & 0xF0, "unknown")
    return {"address": addr, "type": kind, "side": "right" if addr & 1 else "left"}


def read_store(link: Link, subcmd: int, index: int) -> Optional[bytes]:
    """Chunked REMAP read: 30/1003 layer data, 30/100d LED map, 30/100b module config.

    First request flags 00, then flags 01 ("continue") while the reply status is 01.
    Every reply chunk starts with the index byte again; records cross chunk borders.
    The cursor belongs to the open port, so keep one Link for the whole read.
    """
    body = bytearray()
    flags = 0x00
    while True:
        f = link.send(CAT_REMAP, subcmd, bytes([index]), flags=flags)
        if f.status in (ST_NOTHING_STORED, ST_NOTHING_STORED_CONT):
            return None
        if f.status not in (ST_LAST, ST_MORE):
            raise RuntimeError(f"status {f.status:02x} on {subcmd:04x}")
        body += f.payload[1:]
        if f.status == ST_LAST:
            return bytes(body)
        flags = 0x01


def keymap_records(body: bytes) -> Iterator[tuple]:
    """Layer data records: [position][type][len][param...]."""
    i = 0
    while i + 3 <= len(body):
        pos, kind, n = body[i], body[i + 1], body[i + 2]
        yield pos, kind, bytes(body[i + 3:i + 3 + n])
        i += 3 + n


def led_entries(body: bytes) -> Iterator[tuple]:
    """LED map entries: [position][hue u16 LE][saturation]; sat 150 = no color set."""
    for i in range(0, len(body) - 3, 4):
        yield body[i], body[i + 1] | (body[i + 2] << 8), body[i + 3]


def write_store(link: Link, subcmd: int, index: int, records: bytes,
                max_frames: Optional[int] = None) -> None:
    """Chunked REMAP write: 30/1004 layer data, 30/100e LED map, 30/100c module config.

    Every frame carries [index] + up to 241 record bytes (records may straddle frames);
    byte 3 counts the frames still to come (02 01 00 for three frames).
    Firmware 3.28.7 wedges on any three-frame write: pass max_frames=2 and split first.
    """
    slices = [records[i:i + SLICE] for i in range(0, len(records), SLICE)] or [b""]
    if max_frames is not None and len(slices) > max_frames:
        raise ValueError("too many frames: split on record boundaries first")
    for k, part in enumerate(slices):
        remaining = len(slices) - 1 - k
        f = link.send(CAT_REMAP, subcmd, bytes([index]) + part, remaining=remaining)
        if f.status == ST_VALUE_REFUSED:
            raise ValueError("the firmware refused a value; nothing was stored")
        expected = ST_MORE if remaining else ST_LAST
        if f.status != expected:
            raise RuntimeError(f"frame {k}: status {f.status:02x}, expected {expected:02x}")


def split_on_records(records: bytes, rec_len: Callable[[bytes, int], int],
                     limit: int = 2 * SLICE) -> List[bytes]:
    """Group whole records into writes of at most `limit` bytes (two frames by default)."""
    out, cur, i = [], bytearray(), 0
    while i < len(records):
        n = rec_len(records, i)
        if cur and len(cur) + n > limit:
            out.append(bytes(cur))
            cur = bytearray()
        cur += records[i:i + n]
        i += n
    if cur:
        out.append(bytes(cur))
    return out


def keymap_rec_len(b: bytes, i: int) -> int:
    return 3 + b[i + 2]


def led_rec_len(b: bytes, i: int) -> int:
    return 4


def key_press(position: int, usage: int, page: int = 0x07, mods: int = 0x00) -> bytes:
    """A KEY_PRESS record: param = [usage lo][usage hi][page][modifier bits]."""
    return bytes([position, 0x01, 0x04, usage & 0xFF, (usage >> 8) & 0xFF, page, mods])


def led_entry(position: int, hue: int, sat: int) -> bytes:
    if not (0 <= hue <= 360 and (0 <= sat <= 100 or sat == 150)):
        raise ValueError("hue 0-360, saturation 0-100 (150 = no color)")
    return bytes([position, hue & 0xFF, hue >> 8, sat])


def led_setting(link: Link, subcmd: int, value: int, target: int = 0x00) -> Frame:
    """ED commands take [target, value] after the flags byte (params 00 <target> <value>).
    A one-byte payload is zero-filled by the firmware (value 0), and every ED frame is
    acked, applied or not. ed/1012 scan mode (0/1), ed/1013 max brightness (1-100,
    persistent), ed/1014 LED action override (0 until restart, 1 until layer change),
    ed/1008 brightness now (0-100), ed/1011 effect now."""
    if subcmd == 0x1013 and not 1 <= value <= 100:
        raise ValueError("ed/1013 value 0 keeps the key LEDs dark across reboots")
    return link.send(CAT_LED, subcmd, bytes([target, value]))


def get_timeouts(link: Link) -> tuple:
    """fe/100b: three u32 LE milliseconds (idle, sleep, third field)."""
    return struct.unpack("<3I", link.send(CAT_SYSTEM, 0x100B).payload[:12])


def set_timeouts(link: Link, idle_ms: int, sleep_ms: int, third_ms: int = 30000) -> tuple:
    """fe/100a, then read back with fe/100b as NayaCore does. On 3.41.0 values under
    30 s are refused (status EA); 0 turns idle or sleep off."""
    for v in (idle_ms, sleep_ms):
        if v and v < 30000:
            raise ValueError("under 30 s is refused")
    if third_ms < 30000:
        raise ValueError("third field: keep 30 s or more (0 untested)")
    f = link.send(CAT_SYSTEM, 0x100A, struct.pack("<3I", idle_ms, sleep_ms, third_ms))
    if f.status == ST_VALUE_REFUSED:
        raise ValueError("the firmware refused the timeouts")
    return get_timeouts(link)


PARTITION_STATE = {0: "not detected", 1: "detected", 2: "formatted", 3: "mounted", 4: "erased"}


def spiflash_test(link: Link) -> dict:
    """fa/1001, read-only: 2 header bytes, then 6 bytes per partition
    (state + five return codes, signed). Left 5 partitions, right 3 on 3.41.0."""
    p = link.send(CAT_FLASH, 0x1001, timeout=3.0).payload
    parts = []
    for i in range(2, len(p) - 5, 6):
        codes = [c - 256 if c > 127 else c for c in p[i + 1:i + 6]]
        parts.append((PARTITION_STATE.get(p[i], p[i]), codes))
    return {"header": p[:2].hex(" "), "partitions": parts}
