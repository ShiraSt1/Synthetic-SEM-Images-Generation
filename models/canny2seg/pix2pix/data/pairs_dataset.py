import os, glob, re
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

def list_pairs(split, allow_empty=False):
    """
    Return matched pairs [(edge_path, overlay_path)] for split in {train,val,test}.

    Assumes input datasets under /kaggle/input/** with these folders:
      train:     SEM_edges_2040/**  <->  SEM_overlay_2040/**
      val:       val_edges/**       <->  val_overlay/**
      test:      test_edges/**      <->  test_overlay/**
    """
    if split == "train":
        E_dirname, O_dirname = "SEM_edges_2040", "SEM_overlay_2040"
    elif split == "val":
        E_dirname, O_dirname = "val_edges", "val_overlay"
    elif split == "test":
        E_dirname, O_dirname = "test_edges", "test_overlay"
    else:
        raise ValueError("split must be train/val/test")

    roots = sorted([p for p in glob.glob("/kaggle/input/*") if os.path.isdir(p)])

    edge_files, over_files = [], []
    for root in roots:
        e_root = os.path.join(root, E_dirname)
        o_root = os.path.join(root, O_dirname)
        if os.path.isdir(e_root):
            edge_files += glob.glob(os.path.join(e_root, "**", "*_edges.*"), recursive=True)
        if os.path.isdir(o_root):
            over_files += glob.glob(os.path.join(o_root, "**", "*_overlay.*"), recursive=True)

    if (not edge_files or not over_files):
        if allow_empty:
            return []
        else:
            raise RuntimeError(
                f"Didn't find expected folders/files for split='{split}'. "
                f"Looked for '{E_dirname}' and '{O_dirname}' under /kaggle/input/*"
            )

    def base_key(p, suffix):
        name = os.path.splitext(os.path.basename(p))[0]
        return name.replace(suffix, "")

    edges_by_key = {base_key(p, "_edges"): p for p in edge_files}
    over_by_key  = {base_key(p, "_overlay"): p for p in over_files}

    keys = sorted(set(edges_by_key) & set(over_by_key))
    pairs = [(edges_by_key[k], over_by_key[k]) for k in keys]

    if not pairs and not allow_empty:
        raise RuntimeError(
                f"No matching pairs for split='{split}'. "
                "Make sure filenames share the same base (e.g., *_edges ↔ *_overlay)."
        )
    return pairs

class PairDataset(Dataset):
    def __init__(self, pairs, size=256):
        self.items = pairs
        self.size = size

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        a_path, b_path = self.items[i]
        A = Image.open(a_path).convert('L').resize((self.size,self.size), Image.BILINEAR)
        B = Image.open(b_path).convert('RGB').resize((self.size,self.size), Image.NEAREST)
        A = (np.array(A, dtype=np.float32)/255.0 - 0.5)/0.5
        B = (np.array(B, dtype=np.float32)/255.0 - 0.5)/0.5
        A = torch.from_numpy(A)[None, ...]
        B = torch.from_numpy(B).permute(2,0,1)
        return A, B
