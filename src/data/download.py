"""
Download module for Instacart Market Basket Analysis dataset from HuggingFace mirror.
"""

import sys
import argparse
from pathlib import Path
import requests
from tqdm import tqdm

from src.config import RAW_DATA_DIR, HF_DATASET_URL

FILES = {
    "aisles.csv": f"{HF_DATASET_URL}/aisles.csv",
    "departments.csv": f"{HF_DATASET_URL}/departments.csv",
    "products.csv": f"{HF_DATASET_URL}/products.csv",
    "orders.csv": f"{HF_DATASET_URL}/orders.csv",
    "order_products__train.csv": f"{HF_DATASET_URL}/order_products__train.csv",
    "order_products__prior.csv": f"{HF_DATASET_URL}/order_products__prior.csv",
}


def download_file(url: str, dest_path: Path, max_bytes: int | None = None, chunk_size: int = 1024 * 1024) -> None:
    """Download a file with streaming and progress bar. Optionally limits downloaded bytes."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        if max_bytes is None or dest_path.stat().st_size >= max_bytes:
            print(f"[OK] {dest_path.name} already exists ({dest_path.stat().st_size / (1024*1024):.2f} MB). Skipping.")
            return

    headers = {}
    if max_bytes is not None:
        headers["Range"] = f"bytes=0-{max_bytes - 1}"

    print(f"[DOWNLOADING] {dest_path.name} from {url}...")
    response = requests.get(url, headers=headers, stream=True, timeout=60)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    if max_bytes is not None and (total_size == 0 or total_size > max_bytes):
        total_size = max_bytes

    temp_path = dest_path.with_suffix(".tmp")
    downloaded = 0

    with open(temp_path, "wb") as f, tqdm(
        desc=dest_path.name,
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                break
            if max_bytes is not None and (downloaded + len(chunk) > max_bytes):
                allowed = max_bytes - downloaded
                f.write(chunk[:allowed])
                bar.update(allowed)
                break
            f.write(chunk)
            bar.update(len(chunk))
            downloaded += len(chunk)

    # In case of partial byte range, ensure we don't have a broken trailing line
    if max_bytes is not None:
        with open(temp_path, "rb+") as f:
            f.seek(max(0, downloaded - 4096))
            tail = f.read()
            last_newline = tail.rfind(b"\n")
            if last_newline != -1:
                cutoff = (downloaded - len(tail)) + last_newline + 1
                f.seek(cutoff)
                f.truncate()

    temp_path.replace(dest_path)
    print(f"[SAVED] {dest_path.name} ({dest_path.stat().st_size / (1024*1024):.2f} MB)")


def download_all(full: bool = False, prior_mb: int = 60) -> None:
    """
    Downloads dataset files.
    - aisles.csv, departments.csv, products.csv are always downloaded completely (~2.1MB total).
    - order_products__train.csv is downloaded completely (~24MB).
    - orders.csv is downloaded (~104MB).
    - order_products__prior.csv is downloaded either full (~550MB) or prior_mb (default 60MB, ~3.5 million lines).
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Essential catalog files
    for fname in ["aisles.csv", "departments.csv", "products.csv", "order_products__train.csv"]:
        dest = RAW_DATA_DIR / fname
        download_file(FILES[fname], dest)

    # 2. Orders file
    orders_dest = RAW_DATA_DIR / "orders.csv"
    if full:
        download_file(FILES["orders.csv"], orders_dest)
    else:
        # 30 MB of orders covers over 50,000 users and ~1 million orders
        download_file(FILES["orders.csv"], orders_dest, max_bytes=35 * 1024 * 1024)

    # 3. Prior order products
    prior_dest = RAW_DATA_DIR / "order_products__prior.csv"
    if full:
        download_file(FILES["order_products__prior.csv"], prior_dest)
    else:
        download_file(FILES["order_products__prior.csv"], prior_dest, max_bytes=prior_mb * 1024 * 1024)

    print("\n[SUCCESS] Dataset download completed in:", RAW_DATA_DIR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Instacart Dataset")
    parser.add_argument("--full", action="store_true", help="Download the entire 550MB prior dataset")
    parser.add_argument("--prior-mb", type=int, default=60, help="Megabytes of prior orders to download if not full")
    args = parser.parse_args()

    download_all(full=args.full, prior_mb=args.prior_mb)
