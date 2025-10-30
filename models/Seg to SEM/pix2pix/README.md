# Wafer Pix2Pix – SEM Image Translation

This project trains and tests a **Pix2Pix** model that converts **segmentation maps of SEM wafers** into realistic SEM images.

> **Mandatory (for model weights):**
> ```bash
> git lfs install
> git lfs pull
> ```

## 📂 Project Structure
- `pix2pix/` – original model source code (from the [CycleGAN & Pix2Pix repo](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix))
- `checkpoints/` – pretrained models (tracked via **Git LFS**)
- `notebooks/` – Kaggle notebooks used for training and testing
- `examples/` – sample segmentation inputs for inference
- `outputs/` – generated SEM results
- `single_inference.py` – simple CLI script for single-image inference (only needs input/output paths)
- `requirements.txt` – Python dependencies

---

## 🚀 Quick Start

```bash
# 1) Clone the repo (or navigate to this module inside the parent repo)
git clone https://github.com/KamaTechOrg/SemTTI.git
cd SemTTI/models/Seg_to_SEM/pix2pix_model  # adjust path if different

# 2) Python deps
pip install -r requirements.txt

# 3) (If not done yet) enable Git LFS for weights
git lfs install
git lfs pull   # downloads the large weights tracked by LFS
```

### Run Single Image Inference

After placing (or pulling) your trained model under `checkpoints/wafer_pix2pix_AtoB_256_out1/`:
 
```bash
python single_inference.py --input ./examples/sample_input.png --output ./outputs/sample_input_fake.png
```

### What Happens
- Loads your **trained Pix2Pix generator (G)**
- Runs inference using the official [CycleGAN & Pix2Pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix) implementation
- Saves the generated SEM image to your specified output path.

### Notes
- Edit default parameters (model name, sizes, etc.) directly inside `single_inference.py`.
- Input should match your training dimensions (e.g. **256×256**).
- Output is grayscale (1-channel) .

---

## 📦 Large Files (Git LFS)

We track checkpoints/weights via **Git LFS** to avoid huge Git history.

### If you’re a contributor pushing new weights
```bash
git lfs install
git lfs track "*.pth" "*.pt" "*.ckpt" "*.safetensors" "*.onnx" "*.bin" "*.npz" "*.tar" "*.tar.gz" "*.zip"
git add .gitattributes
git add path/to/your/weights
git commit -m "chore: track weights with Git LFS"
git push
```

### Selective LFS download (optional)
If you don’t want to download all large files:
```bash
# only fetch checkpoints (examples)
git lfs fetch --include="checkpoints/**"
git lfs checkout --include="checkpoints/**"
```

### Troubleshooting
- **I only see tiny text files instead of weights** → run `git lfs install` and then `git lfs pull` (or use the selective commands above).
- **Push blocked due to >100MB file** → you probably didn’t track it with LFS. Run the `git lfs track …` commands above and recommit, or use GitHub Releases/Hugging Face for hosting.

---

## 📁 Example Folder Structure
```
pix2pix_model/
├─ pix2pix/                         ← model source code
├─ checkpoints/
│  └─ wafer_pix2pix_AtoB_256_out1/
│     ├─ latest_net_G.pth
│     └─ train_opt.txt
├─ notebooks/
│  ├─ training.ipynb
│  └─ testing.ipynb
├─ examples/
│  └─ sample_input.png
├─ outputs/
│  └─ sample_input_fake.png
├─ single_inference.py
├─ README.md
└─ requirements.txt
```

---

## 🧠 Credits
- Based on [Pix2Pix by Jun-Yan Zhu et al.](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
- Adapted for **Applied Materials SEM wafer dataset** by your team.
