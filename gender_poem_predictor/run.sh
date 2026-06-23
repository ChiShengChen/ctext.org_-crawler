#!/usr/bin/env bash
# Reproduce the full regional-origin prediction pipeline end to end.
set -e
cd "$(dirname "$0")"

echo "### Step 1/2: build poet-level dataset from 全唐詩 volumes + CBDB geo labels"
python3 build_dataset.py --min-poems 5

echo
echo "### Step 2/2: train & evaluate classifiers"
echo
echo "===================== TASK: South vs North (binary) ====================="
python3 train.py --task southnorth --min-poems 10

echo
echo "===================== TASK: macro regions (3-way) ======================="
python3 train.py --task macro --min-poems 10

echo
echo "===================== TASK: circuit / 道 (multi-class) ==================="
python3 train.py --task circuit --min-poems 10 --max-regions 6
