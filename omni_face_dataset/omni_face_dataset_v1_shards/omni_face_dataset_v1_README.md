# Omni Face Dataset v1

This sharded release contains 1,376 reviewed assets and the required `rest_template` directory. Extract every shard into the same parent directory; all shards share the `omni_face_dataset_v1` root.

## Contents

- Shards: 25 `tar.zst` archives
- Asset directories: 1,376
- Files per asset: 11
- `rest_template`: included in `omni_face_dataset_v1-shard-00001-of-00025.tar.zst`
- Uncompressed payload: 30,589,813,958 bytes

The existing monolithic ZIP is a separate legacy artifact and is not part of this sharded release.

## Verify

Run SHA-256 verification against `SHA256SUMS` before extraction. On Linux or macOS:

```bash
sha256sum -c SHA256SUMS
```

On Windows PowerShell:

```powershell
Get-Content .\SHA256SUMS | ForEach-Object {
  $hash, $name = $_ -split '  ', 2
  if ((Get-FileHash -Algorithm SHA256 -LiteralPath $name).Hash.ToLowerInvariant() -ne $hash) { throw "Checksum failed: $name" }
}
```

## Extract

Extract all shards into the same directory in filename order. On Linux or macOS:

```bash
for shard in omni_face_dataset_v1-shard-*.tar.zst; do
  zstd -dc "$shard" | tar -xf -
done
```

On Windows PowerShell:

```powershell
Get-ChildItem .\omni_face_dataset_v1-shard-*.tar.zst | Sort-Object Name | ForEach-Object {
  & zstd -dc $_.FullName | tar -xf -
  if ($LASTEXITCODE -ne 0) { throw "Extraction failed: $($_.Name)" }
}
```

After extraction, the dataset is under `omni_face_dataset_v1`.
