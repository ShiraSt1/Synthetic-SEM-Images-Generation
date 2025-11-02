# Training Notes (fill during/after runs)

## Datasets
- Input dataset: `yealsh/canny2segmentation-dataset`
- Checkpoints dataset: `edgeseg-pix2pix-ckpts`
- Outputs dataset: `edgeseg-pix2pix-outputs`

## Last Good Run
- Epochs: 1..N
- Best val sample: `EXPORT/samples/epoch_150.png`
- History JSON: `EXPORT/training_history.json`

## Hyperparameters
- `img_size`: 256
- `batch_size`: 8
- `max_epochs`: 150
- `lr_g`: 2e-4
- `lr_d`: 2e-4
- `lambda_l1`: 100

## Observations
- Add bullets on artifacts, over-smoothing vs sharpness, effect of lambda_l1, etc.

## Next Steps
- Try `lambda_l1` ∈ {100, 150}
- Try `img_size` 256 → 384 / 512
- Export cadence tweaks to avoid 429s
