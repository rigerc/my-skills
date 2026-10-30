"""PNG decoding and frame-directory regression tests."""
import importlib.util
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from inspect_render import inspect


def png(path, truncated=False):
    def chunk(name, data):
        return (struct.pack('>I', len(data)) + name + data +
                struct.pack('>I', zlib.crc32(name + data) & 0xffffffff))
    raw = b'\x00' + b'\x20\x40\x60' * 4
    stream = zlib.compress(raw)
    if truncated:
        stream = stream[:-5]  # Correct PNG chunk CRC, incomplete zlib stream.
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n' +
        chunk(b'IHDR', struct.pack('>IIBBBBB', 4, 1, 8, 2, 0, 0, 0)) +
        chunk(b'IDAT', stream) + chunk(b'IEND', b'')
    )


@unittest.skipUnless(importlib.util.find_spec('PIL'), 'Pillow required for pixel decode')
class ImageInspectionTests(unittest.TestCase):
    def test_decodes_pixels_instead_of_only_headers(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td)
            valid = directory / 'valid.png'
            invalid = directory / 'broken.png'
            png(valid)
            png(invalid, truncated=True)
            self.assertTrue(inspect(valid)['ok'])
            result = inspect(invalid)
            self.assertFalse(result['ok'])
            self.assertTrue(any('Image inspection error' in x for x in result['issues']))

    def test_frame_directory_requires_every_valid_png(self):
        with tempfile.TemporaryDirectory() as td:
            directory = Path(td) / 'frames'
            directory.mkdir()
            png(directory / 'one.png')
            (directory / 'two.png').write_bytes(b'not a PNG')
            result = inspect(directory)
            self.assertFalse(result['ok'])
            self.assertIn('two.png', ' '.join(result['issues']))
            self.assertEqual(result['metadata']['png_frames'], 2)


if __name__ == '__main__':
    unittest.main()
