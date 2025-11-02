import os, json, glob, re, random, time, yaml
import numpy as np
from PIL import Image
from tqdm.auto import tqdm
import torch, torch.nn as nn, torch.nn.functional as F
from torch.utils.data import DataLoader

from models.unet import GeneratorUNet
from models.discriminator import PatchDiscriminator
from data.pairs_dataset import PairDataset, list_pairs
from utils.kaggle_sync import write_metadata, ensure_created_or_versioned, download_latest_pair_only, download_specific_epoch

def denorm(x): return (x.clamp(-1,1)+1)*0.5

def save_sample_grid(A,B,F,out_path,nmax=8):
    A = denorm(A[:nmax]).cpu(); B = denorm(B[:nmax]).cpu(); F = denorm(F[:nmax]).cpu()
    A3 = A.repeat(1,3,1,1)
    rows = []
    for i in range(min(nmax, A3.shape[0])):
        rows.append(torch.cat([A3[i], F[i], B[i]], dim=2))
    grid = torch.cat(rows, dim=1)
    img = (grid.permute(1,2,0).numpy()*255).astype(np.uint8)
    Image.fromarray(img).save(out_path)

def set_seed(s=42):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

def main(cfg_path="configs/pix2pix.yaml",
         resume_epoch=None,
         resume_version=None):
    with open(cfg_path, "r") as f:
        C = yaml.safe_load(f)

    INPUT_DATASET            = C["input_dataset"]
    KAGGLE_SECRET_DATASET    = C["kaggle_secret_dataset"]
    CHECKPOINTS_DATASET_SLUG = C["checkpoints_dataset_slug"]
    OUTPUTS_DATASET_SLUG     = C["outputs_dataset_slug"]

    IMG_SIZE   = int(C["img_size"])
    BATCH_SIZE = int(C["batch_size"])
    MAX_EPOCHS = int(C["max_epochs"])
    LR_G = float(C["lr_g"]); LR_D = float(C["lr_d"])
    LAMBDA_L1 = float(C["lambda_l1"])
    SEED = int(C["seed"])

    EXPORT_CKPT_EVERY_STEPS = int(C["export_ckpt_every_steps"])
    EXPORT_SAMPLES_EVERY_E  = int(C["export_samples_every_epochs"])

    os.makedirs("/root/.kaggle", exist_ok=True)
    secret_candidates = glob.glob("/kaggle/input/*/kaggle.json")
    if not secret_candidates:
        raise RuntimeError("kaggle.json not found in /kaggle/input — add your 'kaggle-json-secret' dataset to the notebook.")
    import shutil
    shutil.copy(secret_candidates[0], "/root/.kaggle/kaggle.json")
    os.chmod("/root/.kaggle/kaggle.json", 0o600)

    with open("/root/.kaggle/kaggle.json") as f:
        _kg = json.load(f)
    USERNAME = _kg.get("username") or _kg.get("user")
    if not USERNAME:
        raise RuntimeError("Failed to read username from kaggle.json")

    WORK_DIR = "/kaggle/working"
    CKPT_LOCAL_DIR = f"{WORK_DIR}/CKPTS"
    OUT_LOCAL_DIR  = f"{WORK_DIR}/EXPORT"
    RESUME_DIR     = f"{WORK_DIR}/RESUME"
    os.makedirs(CKPT_LOCAL_DIR, exist_ok=True)
    os.makedirs(OUT_LOCAL_DIR, exist_ok=True)
    os.makedirs(RESUME_DIR, exist_ok=True)

    set_seed(SEED)

    train_pairs = list_pairs("train")
    val_pairs   = list_pairs("val")
    train_dl = DataLoader(PairDataset(train_pairs, IMG_SIZE), batch_size=BATCH_SIZE, shuffle=True,  num_workers=2, drop_last=True)
    val_dl   = DataLoader(PairDataset(val_pairs,   IMG_SIZE), batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    G = GeneratorUNet(1,3).to(device)
    D = PatchDiscriminator(4).to(device)
    optG = torch.optim.Adam(G.parameters(), lr=LR_G, betas=(0.5,0.999))
    optD = torch.optim.Adam(D.parameters(), lr=LR_D, betas=(0.5,0.999))
    bce = nn.BCEWithLogitsLoss()
    l1  = nn.L1Loss()

    latest_e = 0
    if resume_epoch is not None:
        print(f"[RESUME] Trying epoch={resume_epoch} (version={resume_version})")
        latest_e = download_specific_epoch(USERNAME, CHECKPOINTS_DATASET_SLUG, resume_epoch, RESUME_DIR, version=resume_version)
    else:
        latest_e = download_latest_pair_only(USERNAME, CHECKPOINTS_DATASET_SLUG, RESUME_DIR)

    if latest_e > 0:
        print(f"Resuming from epoch {latest_e}")
        G.load_state_dict(torch.load(os.path.join(RESUME_DIR, f"G_epoch_{latest_e:03d}.pt"), map_location=device))
        D.load_state_dict(torch.load(os.path.join(RESUME_DIR, f"D_epoch_{latest_e:03d}.pt"), map_location=device))
        start_epoch = latest_e + 1
    else:
        start_epoch = 1

    history = []
    global_step = 0

    def export_ckpt_version(epoch, step_msg):
        torch.save(G.state_dict(), f"{CKPT_LOCAL_DIR}/G_epoch_{epoch:03d}.pt")
        torch.save(D.state_dict(), f"{CKPT_LOCAL_DIR}/D_epoch_{epoch:03d}.pt")
        ensure_created_or_versioned(CKPT_LOCAL_DIR, USERNAME, CHECKPOINTS_DATASET_SLUG, message=step_msg)

    def export_outputs_version(epoch, note):
        A, B = next(iter(val_dl))
        A, B = A.to(device), B.to(device)
        with torch.no_grad(): F = G(A)
        os.makedirs(f"{OUT_LOCAL_DIR}/samples", exist_ok=True)
        save_sample_grid(A,B,F, f"{OUT_LOCAL_DIR}/samples/epoch_{epoch:03d}.png")
        with open(f"{OUT_LOCAL_DIR}/training_history.json", "w") as f:
            json.dump(history, f, indent=2)
        ensure_created_or_versioned(OUT_LOCAL_DIR, USERNAME, OUTPUTS_DATASET_SLUG, message=note)

    for epoch in range(start_epoch, MAX_EPOCHS+1):
        G.train(); D.train()
        g_run=d_run=l1_run=0.0
        for A,B in tqdm(train_dl, desc=f"Epoch {epoch}"):
            A,B = A.to(device), B.to(device)

            with torch.no_grad():
                F_fake = G(A)
            real_logits = D(torch.cat([A,B],1))
            fake_logits = D(torch.cat([A,F_fake.detach()],1))
            d_loss = bce(real_logits, torch.ones_like(real_logits)) + \
                     bce(fake_logits, torch.zeros_like(fake_logits))
            optD.zero_grad(); d_loss.backward(); optD.step()

            F_fake = G(A)
            adv = bce(D(torch.cat([A,F_fake],1)), torch.ones_like(fake_logits))
            l1_loss = l1(F_fake, B)*LAMBDA_L1
            g_loss = adv + l1_loss
            optG.zero_grad(); g_loss.backward(); optG.step()

            g_run += g_loss.item(); d_run += d_loss.item(); l1_run += l1_loss.item()
            global_step += 1

            if global_step % EXPORT_CKPT_EVERY_STEPS == 0:
                export_ckpt_version(epoch, step_msg=f"epoch {epoch} step {global_step}")

        n = len(train_dl)
        epoch_stats = {"epoch": epoch, "g": g_run/n, "d": d_run/n, "l1": l1_run/n}
        history.append(epoch_stats)

        if epoch % EXPORT_SAMPLES_EVERY_E == 0 or epoch == start_epoch:
            export_outputs_version(epoch, note=f"epoch {epoch}")

    export_ckpt_version(epoch, step_msg=f"final epoch {epoch}")
    export_outputs_version(epoch, note=f"final epoch {epoch}")
    print("Done.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/pix2pix.yaml")
    ap.add_argument("--resume-epoch", type=int, default=None, help="Resume from specific epoch (downloads matching G/D).")
    ap.add_argument("--resume-version", type=int, default=None, help="Try to pull from a specific Kaggle dataset version (best-effort).")
    args = ap.parse_args()
    main(cfg_path=args.config, resume_epoch=args.resume_epoch, resume_version=args.resume_version)
