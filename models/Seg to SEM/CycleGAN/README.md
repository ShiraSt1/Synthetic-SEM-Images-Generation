# CycleGAN Training & Metrics

This repository contains a Kaggle-style notebook and helper scripts to:
- train a CycleGAN on a custom dataset
- manage checkpoints (copy/clean)
- run tests A->B and B->A
- prepare folders for FID/KID
- optionally train a small binary classifier to check image realism

## Requirements
- Python 3.8+
- PyTorch + Torchvision
- PIL (Pillow)
- Matplotlib

## Dataset layout
Expected dataset:
- A train/test structure for CycleGAN
- Generated results will be exported to `/kaggle/working/...` (see the notebook)

## How to run
1. Open the notebook in Kaggle.
2. Edit the config section (paths, owner, repo).
3. Run the training cell.
4. Run the metrics section (FID/KID).

## Notes
- Paths are currently set for Kaggle. Adjust them if you run locally.
- Do not delete `dataset-metadata.json` if it already exists.
