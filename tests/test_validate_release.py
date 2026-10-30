"""Regression checks for release correction maps and LFS-only validation."""
import csv
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "validate_release", Path(__file__).resolve().parents[1] / "scripts/validate_release.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class CorrectionValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        data = self.root / "omni_face_dataset"
        data.mkdir()
        self.metadata = data / "omni_face_dataset_v1_metadata.csv"
        self.metadata.write_text("asset,group,gender,face_type\n209_human_professions_male,human_professions,male,human\n")
        self.map_path = data / "omni_face_dataset_v1_asset_renames.csv"
        self.video_path = data / "dataset_review_videos.zip"
        self.video_path.write_text("version https://git-lfs.github.com/spec/v1\n"
                                   + "oid sha256:" + "a" * 64 + "\nsize 12345\n")
        self.manifest = {"release_version": "v1.0.1", "asset_renames": {
            "path": str(self.map_path.relative_to(self.root)), "count": 1},
            "review_videos": {"path": str(self.video_path.relative_to(self.root)),
                              "sha256": "a" * 64, "archive_bytes": 12345, "video_count": 2}}
        self.rows = [{"old_asset": "202_domestic_cats_male", "new_asset": "209_human_professions_male",
                      "old_group": "domestic_cats", "new_group": "human_professions", "face_type": "human"}]
        self.assets = {"209_human_professions_male"}

    def save_map(self):
        with self.map_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)
        self.manifest["asset_renames"]["sha256"] = hashlib.sha256(self.map_path.read_bytes()).hexdigest()

    def check(self):
        errors = []
        with patch.object(validator, "REPO_ROOT", self.root), patch.object(validator, "METADATA_CSV", self.metadata):
            validator.check_release_attachments(errors, self.manifest, self.assets)
        return errors

    def test_valid_correction_with_lfs_pointer(self):
        self.save_map()
        self.assertEqual(self.check(), [])

    def test_rejects_stale_identity_and_duplicate_mapping(self):
        self.rows *= 2
        self.manifest["asset_renames"]["count"] = 2
        self.assets.add("202_domestic_cats_male")
        self.save_map()
        errors = self.check()
        self.assertTrue(any("duplicate" in e for e in errors))
        self.assertTrue(any("identity mismatch" in e for e in errors))

    def test_rejects_category_mismatch(self):
        self.rows[0]["new_group"] = "sci_fi"
        self.save_map()
        self.assertTrue(any("metadata mismatch" in e for e in self.check()))

    def test_rejects_tampered_map_and_wrong_lfs_object(self):
        self.save_map()
        self.map_path.write_text(self.map_path.read_text() + "\n")
        self.manifest["review_videos"]["sha256"] = "b" * 64
        errors = self.check()
        self.assertEqual(sum("SHA-256" in e for e in errors), 2)


if __name__ == "__main__":
    unittest.main()
