#!/bin/bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
output_path=${1:-"$repo_root/dist/kvstore-m2.tar.gz"}
case "$output_path" in
  /*) ;;
  *) output_path="$PWD/$output_path" ;;
esac
python_bin=${PYTHON_BIN:-python3}
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT

mkdir -p "$build_dir/wheels" "$build_dir/infra/application" "$build_dir/kvstore" "$(dirname "$output_path")"
"$python_bin" -m pip download \
  --only-binary=:all: \
  --implementation cp \
  --python-version 3.11 \
  --abi cp311 \
  --platform manylinux_2_17_x86_64 \
  --dest "$build_dir/wheels" \
  -r "$repo_root/requirements.txt"

cp "$repo_root"/kvstore/*.py "$build_dir/kvstore"
cp "$repo_root/requirements.txt" "$build_dir/requirements.txt"
cp "$repo_root/infra/application/bootstrap.sh" "$build_dir/infra/application/bootstrap.sh"
cp "$repo_root/infra/application/refresh.sh" "$build_dir/infra/application/refresh.sh"
cp "$repo_root/infra/application/kvstore-refresh.service" "$build_dir/infra/application/kvstore-refresh.service"
tar -czf "$output_path" -C "$build_dir" kvstore requirements.txt infra wheels
echo "$output_path"
