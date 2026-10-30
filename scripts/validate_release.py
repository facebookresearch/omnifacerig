#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""Validate that the OmniFaceRig release metadata files agree with each other.

Checks the metadata CSV, the per-file JSON Lines index, the release manifest,
and SHA256SUMS. Git LFS artifacts are verified through their pointer files, so
a checkout without `git lfs pull` is enough. If the archive content is present
instead, it is hashed.

Usage: python scripts/validate_release.py
"""

import collections
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = REPO_ROOT / "omni_face_dataset"
SHARD_DIR = DATASET_DIR / "omni_face_dataset_v1_shards"
METADATA_CSV = DATASET_DIR / "omni_face_dataset_v1_metadata.csv"
MANIFEST = SHARD_DIR / "omni_face_dataset_v1_manifest.json"
SHA256SUMS = SHARD_DIR / "SHA256SUMS"

METADATA_COLUMNS = ["asset", "group", "gender", "face_type"]
GENDERS = {"female", "male"}
FACE_TYPES = {"human", "humanoid", "animal_short_muzzle", "animal_long_muzzle"}
ASSET_FILE_SUFFIXES = [
    ".glb",
    ".obj",
    ".mtl",
    ".png",
    "_render.png",
    "_final_segmentation.png",
    "_head_crop_keypoints.png",
    "_solved_template.obj",
    "_rig.fbx",
    "_rig.glb",
    "_rig.usdz",
]
REST_TEMPLATE_DIR = "rest_template"
REST_TEMPLATE_FILES = {
    "humanoid_template_v3_style2.obj",
    "humanoid_template_v3_style2.usd",
    "humanoid_template_v3_style2_arap.obj",
}
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1\n"
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_digest(path):
    """Return (sha256, size) of a file, reading Git LFS pointers when present."""
    size = path.stat().st_size
    if size < 1024:
        data = path.read_bytes()
        if data.startswith(LFS_POINTER_PREFIX):
            fields = dict(
                line.split(" ", 1) for line in data.decode().splitlines()[1:]
            )
            return fields["oid"].removeprefix("sha256:"), int(fields["size"])
    return sha256_of(path), size


def check_metadata(errors):
    """Validate the metadata CSV and return its asset names."""
    with open(METADATA_CSV, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != METADATA_COLUMNS:
            errors.append(
                f"{METADATA_CSV.name}: expected columns {METADATA_COLUMNS}, "
                f"found {reader.fieldnames}"
            )
            return set()
        rows = list(reader)

    assets = set()
    for line, row in enumerate(rows, start=2):
        asset = row["asset"]
        where = f"{METADATA_CSV.name}:{line}"
        if asset in assets:
            errors.append(f"{where}: duplicate asset {asset}")
        assets.add(asset)
        if row["gender"] not in GENDERS:
            errors.append(f"{where}: unknown gender {row['gender']!r}")
        if row["face_type"] not in FACE_TYPES:
            errors.append(f"{where}: unknown face_type {row['face_type']!r}")
        name_re = rf"\d{{3}}_{re.escape(row['group'])}_{re.escape(row['gender'])}"
        if not re.fullmatch(name_re, asset):
            errors.append(
                f"{where}: asset {asset} does not match "
                f"<NNN>_{row['group']}_{row['gender']}"
            )
    return assets


def check_file_index(errors, manifest, assets):
    """Validate the JSON Lines file index against the manifest and the CSV."""
    index_path = SHARD_DIR / manifest["file_manifest"]["filename"]
    if sha256_of(index_path) != manifest["file_manifest"]["sha256"]:
        errors.append(f"{index_path.name}: SHA-256 does not match the manifest")

    root = manifest["dataset_root"]
    shards = {shard["filename"]: shard for shard in manifest["shards"]}
    files_by_dir = collections.defaultdict(set)
    shard_files = collections.Counter()
    shard_bytes = collections.Counter()
    shard_assets = collections.defaultdict(set)
    seen = set()
    with open(index_path) as f:
        for line_no, line in enumerate(f, start=1):
            where = f"{index_path.name}:{line_no}"
            entry = json.loads(line)
            path = entry["path"]
            parts = path.split("/")
            if len(parts) != 3 or parts[0] != root:
                errors.append(f"{where}: unexpected path {path}")
                continue
            if path in seen:
                errors.append(f"{where}: duplicate path {path}")
            seen.add(path)
            if not SHA256_RE.fullmatch(entry["sha256"]):
                errors.append(f"{where}: malformed sha256 for {path}")
            if entry["shard"] not in shards:
                errors.append(f"{where}: unknown shard {entry['shard']}")
                continue
            files_by_dir[parts[1]].add(parts[2])
            shard_files[entry["shard"]] += 1
            shard_bytes[entry["shard"]] += entry["size"]
            shard_assets[entry["shard"]].add(parts[1])

    rest_files = files_by_dir.pop(REST_TEMPLATE_DIR, set())
    if rest_files != REST_TEMPLATE_FILES:
        errors.append(
            f"{REST_TEMPLATE_DIR}: expected {sorted(REST_TEMPLATE_FILES)}, "
            f"found {sorted(rest_files)}"
        )
    if len(rest_files) != manifest["rest_template_file_count"]:
        errors.append("manifest: rest_template_file_count does not match the index")

    for asset in sorted(files_by_dir.keys() - assets):
        errors.append(f"{index_path.name}: {asset} is not in {METADATA_CSV.name}")
    for asset in sorted(assets - files_by_dir.keys()):
        errors.append(f"{index_path.name}: {asset} has no files")
    for asset, names in sorted(files_by_dir.items()):
        expected = {asset + suffix for suffix in ASSET_FILE_SUFFIXES}
        if names != expected:
            errors.append(
                f"{index_path.name}: {asset} missing {sorted(expected - names)}, "
                f"unexpected {sorted(names - expected)}"
            )

    for name, shard in shards.items():
        dirs = shard_assets[name]
        has_template = REST_TEMPLATE_DIR in dirs
        asset_dirs = dirs - {REST_TEMPLATE_DIR}
        if has_template != shard["includes_rest_template"]:
            errors.append(f"{name}: includes_rest_template does not match the index")
        if has_template != (name == manifest["rest_template_shard"]):
            errors.append(f"{name}: rest_template is not in rest_template_shard")
        if shard_files[name] != shard["verified_files"]:
            errors.append(f"{name}: verified_files does not match the index")
        if not (
            shard_bytes[name]
            == shard["uncompressed_payload_bytes"]
            == shard["verified_bytes"]
        ):
            errors.append(f"{name}: payload bytes do not match the index")
        if len(asset_dirs) != shard["asset_count"]:
            errors.append(f"{name}: asset_count does not match the index")
        if asset_dirs and (
            min(asset_dirs) != shard["first_asset"]
            or max(asset_dirs) != shard["last_asset"]
        ):
            errors.append(f"{name}: first_asset/last_asset do not match the index")

    if sum(shard_bytes.values()) != manifest["total_source_bytes"]:
        errors.append("manifest: total_source_bytes does not match the index")


def check_manifest(errors, manifest, assets):
    root = manifest["dataset_root"]
    count = manifest["shard_count"]
    expected_names = [
        f"{root}-shard-{i:05d}-of-{count:05d}.tar.zst" for i in range(1, count + 1)
    ]
    if [shard["filename"] for shard in manifest["shards"]] != expected_names:
        errors.append(f"manifest: shards are not {expected_names[0]} .. of-{count:05d}")
    if manifest["asset_count"] != len(assets):
        errors.append(
            f"manifest: asset_count {manifest['asset_count']} != "
            f"{len(assets)} rows in {METADATA_CSV.name}"
        )
    if sum(shard["asset_count"] for shard in manifest["shards"]) != len(assets):
        errors.append("manifest: shard asset counts do not sum to asset_count")
    total_archive = sum(shard["archive_bytes"] for shard in manifest["shards"])
    if total_archive != manifest["total_archive_bytes"]:
        errors.append("manifest: total_archive_bytes does not match the shards")
    if manifest["files_per_asset"] != len(ASSET_FILE_SUFFIXES):
        errors.append(f"manifest: files_per_asset != {len(ASSET_FILE_SUFFIXES)}")


def check_sha256sums(errors, manifest):
    sums = {}
    for line_no, line in enumerate(SHA256SUMS.read_text().splitlines(), start=1):
        digest, sep, name = line.partition("  ")
        if not sep or not SHA256_RE.fullmatch(digest) or "/" in name:
            errors.append(f"{SHA256SUMS.name}:{line_no}: malformed line {line!r}")
            continue
        if name in sums:
            errors.append(f"{SHA256SUMS.name}:{line_no}: duplicate entry {name}")
        sums[name] = digest

    on_disk = {p.name for p in SHARD_DIR.iterdir() if p.is_file()} - {SHA256SUMS.name}
    for name in sorted(on_disk - sums.keys()):
        errors.append(f"{SHA256SUMS.name}: {name} is not listed")

    shards = {shard["filename"]: shard for shard in manifest["shards"]}
    for name, digest in sorted(sums.items()):
        path = SHARD_DIR / name
        if not path.is_file():
            errors.append(f"{SHA256SUMS.name}: {name} does not exist")
            continue
        actual, size = content_digest(path)
        if actual != digest:
            errors.append(f"{SHA256SUMS.name}: checksum mismatch for {name}")
        if name in shards:
            if shards[name]["sha256"] != digest:
                errors.append(f"{name}: manifest sha256 differs from SHA256SUMS")
            if shards[name]["archive_bytes"] != size:
                errors.append(f"{name}: size {size} != manifest archive_bytes")
    for name in sorted(shards.keys() - sums.keys()):
        errors.append(f"{SHA256SUMS.name}: shard {name} is not listed")


def check_release_attachments(errors, manifest, assets):
    """Validate the correction map and review ZIP, including LFS-only checkouts."""
    specs = {
        "asset_renames": "omni_face_dataset/omni_face_dataset_v1_asset_renames.csv",
        "review_videos": "omni_face_dataset/dataset_review_videos.zip",
    }
    for key, expected_path in specs.items():
        record = manifest.get(key)
        if record is None:
            if manifest["release_version"] != "v1":
                errors.append(f"manifest: missing {key}")
            continue
        if record.get("path") != expected_path:
            errors.append(f"manifest: unexpected {key} path")
            continue
        path = REPO_ROOT / expected_path
        if not path.is_file():
            errors.append(f"{key}: file is missing")
            continue
        actual, size = content_digest(path)
        if actual != record.get("sha256"):
            errors.append(f"{key}: SHA-256 does not match the manifest")
        if key == "review_videos":
            if size != record.get("archive_bytes"):
                errors.append("review_videos: size does not match the manifest")
            if record.get("video_count") != 2 * len(assets):
                errors.append("review_videos: expected two videos per asset")
            continue
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["old_asset", "new_asset", "old_group", "new_group", "face_type"]:
                errors.append("asset_renames: unexpected CSV columns")
                continue
            rows = list(reader)
        with METADATA_CSV.open(newline="") as f:
            metadata = {r["asset"]: r for r in csv.DictReader(f)}
        if len(rows) != record.get("count"):
            errors.append("asset_renames: row count does not match the manifest")
        old_names, new_names = set(), set()
        for row in rows:
            old, new = row["old_asset"], row["new_asset"]
            if old in old_names or new in new_names:
                errors.append("asset_renames: duplicate old or new asset")
            old_names.add(old)
            new_names.add(new)
            if old in assets or new not in assets:
                errors.append(f"asset_renames: old/new identity mismatch for {old}")
            if new in metadata:
                current = metadata[new]
                if current["group"] != row["new_group"] or current["face_type"] != row["face_type"]:
                    errors.append(f"asset_renames: metadata mismatch for {new}")
                expected = rf"\d{{3}}_{re.escape(row['old_group'])}_{re.escape(current['gender'])}"
                if not re.fullmatch(expected, old):
                    errors.append(f"asset_renames: invalid original name {old}")


def main():
    errors = []
    manifest = json.loads(MANIFEST.read_text())
    assets = check_metadata(errors)
    check_manifest(errors, manifest, assets)
    check_file_index(errors, manifest, assets)
    check_sha256sums(errors, manifest)
    check_release_attachments(errors, manifest, assets)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"\n{len(errors)} error(s) found.")
        return 1
    print(
        f"OK: {len(assets)} assets, {manifest['shard_count']} shards, "
        f"release {manifest['release_version']} metadata is consistent."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
