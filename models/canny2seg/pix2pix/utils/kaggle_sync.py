import os, glob, json, re, time, subprocess

def _run(cmd):
    print(f"$ {cmd}")
    return os.system(cmd)

def write_metadata(dirpath, username, slug, title=None, license_name="CC0-1.0"):
    os.makedirs(dirpath, exist_ok=True)
    meta = {"title": title or slug.replace("-", " ").title(),
            "id": f"{username}/{slug}",
            "licenses": [{"name": license_name}]}
    with open(os.path.join(dirpath, "dataset-metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

def ensure_created_or_versioned(dirpath, username, slug, message, max_retries=5):
    others = [p for p in glob.glob(os.path.join(dirpath, "*"))
              if os.path.basename(p) != "dataset-metadata.json"]
    if not others:
        raise RuntimeError(f"'{dirpath}' is empty. Add at least one file before create/version.")

    write_metadata(dirpath, username, slug)

    rc_create = _run(f'kaggle datasets create -p "{dirpath}" -r zip')
    rc_version = _run(f'kaggle datasets version -p "{dirpath}" -m "{message}"')
    if rc_version != 0:
        rc_version = _run(f'kaggle datasets version -p "{dirpath}" -m "{message}" -r zip')

    tries = 0
    while rc_create != 0 and rc_version != 0 and tries < max_retries:
        tries += 1
        wait = min(60, 5 * tries)
        print(f"[WARN] Kaggle create/version failed. Sleeping {wait}s and retrying ({tries}/{max_retries})...")
        time.sleep(wait)
        rc_version = _run(f'kaggle datasets version -p "{dirpath}" -m "retry {tries}: {message}"')
        if rc_version == 0:
            break

    if rc_create != 0 and rc_version != 0:
        raise RuntimeError("Failed to create/version Kaggle dataset. If you see 403/429, try again later.")

    print(f"[OK] dataset {username}/{slug} created/versioned.")

def download_latest_pair_only(username, slug, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    token = None
    files = []
    while True:
        cmd = f'kaggle datasets files {username}/{slug}'
        if token: cmd += f' --page-token {token}'
        out = subprocess.getoutput(cmd)
        files += re.findall(r'(G_epoch_\d+\.pt|D_epoch_\d+\.pt)', out)
        m = re.search(r'Next Page Token = (\S+)', out)
        if m: token = m.group(1)
        else: break

    if not files:
        print("[INFO] No files found in checkpoints dataset. Starting from scratch.")
        return 0

    g_epochs = {int(re.search(r'_(\d+)\.pt$', f).group(1)) for f in files if f.startswith('G_epoch_')}
    d_epochs = {int(re.search(r'_(\d+)\.pt$', f).group(1)) for f in files if f.startswith('D_epoch_')}
    common = sorted(g_epochs & d_epochs)
    if not common:
        print("[WARN] Found files but no matching G/D pairs.")
        return 0

    e = common[-1]
    need = [f"G_epoch_{e:03d}.pt", f"D_epoch_{e:03d}.pt"]
    for fname in need:
        rc = _run(f'kaggle datasets download -d {username}/{slug} -f {fname} -p "{target_dir}" -q')
        if rc != 0:
            print(f"[WARN] download rc={rc} for {fname}")
    for z in glob.glob(os.path.join(target_dir, "*.zip")):
        _run(f'unzip -o "{z}" -d "{target_dir}" >/dev/null')
        os.remove(z)
    print(f"[OK] Downloaded: {need}")
    return e

def download_specific_epoch(username, slug, epoch, target_dir, version=None):
    os.makedirs(target_dir, exist_ok=True)
    files = [f"G_epoch_{epoch:03d}.pt", f"D_epoch_{epoch:03d}.pt"]
    for fname in files:
        if version is not None:
            rc = _run(f'kaggle datasets download -d {username}/{slug} -v {version} -f {fname} -p "{target_dir}" -q')
            if rc != 0:
                print(f"[WARN] '-v {version}' not supported or file not in that version. Falling back to active version for {fname}.")
                rc = _run(f'kaggle datasets download -d {username}/{slug} -f {fname} -p "{target_dir}" -q')
        else:
            rc = _run(f'kaggle datasets download -d {username}/{slug} -f {fname} -p "{target_dir}" -q')
        if rc != 0:
            print(f"[WARN] download rc={rc} for {fname}")

    for z in glob.glob(os.path.join(target_dir, "*.zip")):
        _run(f'unzip -o "{z}" -d "{target_dir}" >/dev/null')
        os.remove(z)

    ok = all(os.path.exists(os.path.join(target_dir, f)) for f in files)
    if ok:
        print(f"[OK] epoch {epoch:03d} ready in {target_dir}")
        return epoch
    else:
        print(f"[ERR] epoch {epoch:03d} files not found after download attempts.")
        return 0
