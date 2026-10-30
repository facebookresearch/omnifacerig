# Changelog

All notable changes to the OmniFaceRig dataset and this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dataset versions match `release_version` in the release manifest.

## v1.0.1 - Unreleased

### Fixed

- Corrected six human/humanoid asset names previously assigned to `domestic_cats`.
  The reviewed destination categories are `fantasy_races` (three), `sci_fi` (two),
  and `human_professions` (one), with IDs appended to each category's number range.
- Renamed asset directories, their 66 files, and 12 review videos; updated OBJ/MTL
  references, metadata, file index, release manifest, checksums, and README counts.
  Only shards 1, 4, 5, and 6 changed. Geometry, rig/texture/video payloads and the
  separate legacy sample ZIP are unchanged.

### Added

- `omni_face_dataset_v1_asset_renames.csv` records the old-to-new asset mapping.
  The release validator also checks this map and the review ZIP against the manifest.
- GitHub Actions workflow that runs `scripts/validate_release.py` on every push and pull request. It checks that the metadata CSV, the file index, the release manifest, and `SHA256SUMS` agree.
- Issue templates for dataset problems and download or extraction problems, and a pull request template.
- This changelog.

## v1 - 2026-10-26

### Added

- Sharded v1 release: 1,345 assets in 25 `tar.zst` shards under `omni_face_dataset/omni_face_dataset_v1_shards/`, with `SHA256SUMS`, a release manifest, and a JSON Lines index of every dataset file.
- `rest_template/` with the canonical humanoid template in OBJ and USD formats and the ARAP template mesh, stored in shard 1.
- `omni_face_dataset_v1_metadata.csv` with `group`, `gender`, and `face_type` labels for every asset.
- `dataset_review_videos.zip` with frontal and 45-degree review renders for every asset (2,690 MP4 files).
- FAIR Noncommercial Research License v1.

### Changed

- The earlier monolithic `omni_face_dataset_v1.zip` is now `omni_face_dataset_sample.zip`, a legacy quick-look archive with 49 assets. It is not part of the v1 sharded release.
