import os
import tempfile
import unittest
from pathlib import Path
from app import (
    even,
    format_seconds,
    format_bytes,
    build_zoom_filter,
    recommend_zoom,
    parse_args,
    main,
)

class TestFlowVideoProcessor(unittest.TestCase):
    def test_even(self):
        self.assertEqual(even(10), 10)
        self.assertEqual(even(11), 10)
        self.assertEqual(even(0), 0)
        self.assertEqual(even(-3), -4)

    def test_format_seconds(self):
        self.assertEqual(format_seconds(45), "45s")
        self.assertEqual(format_seconds(125), "2m 5s")
        self.assertEqual(format_seconds(3665), "1h 1m 5s")

    def test_format_bytes(self):
        self.assertEqual(format_bytes(512), "512.0 B")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1024 * 1024 * 5), "5.0 MB")

    def test_build_zoom_filter(self):
        vf = build_zoom_filter(1080, 1920, 1.12)
        self.assertIn("flags=lanczos", vf)
        self.assertIn("crop=720:1280:", vf)

    def test_recommend_zoom(self):
        rec_exact = recommend_zoom(720, 1280, 1.12)
        self.assertIn("Already 720x1280", rec_exact)

        rec_other = recommend_zoom(1920, 1080, 1.12)
        self.assertIn("Recommended output: 720x1280", rec_other)

    def test_parse_args_defaults(self):
        args = parse_args([])
        self.assertEqual(args.zoom, 1.12)
        self.assertFalse(args.dry_run)
        self.assertFalse(args.assume_yes)
        self.assertFalse(args.skip_processed)
        self.assertFalse(args.skip_target_res)

    def test_parse_args_custom(self):
        args = parse_args(["1.25", "--dry-run", "-y", "--skip-processed", "--skip-target-res", "-i", "my_vids", "-o", "my_out"])
        self.assertEqual(args.zoom, 1.25)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.assume_yes)
        self.assertTrue(args.skip_processed)
        self.assertTrue(args.skip_target_res)
        self.assertEqual(str(args.input_dir), "my_vids")
        self.assertEqual(str(args.output_dir), "my_out")

    def test_dry_run_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ret = main(["--dry-run", "-i", tmpdir])
            self.assertEqual(ret, 0)

if __name__ == "__main__":
    unittest.main()
