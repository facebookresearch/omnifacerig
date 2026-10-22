# OmniFaceRig

https://github.com/user-attachments/assets/0ac09a3f-f804-4655-aa3d-0e327edd3ef8

![License: TBD](https://img.shields.io/badge/license-TBD-lightgrey.svg)
![Dataset: 1,345 assets](https://img.shields.io/badge/dataset-1%2C345%20assets-1877F2.svg)
[![Paper: arXiv](https://img.shields.io/badge/paper-arXiv%3A2606.08043-b31b1b.svg)](https://arxiv.org/abs/2606.08043)

**Paper:** [arXiv:2606.08043](https://arxiv.org/abs/2606.08043) | **Project page:** [omnifacerig.github.io](https://omnifacerig.github.io/)

## Overview

The OmniFaceRig dataset contains rigged, stylized 3D faces for research in facial animation, avatar creation, and geometry processing. Each asset was created using blendshapes that follow a FACS based interface. The v1 release contains 1,345 assets spanning human, humanoid, domestic animal, and wild animal faces. Its subject groups include domestic cats and dogs, human professions, science-fiction characters, fantasy races, nature and elemental humanoids, and wild felines and canines.

Each asset provides source geometry, textures, reference renders, segmentation and keypoint images, a solved template mesh, and production-friendly rig exports. The release includes 687 male and 658 female assets across four face types.

## Dataset at a glance

| Item | v1 release |
| --- | ---: |
| Assets | 1,345 |
| Files per asset | 11 |
| Dataset files | 14,798 |
| Shards | 25 |
| Compressed shard size | 25642876340 bytes (23.88 GiB) |
| Uncompressed payload | 29880067699 bytes (27.83 GiB) |
| Review videos | 2,690 |
| `rest_template` files | 3 |

### Asset distribution

| Dimension | Value | Assets |
| --- | --- | ---: |
| Group | Domestic cats | 164 |
| Group | Domestic dogs | 178 |
| Group | Fantasy races | 204 |
| Group | Human professions | 168 |
| Group | Humanoids, elemental | 145 |
| Group | Humanoids, nature | 221 |
| Group | Science fiction | 65 |
| Group | Wild canines | 71 |
| Group | Wild felines | 129 |
| Gender | Female | 658 |
| Gender | Male | 687 |
| Face type | Animal, long muzzle | 255 |
| Face type | Animal, short muzzle | 281 |
| Face type | Human | 331 |
| Face type | Humanoid | 478 |

These counts are generated from [`omni_face_dataset/omni_face_dataset_v1_metadata.csv`](omni_face_dataset/omni_face_dataset_v1_metadata.csv).

## Dataset structure

Extracting every shard into the same parent directory produces:

```text
omni_face_dataset_v1/
|-- rest_template/
|   |-- humanoid_template_v3_style2.obj
|   |-- humanoid_template_v3_style2.usd
|   `-- humanoid_template_v3_style2_arap.obj
|-- <asset>/
|   |-- <asset>.glb
|   |-- <asset>.obj
|   |-- <asset>.mtl
|   |-- <asset>.png
|   |-- <asset>_render.png
|   |-- <asset>_final_segmentation.png
|   |-- <asset>_head_crop_keypoints.png
|   |-- <asset>_solved_template.obj
|   |-- <asset>_rig.fbx
|   |-- <asset>_rig.glb
|   `-- <asset>_rig.usdz
`-- ...
```

The `rest_template` directory contains the canonical humanoid template in OBJ and USD formats plus the ARAP template mesh used during fitting.

| Per-asset file | Description |
| --- | --- |
| `<asset>.glb` | Textured source mesh in binary glTF format. |
| `<asset>.obj` | Source mesh geometry in OBJ format. |
| `<asset>.mtl` | Material definition for the source OBJ. |
| `<asset>.png` | Texture referenced by the source material. |
| `<asset>_render.png` | Reference render of the asset. |
| `<asset>_final_segmentation.png` | Final semantic segmentation image. |
| `<asset>_head_crop_keypoints.png` | Head crop with detected keypoints. |
| `<asset>_solved_template.obj` | Template mesh fitted to the asset. |
| `<asset>_rig.fbx` | Rigged asset in FBX format. |
| `<asset>_rig.glb` | Rigged asset in binary glTF format. |
| `<asset>_rig.usdz` | Rigged asset in USDZ format. |

The shard directory also includes `SHA256SUMS`, a release manifest, and a JSON Lines file with the path, size, SHA-256 digest, and shard assignment for every dataset file.

## Download and rebuild from shards

### Prerequisites

Install [Git LFS](https://git-lfs.com/), [Zstandard](https://facebook.github.io/zstd/), and a `tar` implementation. Then clone the repository and enter the shard directory:

```bash
git lfs install
git clone https://github.com/facebookresearch/omnifacerig.git
cd omnifacerig/omni_face_dataset/omni_face_dataset_v1_shards
git lfs pull
```

### Linux and macOS

Verify every release artifact before extraction:

```bash
sha256sum -c SHA256SUMS
```

Extract every shard into the same directory in filename order:

```bash
for shard in omni_face_dataset_v1-shard-*.tar.zst; do
  zstd -dc "$shard" | tar -xf -
done
```

### Windows PowerShell

Verify every release artifact before extraction:

```powershell
Get-Content .\SHA256SUMS | ForEach-Object {
  $hash, $name = $_ -split '  ', 2
  if ((Get-FileHash -Algorithm SHA256 -LiteralPath $name).Hash.ToLowerInvariant() -ne $hash) {
    throw "Checksum failed: $name"
  }
}
```

Extract every shard into the same directory in filename order:

```powershell
Get-ChildItem .\omni_face_dataset_v1-shard-*.tar.zst | Sort-Object Name | ForEach-Object {
  & zstd -dc $_.FullName | tar -xf -
  if ($LASTEXITCODE -ne 0) { throw "Extraction failed: $($_.Name)" }
}
```

The result is `omni_face_dataset_v1/` with 1,345 asset directories and one `rest_template/` directory. The template is stored in `omni_face_dataset_v1-shard-00001-of-00025.tar.zst`; all shards are required for a complete release.

## Review videos and sample data

[`omni_face_dataset/dataset_review_videos.zip`](omni_face_dataset/dataset_review_videos.zip) contains two review renders per released asset: a frontal `rig_face_0` view and a 45-degree `rig_face_45` view. The archive contains 2,690 MP4 files under `dataset_review_videos/`.

[`omni_face_dataset/omni_face_dataset_sample.zip`](omni_face_dataset/omni_face_dataset_sample.zip) is an unchanged legacy quick-look archive with 49 sample assets and a two-file `rest_template`. It is packaged under its existing `omni_face_dataset_v2/` directory and is separate from the complete v1 sharded release.

## Metadata

[`omni_face_dataset/omni_face_dataset_v1_metadata.csv`](omni_face_dataset/omni_face_dataset_v1_metadata.csv) has one row per released asset and four columns:

| Column | Description |
| --- | --- |
| `asset` | Asset directory stem and stable release identifier. |
| `group` | Content group such as `domestic_cats`, `fantasy_races`, or `humanoids_nature`. |
| `gender` | Reviewed gender label: `female` or `male`. |
| `face_type` | Broad facial morphology: `human`, `humanoid`, `animal_short_muzzle`, or `animal_long_muzzle`. |

## License

The OmniFaceRig license is not yet finalized. See [`LICENSE`](LICENSE) for the current placeholder and confirm the final terms with Meta Open Source and Legal before public release. CC BY-NC 4.0 is under consideration but does not apply unless the placeholder is replaced with approved license text.

## Citation

If you find this work useful, please cite the [OmniFaceRig paper](https://arxiv.org/abs/2606.08043):

```bibtex
@article{wang2026omnifacerig,
  title={OmniFaceRig: Fully Automatic Inner-Mouth-Aware Face Rigging Across Diverse 3D Character Topologies},
  author={Wang, Chao and Ma, Guangyao and Doublestein, John and Chen, Junming and Lin, Yiming and Su, Zhaoen and Luo, Xiaomin and Cheng, Shiyang and Shen, Jie and Roble, Doug and Wang, Dilin and Li, Yilei and Ranjan, Rakesh},
  journal={arXiv preprint arXiv:2606.08043},
  year={2026}
}
```

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) before opening an issue or pull request.
