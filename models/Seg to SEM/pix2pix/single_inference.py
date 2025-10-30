#!/usr/bin/env python3
"""
Single-image inference with fixed config inside the script.
Usage:
    python single_infer.py --input ./examples/sample_input.png --output ./outputs/sample_input_fake.png
"""

import argparse
import sys, shlex, subprocess
from pathlib import Path
from PIL import Image

# ===== Fixed config (edit here if needed) =====
REPO        = Path(__file__).parent / "pix2pix"              # path to cloned CycleGAN&Pix2Pix repo
CKPT_ROOT   = Path(__file__).parent / "checkpoints"          # checkpoints root
EXPERIMENT  = "wafer_pix2pix_AtoB_256_out1"                  # your experiment folder name under checkpoints
NETG        = "unet_256"
NORM        = "batch"
DIRECTION   = "AtoB"
DATASET_MODE= "single"
PREPROCESS  = "resize_and_crop"
LOAD_SIZE   = 286
CROP_SIZE   = 256
INPUT_NC    = 3                                               # your “input 3”
OUTPUT_NC   = 1                                               # your “output 1”
EPOCH       = "latest"
NUM_TEST    = 1
EVAL        = True
# ==============================================

def main():
    p = argparse.ArgumentParser(description="Single-image inference (A only) with fixed config")
    p.add_argument("--input", required=True, help="Path to input image (A)")
    p.add_argument("--output", required=True, help="Path to save generated image")
    args = p.parse_args()

    repo = REPO.resolve()
    ckpt_root = CKPT_ROOT.resolve()
    exp = EXPERIMENT
    inp = Path(args.input).resolve()
    out_path = Path(args.output).resolve()

    # temp/results dirs local to the script
    work_dir = Path(__file__).parent.resolve()
    temp_dir = work_dir / "single_infer_tmp"
    results_dir = work_dir / "inference_single"

    temp_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # stage input as PNG (RGB) like in Kaggle flow
    staged = temp_dir / "test.png"
    Image.open(inp).convert("RGB").save(staged)
    print("Saved staged input:", staged)

    test_py = repo / "test.py"
    if not test_py.exists():
        print(f"[ERROR] Could not find test.py under repo path: {repo}")
        print("Clone the repo locally, e.g.:")
        print("  git clone --depth 1 https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix.git pix2pix")
        sys.exit(1)

    cmd = [
        sys.executable, str(test_py),
        "--model", "test",
        "--netG", NETG,
        "--norm", NORM,
        "--dataroot", str(temp_dir),
        "--dataset_mode", DATASET_MODE,
        "--direction", DIRECTION,
        "--name", exp,
        "--checkpoints_dir", str(ckpt_root),
        "--preprocess", PREPROCESS,
        "--load_size", str(LOAD_SIZE),
        "--crop_size", str(CROP_SIZE),
        "--input_nc", str(INPUT_NC),
        "--output_nc", str(OUTPUT_NC),
        "--results_dir", str(results_dir),
        "--epoch", str(EPOCH),
        "--num_test", str(NUM_TEST),
    ]
    if EVAL:
        cmd.append("--eval")

    print(">>>", " ".join(shlex.quote(c) for c in cmd))
    ret = subprocess.run(cmd, check=False)
    print("Return code:", ret.returncode)

    # copy the generated file to requested --output
    out_dir = results_dir / exp / f"test_{EPOCH}" / "images"
    fake = out_dir / "test_fake.png"
    if not fake.exists():
        print("[ERROR] Could not find generated file:", fake)
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # if OUTPUT_NC==1 and you want to guarantee single-channel, convert to 'L'
    img = Image.open(fake)
    if OUTPUT_NC == 1:
        img = img.convert("L")
    img.save(out_path)
    print("Saved:", out_path)

if __name__ == "__main__":
    main()
