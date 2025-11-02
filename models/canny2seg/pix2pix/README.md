# SEM pix2pix (Edges ➜ Overlay) — Repo Scaffold

This repo splits your Kaggle notebook into maintainable files, adds inference scripts,
and includes Kaggle dataset syncing helpers for checkpoints and samples.

## Quick Start (Kaggle Notebook)

1. **Attach your secret dataset** that contains `kaggle.json` in **Add data**.
2. Make sure your train/val folders exist under `/kaggle/input/**` with naming:
   - `SEM_edges_2040/**` ↔ `SEM_overlay_2040/**` (train)
   - `val_edges/**` ↔ `val_overlay/**` (val)

### Train (resume automatically from latest in checkpoints dataset)
```bash
python train_pix2pix.py --config configs/pix2pix.yaml
```

### Train resuming from a *specific* epoch (best-effort version pin)
```bash
python train_pix2pix.py --config configs/pix2pix.yaml --resume-epoch 145 --resume-version 184
```
> If your Kaggle CLI build doesn't support `-v` for version, the script will fall back
> to the active dataset version and print a warning.

### Inference on a folder
Ensure `/kaggle/working/RESUME` contains the generator checkpoint you want (training
script puts it there automatically). Then:
```bash
python infer_folder.py --in-dir /kaggle/input/test-pix2pix/test_edges --out-dir /kaggle/working/preds --img-size 256
```

## Files
- `train_pix2pix.py` – training loop + checkpoint/versioning with Kaggle datasets.
- `infer_folder.py` – batch inference for a folder of `*_edges.*` images.
- `models/unet.py`, `models/discriminator.py` – network definitions.
- `data/pairs_dataset.py` – pair listing & dataset.
- `utils/kaggle_sync.py` – dataset create/version + resume helpers (latest / specific epoch).
- `configs/pix2pix.yaml` – config; override for your experiments.
- `requirements.txt`, `.gitignore`, `PR_TEMPLATE.md`, `TRAINING_NOTES.md` – housekeeping.

## Notes
- Checkpoint dataset rate limits (HTTP 429) are handled with simple retries. If you still hit
  limits, increase the cadence (export less frequently) or re-run later.
- To pin to a specific dataset version reliably, you can also switch the *active* version in
  Kaggle UI and run without `--resume-version`.
