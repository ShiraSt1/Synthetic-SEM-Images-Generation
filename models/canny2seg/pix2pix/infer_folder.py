import os, glob, torch
import numpy as np
from PIL import Image
from models.unet import GeneratorUNet

def denorm(x): return (x.clamp(-1,1)+1)*0.5

def load_latest_from_resume(resume_dir, device):
    import re, glob, os, torch
    g = sorted(glob.glob(os.path.join(resume_dir, "G_epoch_*.pt")))
    d = sorted(glob.glob(os.path.join(resume_dir, "D_epoch_*.pt")))
    if not g: raise FileNotFoundError("No G_epoch_*.pt found in RESUME dir")
    def e(p): 
        m = re.search(r"_(\d+)\.pt$", os.path.basename(p))
        return int(m.group(1)) if m else 0
    emax = max(set(map(e,g)) & set(map(e,d)))
    G = GeneratorUNet(1,3).to(device)
    G.load_state_dict(torch.load(os.path.join(resume_dir, f"G_epoch_{emax:03d}.pt"), map_location=device))
    G.eval()
    return G, emax

def main(in_dir, out_dir, img_size=256, resume_dir="/kaggle/working/RESUME", device=None):
    os.makedirs(out_dir, exist_ok=True)
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    G, emax = load_latest_from_resume(resume_dir, device)
    print(f"[OK] Loaded G_epoch_{emax:03d}.pt from {resume_dir}")

    edge_files = []
    for ext in ("png","jpg","jpeg","bmp","tif","tiff"):
        edge_files += glob.glob(os.path.join(in_dir, f"*._edges.{ext}".replace("._",".*")))
        edge_files += glob.glob(os.path.join(in_dir, f"*_edges.{ext}"))
    if not edge_files:
        for ext in ("png","jpg","jpeg","bmp","tif","tiff"):
            edge_files += glob.glob(os.path.join(in_dir, f"*.{ext}"))
    print("Found", len(edge_files), "files")

    with torch.no_grad():
        for p in edge_files:
            name = os.path.splitext(os.path.basename(p))[0]
            outp = os.path.join(out_dir, f"pred_{name}.png")

            img = Image.open(p).convert('L').resize((img_size,img_size), Image.BILINEAR)
            arr = (np.array(img).astype(np.float32)/255.0 - 0.5)/0.5
            A   = torch.from_numpy(arr)[None,None,...].to(device)

            pred = G(A)
            pred_img = (denorm(pred)[0].permute(1,2,0).cpu().numpy()*255).astype(np.uint8)
            Image.fromarray(pred_img).save(outp)

    print("Saved to:", out_dir)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", required=True, help="Folder with *_edges.* images")
    ap.add_argument("--out-dir", default="/kaggle/working/preds")
    ap.add_argument("--img-size", type=int, default=256)
    ap.add_argument("--resume-dir", default="/kaggle/working/RESUME")
    args = ap.parse_args()
    main(args.in_dir, args.out_dir, args.img_size, args.resume_dir)
