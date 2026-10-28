# Changelog

All notable changes to the OmniFaceRig dataset and this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dataset versions match `release_version` in the release manifest.

## Unreleased

### Added

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
