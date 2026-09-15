"""
Training and Evaluation script for Hybrid Two-Tower Supermarket Recommender.
Computes industry metrics: HitRate@K, Recall@K, NDCG@K, MRR on held-out customer baskets.
"""

import argparse
import json
import math
import pickle
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

from src.config import (
    PROCESSED_DATA_DIR,
    MODEL_DIR,
    BATCH_SIZE,
    NUM_EPOCHS,
    LEARNING_RATE,
    TEMPERATURE,
    OUTPUT_EMBEDDING_DIM,
)
from src.models.two_tower import HybridTwoTowerModel


class GroceryInteractionDataset(Dataset):
    """
    PyTorch Dataset pairing user profile/context with purchased item attributes.
    """
    def __init__(
        self,
        interactions_df: pd.DataFrame,
        user_profiles: dict,
        catalog_mappings: dict,
        item_stats: dict,
        num_users: int,
    ):
        self.interactions = interactions_df
        self.num_users = num_users
        
        # User lookup features
        self.dept_affinity = user_profiles["user_dept_affinity"]
        self.cadence = user_profiles["user_cadence"]

        # Item lookup features
        catalog_df = catalog_mappings["catalog_df"].set_index("item_idx")
        self.item_aisles = catalog_df["aisle_idx"].to_dict()
        self.item_depts = catalog_df["dept_idx"].to_dict()

        self.item_stats = item_stats

        # Pre-extract arrays for ultra-fast indexing
        self.user_indices = self.interactions["user_idx"].values
        self.item_indices = self.interactions["item_idx"].values
        self.dows = self.interactions["order_dow"].values
        self.hours = self.interactions["order_hour"].values
        self.reorders = self.interactions["reordered"].values

        # Default fallback feature vectors
        self.default_affinity = np.ones(catalog_mappings["num_departments"], dtype=np.float32) / catalog_mappings["num_departments"]

    def __len__(self):
        return len(self.interactions)

    def __getitem__(self, idx):
        u_idx = int(self.user_indices[idx])
        it_idx = int(self.item_indices[idx])
        dow = int(self.dows[idx])
        hour = int(self.hours[idx])
        reordered = int(self.reorders[idx])

        # User profile
        aff = self.dept_affinity.get(u_idx, self.default_affinity)
        cad = self.cadence.get(u_idx, {"total_orders": 10, "avg_days_between_orders": 10.0})
        cadence_feat = np.array(
            [math.log1p(cad["total_orders"]), min(cad["avg_days_between_orders"], 30.0) / 30.0],
            dtype=np.float32,
        )

        # Item profile
        aisle_idx = self.item_aisles.get(it_idx, 0)
        dept_idx = self.item_depts.get(it_idx, 0)
        stats = self.item_stats.get(it_idx, {"log_purchases": 0.0, "reorder_rate": 0.0, "avg_add_to_cart": 5.0})
        item_feat = np.array(
            [stats.get("log_purchases", 0.0), stats.get("reorder_rate", 0.0), min(stats.get("avg_add_to_cart", 5.0), 20.0) / 20.0],
            dtype=np.float32,
        )

        return {
            "user_idx": u_idx,
            "dept_affinity": torch.tensor(aff, dtype=torch.float32),
            "cadence_features": torch.tensor(cadence_feat, dtype=torch.float32),
            "dow": dow,
            "hour": hour,
            "item_idx": it_idx,
            "aisle_idx": aisle_idx,
            "dept_idx": dept_idx,
            "item_features": torch.tensor(item_feat, dtype=torch.float32),
            "reordered": reordered,
        }


def collate_fn(batch):
    return {
        "user_inputs": {
            "user_idx": torch.tensor([b["user_idx"] for b in batch], dtype=torch.long),
            "dept_affinity": torch.stack([b["dept_affinity"] for b in batch]),
            "cadence_features": torch.stack([b["cadence_features"] for b in batch]),
            "dow": torch.tensor([b["dow"] for b in batch], dtype=torch.long),
            "hour": torch.tensor([b["hour"] for b in batch], dtype=torch.long),
        },
        "item_inputs": {
            "item_idx": torch.tensor([b["item_idx"] for b in batch], dtype=torch.long),
            "aisle_idx": torch.tensor([b["aisle_idx"] for b in batch], dtype=torch.long),
            "dept_idx": torch.tensor([b["dept_idx"] for b in batch], dtype=torch.long),
            "item_features": torch.stack([b["item_features"] for b in batch]),
        },
        "reordered": torch.tensor([b["reordered"] for b in batch], dtype=torch.long),
    }


def precompute_item_embeddings(
    model: HybridTwoTowerModel,
    catalog_mappings: dict,
    item_stats: dict,
    device: torch.device,
    batch_size: int = 1024,
) -> torch.Tensor:
    """Precomputes and normalizes item embeddings for the entire catalog."""
    model.eval()
    num_items = catalog_mappings["num_items"]
    catalog_df = catalog_mappings["catalog_df"].set_index("item_idx")
    aisle_dict = catalog_df["aisle_idx"].to_dict()
    dept_dict = catalog_df["dept_idx"].to_dict()

    all_embeddings = []

    with torch.no_grad():
        for start_idx in range(0, num_items, batch_size):
            end_idx = min(start_idx + batch_size, num_items)
            chunk_indices = list(range(start_idx, end_idx))

            aisles = [aisle_dict.get(i, 0) for i in chunk_indices]
            depts = [dept_dict.get(i, 0) for i in chunk_indices]
            features = []
            for i in chunk_indices:
                st = item_stats.get(i, {"log_purchases": 0.0, "reorder_rate": 0.0, "avg_add_to_cart": 5.0})
                features.append([
                    st.get("log_purchases", 0.0),
                    st.get("reorder_rate", 0.0),
                    min(st.get("avg_add_to_cart", 5.0), 20.0) / 20.0,
                ])

            item_inputs = {
                "item_idx": torch.tensor(chunk_indices, dtype=torch.long, device=device),
                "aisle_idx": torch.tensor(aisles, dtype=torch.long, device=device),
                "dept_idx": torch.tensor(depts, dtype=torch.long, device=device),
                "item_features": torch.tensor(features, dtype=torch.float32, device=device),
            }

            emb = model.get_item_embedding(item_inputs)
            all_embeddings.append(emb.cpu())

    return torch.cat(all_embeddings, dim=0)


def evaluate_model(
    model: HybridTwoTowerModel,
    item_embeddings: torch.Tensor,
    val_baskets: dict,
    user_profiles: dict,
    catalog_mappings: dict,
    device: torch.device,
    k_list: list = [10, 20],
) -> dict:
    """
    Evaluates Top-K retrieval on validation customer baskets.
    Metrics: HitRate@K, Recall@K, NDCG@K, MRR.
    """
    model.eval()
    dept_affinity = user_profiles["user_dept_affinity"]
    cadence = user_profiles["user_cadence"]
    default_aff = np.ones(catalog_mappings["num_departments"], dtype=np.float32) / catalog_mappings["num_departments"]

    hits = {k: 0 for k in k_list}
    recalls = {k: [] for k in k_list}
    ndcgs = {k: [] for k in k_list}
    mrrs = []

    # Move item matrix to evaluation device
    item_mat = item_embeddings.to(device)

    with torch.no_grad():
        for u_idx, basket_info in val_baskets.items():
            target_items = set(basket_info["target_items"])
            if not target_items:
                continue

            aff = dept_affinity.get(u_idx, default_aff)
            cad = cadence.get(u_idx, {"total_orders": 10, "avg_days_between_orders": 10.0})
            cad_feat = [math.log1p(cad["total_orders"]), min(cad["avg_days_between_orders"], 30.0) / 30.0]

            user_inputs = {
                "user_idx": torch.tensor([u_idx], dtype=torch.long, device=device),
                "dept_affinity": torch.tensor([aff], dtype=torch.float32, device=device),
                "cadence_features": torch.tensor([cad_feat], dtype=torch.float32, device=device),
                "dow": torch.tensor([2], dtype=torch.long, device=device),
                "hour": torch.tensor([14], dtype=torch.long, device=device),
            }

            u_emb = model.get_user_embedding(user_inputs)  # (1, D)
            scores = torch.matmul(u_emb, item_mat.T).squeeze(0)  # (num_items)
            top_k_indices = torch.topk(scores, k=max(k_list)).indices.cpu().numpy()

            # Calculate metrics
            first_hit_rank = None
            for k in k_list:
                preds_k = set(top_k_indices[:k])
                intersection = target_items.intersection(preds_k)
                if len(intersection) > 0:
                    hits[k] += 1
                recalls[k].append(len(intersection) / len(target_items))

                # NDCG@K
                dcg = 0.0
                for rank, pred_item in enumerate(top_k_indices[:k]):
                    if pred_item in target_items:
                        dcg += 1.0 / math.log2(rank + 2)
                        if first_hit_rank is None:
                            first_hit_rank = rank + 1

                idcg = sum([1.0 / math.log2(r + 2) for r in range(min(k, len(target_items)))])
                ndcgs[k].append(dcg / idcg if idcg > 0 else 0.0)

            mrrs.append(1.0 / first_hit_rank if first_hit_rank else 0.0)

    num_eval_users = len(val_baskets)
    results = {
        f"HitRate@{k}": round(hits[k] / num_eval_users, 4) for k in k_list
    }
    for k in k_list:
        results[f"Recall@{k}"] = round(float(np.mean(recalls[k])), 4)
        results[f"NDCG@{k}"] = round(float(np.mean(ndcgs[k])), 4)
    results["MRR"] = round(float(np.mean(mrrs)), 4)
    results["NumEvalUsers"] = num_eval_users
    return results


def train():
    parser = argparse.ArgumentParser(description="Train Hybrid Two-Tower Model")
    parser.add_argument("--epochs", type=int, default=NUM_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--lr", type=float, default=LEARNING_RATE)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    device = torch.device(args.device)
    print(f"[START] Training Hybrid Two-Tower on device: {device}")

    # Load preprocessed files
    with open(PROCESSED_DATA_DIR / "catalog.pkl", "rb") as f:
        catalog_mappings = pickle.load(f)
    with open(PROCESSED_DATA_DIR / "user_mappings.pkl", "rb") as f:
        user_mappings = pickle.load(f)
    with open(PROCESSED_DATA_DIR / "user_profiles.pkl", "rb") as f:
        user_profiles = pickle.load(f)
    with open(PROCESSED_DATA_DIR / "item_stats.pkl", "rb") as f:
        item_stats = pickle.load(f)
    with open(PROCESSED_DATA_DIR / "val_baskets.pkl", "rb") as f:
        val_baskets = pickle.load(f)

    train_df = pd.read_parquet(PROCESSED_DATA_DIR / "train_interactions.parquet")

    num_users = len(user_mappings["user_to_idx"])
    num_items = catalog_mappings["num_items"]
    num_aisles = catalog_mappings["num_aisles"]
    num_depts = catalog_mappings["num_departments"]

    print(f"Catalog size: {num_items} products | Active users: {num_users}")

    dataset = GroceryInteractionDataset(
        interactions_df=train_df,
        user_profiles=user_profiles,
        catalog_mappings=catalog_mappings,
        item_stats=item_stats,
        num_users=num_users,
    )

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        drop_last=True,
    )

    model = HybridTwoTowerModel(
        num_users=num_users,
        num_items=num_items,
        num_aisles=num_aisles,
        num_depts=num_depts,
        embedding_dim=OUTPUT_EMBEDDING_DIM,
        temperature=TEMPERATURE,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    # Training Loop
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        retrieval_loss_acc = 0.0
        reorder_loss_acc = 0.0

        pbar = tqdm(loader, desc=f"Epoch {epoch}/{args.epochs}")
        for batch in pbar:
            user_inputs = {k: v.to(device) for k, v in batch["user_inputs"].items()}
            item_inputs = {k: v.to(device) for k, v in batch["item_inputs"].items()}
            reordered = batch["reordered"].to(device)

            optimizer.zero_grad()
            loss, loss_dict = model(user_inputs, item_inputs, reordered=reordered)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            retrieval_loss_acc += loss_dict["retrieval_loss"].item()
            reorder_loss_acc += loss_dict.get("reorder_loss", torch.tensor(0.0)).item()

            pbar.set_postfix({
                "loss": f"{loss.item():.4f}",
                "retrieval": f"{loss_dict['retrieval_loss'].item():.4f}",
            })

        scheduler.step()
        avg_loss = total_loss / len(loader)
        print(f"Epoch {epoch} Summary - Avg Loss: {avg_loss:.4f} (Retrieval: {retrieval_loss_acc / len(loader):.4f}, Reorder: {reorder_loss_acc / len(loader):.4f})")

    # Precompute all item embeddings for ultra-fast serving
    print("\n[COMPUTING] Precomputing dense item embeddings for catalog...")
    item_embeddings = precompute_item_embeddings(
        model=model,
        catalog_mappings=catalog_mappings,
        item_stats=item_stats,
        device=device,
    )

    # Evaluate on held-out customer baskets
    print("[EVALUATING] Running evaluation on held-out validation baskets...")
    eval_metrics = evaluate_model(
        model=model,
        item_embeddings=item_embeddings,
        val_baskets=val_baskets,
        user_profiles=user_profiles,
        catalog_mappings=catalog_mappings,
        device=device,
    )

    print("\n" + "=" * 45)
    print("      TWO-TOWER VALIDATION BENCHMARK")
    print("=" * 45)
    for k, v in eval_metrics.items():
        print(f"{k:>18}: {v}")
    print("=" * 45 + "\n")

    # Save artifacts
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODEL_DIR / "two_tower_weights.pt")
    torch.save(item_embeddings, MODEL_DIR / "item_embeddings.pt")

    with open(MODEL_DIR / "evaluation_metrics.json", "w") as f:
        json.dump(eval_metrics, f, indent=2)

    print(f"[SAVED] Model weights and precomputed item embeddings saved to: {MODEL_DIR}")


if __name__ == "__main__":
    train()
