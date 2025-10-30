# Wafer Pix2Pix – SEM Image Translation

This project trains and tests a **Pix2Pix** model that converts **segmentation maps of SEM wafers** into realistic SEM images.

## 📂 Project Structure
- `pix2pix/` – original model source code (from the [CycleGAN & Pix2Pix repo](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix))
- `checkpoints/` – pretrained models
- `notebooks/` – Kaggle notebooks used for training and testing
- `examples/` – sample segmentation inputs for inference
- `outputs/` – generated SEM results
- `single_inference.py` – simple CLI script for single-image inference (only needs input/output paths)
- `requirements.txt` – Python dependencies

---

## 🚀 Quick Start

```bash
git clone https://github.com/<yourusername>/wafer-pix2pix.git
cd wafer-pix2pix
pip install -r requirements.txt
```

### Run Single Image Inference

After placing your trained model under `checkpoints/wafer_pix2pix_AtoB_256_out1/`:
 
```bash
python single_inference.py --input ./examples/sample_input.png --output ./outputs/sample_input_fake.png
```

### What Happens
- Loads your **trained Pix2Pix generator (G)**  
- Runs inference using the official [CycleGAN & Pix2Pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix) repo  
- Saves the generated SEM image to your specified output path.

### Notes
- Edit default parameters (model name, sizes, etc.) directly inside `single_inference.py`.
- Input should match your training dimensions (e.g. **256×256**).
- Output is grayscale (1-channel) since training was done with `output_nc=1`.

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
├─ single_inference.py
├─ README.md
└─ requirements.txt
```

---

## 🧠 Credits
- Based on [Pix2Pix by Jun-Yan Zhu et al.](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix)
- Adapted for **Applied Materials SEM wafer dataset** by your team.
