"""
Preprocessing and Feature Engineering pipeline for Instacart Grocery Recommender.
Generates:
1. Catalog index & item metadata
2. User profile & department affinity vectors
3. User-Item repeat consumption cadence (depletion ratios)
4. Co-occurrence matrix for live cart complementarity
5. Two-Tower training dataset & validation evaluation baskets
"""

import argparse
import pickle
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
)


def build_catalog(raw_dir: Path, processed_dir: Path):
    """Builds clean product, aisle, and department metadata mappings."""
    print("[1/5] Building product catalog and categorical indices...")
    products = pd.read_csv(raw_dir / "products.csv")
    aisles = pd.read_csv(raw_dir / "aisles.csv")
    departments = pd.read_csv(raw_dir / "departments.csv")

    # Merge hierarchy
    catalog = products.merge(aisles, on="aisle_id", how="left").merge(departments, on="department_id", how="left")

    # Filter out missing or malformed entries
    catalog["product_name"] = catalog["product_name"].fillna("Unknown Product")
    catalog["aisle"] = catalog["aisle"].fillna("missing")
    catalog["department"] = catalog["department"].fillna("missing")

    # Continuous 0-based indices for neural embeddings
    unique_products = sorted(catalog["product_id"].unique())
    unique_aisles = sorted(catalog["aisle_id"].unique())
    unique_departments = sorted(catalog["department_id"].unique())

    product_to_idx = {pid: idx for idx, pid in enumerate(unique_products)}
    idx_to_product = {idx: pid for pid, idx in product_to_idx.items()}

    aisle_to_idx = {aid: idx for idx, aid in enumerate(unique_aisles)}
    dept_to_idx = {did: idx for idx, did in enumerate(unique_departments)}

    catalog["item_idx"] = catalog["product_id"].map(product_to_idx)
    catalog["aisle_idx"] = catalog["aisle_id"].map(aisle_to_idx)
    catalog["dept_idx"] = catalog["department_id"].map(dept_to_idx)

    catalog_dict = catalog.set_index("item_idx").to_dict(orient="index")

    mappings = {
        "num_items": len(unique_products),
        "num_aisles": len(unique_aisles),
        "num_departments": len(unique_departments),
        "product_to_idx": product_to_idx,
        "idx_to_product": idx_to_product,
        "aisle_to_idx": aisle_to_idx,
        "dept_to_idx": dept_to_idx,
        "catalog_df": catalog,
        "catalog_dict": catalog_dict,
    }

    with open(processed_dir / "catalog.pkl", "wb") as f:
        pickle.dump(mappings, f)

    print(f"Catalog saved: {len(unique_products)} products, {len(unique_aisles)} aisles, {len(unique_departments)} depts")
    return mappings


def process_features(
    raw_dir: Path,
    processed_dir: Path,
    catalog_mappings: dict,
    max_users: int = 5000,
    min_user_orders: int = 4,
):
    """
    Processes user order histories, building:
    - User profiles & department preferences
    - Inter-purchase intervals & depletion metrics
    - Training positive interactions for Two-Tower Retrieval
    - Validation test baskets for ranking evaluation
    - Basket co-occurrence matrix for cart re-ranking
    """
    print(f"[2/5] Loading orders and selecting top {max_users} active users...")
    orders_df = pd.read_csv(raw_dir / "orders.csv")
    
    # Filter users with sufficient order history
    user_order_counts = orders_df[orders_df["eval_set"] == "prior"].groupby("user_id")["order_id"].count()
    eligible_users = user_order_counts[user_order_counts >= min_user_orders].index.values

    if len(eligible_users) > max_users:
        selected_users = eligible_users[:max_users]
    else:
        selected_users = eligible_users

    selected_users_set = set(selected_users)
    print(f"Selected {len(selected_users_set)} users with >= {min_user_orders} prior orders.")

    user_to_idx = {uid: idx for idx, uid in enumerate(sorted(selected_users_set))}
    idx_to_user = {idx: uid for uid, idx in user_to_idx.items()}

    # Filter orders to selected users
    user_orders = orders_df[orders_df["user_id"].isin(selected_users_set)].copy()
    user_orders.sort_values(by=["user_id", "order_number"], inplace=True)

    order_meta = user_orders.set_index("order_id")[["user_id", "eval_set", "order_number", "order_dow", "order_hour_of_day", "days_since_prior_order"]].to_dict(orient="index")

    print("[3/5] Loading order products (prior & train)...")
    priors_df = pd.read_csv(raw_dir / "order_products__prior.csv")
    
    # Keep only order products corresponding to our selected users' orders
    relevant_order_ids = set(user_orders["order_id"].values)
    priors_df = priors_df[priors_df["order_id"].isin(relevant_order_ids)].copy()

    # Load train products (target baskets for evaluation)
    trains_df = pd.read_csv(raw_dir / "order_products__train.csv")
    trains_df = trains_df[trains_df["order_id"].isin(relevant_order_ids)].copy()

    print(f"Relevant prior interactions: {len(priors_df):,}, Train interactions: {len(trains_df):,}")

    product_to_idx = catalog_mappings["product_to_idx"]
    catalog_df = catalog_mappings["catalog_df"].set_index("product_id")

    # Map product IDs to internal item_idx
    priors_df["item_idx"] = priors_df["product_id"].map(product_to_idx)
    priors_df.dropna(subset=["item_idx"], inplace=True)
    priors_df["item_idx"] = priors_df["item_idx"].astype(int)

    trains_df["item_idx"] = trains_df["product_id"].map(product_to_idx)
    trains_df.dropna(subset=["item_idx"], inplace=True)
    trains_df["item_idx"] = trains_df["item_idx"].astype(int)

    num_depts = catalog_mappings["num_departments"]

    # Calculate item statistics
    print("[4/5] Computing user profiles, depletion metrics, and item statistics...")
    item_stats = priors_df.groupby("item_idx").agg(
        total_purchases=("reordered", "count"),
        reorder_count=("reordered", "sum"),
        avg_add_to_cart=("add_to_cart_order", "mean")
    )
    item_stats["reorder_rate"] = item_stats["reorder_count"] / item_stats["total_purchases"].clip(lower=1)
    item_stats["log_purchases"] = np.log1p(item_stats["total_purchases"])

    # Aggregate by user:
    # 1. Department affinity vector (21-dim)
    # 2. Average days between orders
    # 3. User-Item purchase counts & inter-purchase intervals
    user_dept_counts = defaultdict(lambda: np.zeros(num_depts, dtype=np.float32))
    user_order_days = defaultdict(list)
    user_item_orders = defaultdict(lambda: defaultdict(list))  # user_id -> item_idx -> list of order_numbers
    user_last_order_num = {}

    # Track order timeline per user
    user_orders_grouped = user_orders.groupby("user_id")
    user_cadence = {}
    for uid, group in user_orders_grouped:
        prior_group = group[group["eval_set"] == "prior"]
        days = prior_group["days_since_prior_order"].dropna().values
        avg_days = float(np.mean(days)) if len(days) > 0 else 10.0
        total_orders = len(prior_group)
        user_cadence[uid] = {
            "avg_days_between_orders": avg_days,
            "total_orders": total_orders,
        }

    # Group prior order products by order
    order_groups = priors_df.groupby("order_id")

    # Co-occurrence dictionary for cart complements: item_a -> item_b -> count
    co_occurrence = defaultdict(lambda: defaultdict(int))

    training_interactions = []
    
    for order_id, group in tqdm(order_groups, desc="Processing prior baskets"):
        meta = order_meta.get(order_id)
        if not meta:
            continue
        uid = meta["user_id"]
        u_idx = user_to_idx[uid]
        order_num = meta["order_number"]
        dow = meta["order_dow"]
        hour = meta["order_hour_of_day"]

        items_in_order = group["item_idx"].values
        reorders = group["reordered"].values

        # Track user-item interactions
        for it_idx, reordered in zip(items_in_order, reorders):
            user_item_orders[uid][it_idx].append(order_num)
            training_interactions.append((u_idx, it_idx, dow, hour, int(reordered)))

            # Dept affinity
            pid = catalog_mappings["idx_to_product"][it_idx]
            d_idx = catalog_df.loc[pid, "dept_idx"]
            user_dept_counts[uid][d_idx] += 1

        # Co-occurrence for basket complementarity (sample pairs to keep memory bounded)
        if len(items_in_order) > 1 and len(items_in_order) <= 30:
            for i in range(len(items_in_order)):
                for j in range(i + 1, min(i + 6, len(items_in_order))):
                    it1, it2 = items_in_order[i], items_in_order[j]
                    co_occurrence[it1][it2] += 1
                    co_occurrence[it2][it1] += 1

    # Normalize user department preferences to probability distribution
    user_dept_affinity = {}
    for uid in selected_users_set:
        counts = user_dept_counts[uid]
        total = np.sum(counts)
        if total > 0:
            user_dept_affinity[uid] = counts / total
        else:
            user_dept_affinity[uid] = np.ones(num_depts, dtype=np.float32) / num_depts

    # Compute User-Item repeat consumption cadence (Depletion Engine)
    user_item_depletion = defaultdict(dict)
    for uid, items in user_item_orders.items():
        cadence = user_cadence.get(uid, {"avg_days_between_orders": 10.0, "total_orders": 10})
        total_u_orders = cadence["total_orders"]
        avg_order_interval = cadence["avg_days_between_orders"]

        for it_idx, order_nums in items.items():
            purchase_count = len(order_nums)
            last_order_bought = max(order_nums)
            orders_since_last = max(0, total_u_orders - last_order_bought)
            days_since_last_bought = orders_since_last * avg_order_interval

            if len(order_nums) > 1:
                # Interval between purchases in terms of orders
                intervals = np.diff(sorted(order_nums))
                avg_interval_orders = float(np.mean(intervals))
            else:
                # If bought once, estimate interval from total orders
                avg_interval_orders = max(2.0, float(total_u_orders) / 2.0)

            avg_cycle_days = max(2.0, avg_interval_orders * avg_order_interval)
            depletion_ratio = float(days_since_last_bought / avg_cycle_days)

            user_item_depletion[uid][it_idx] = {
                "purchase_count": purchase_count,
                "days_since_last_bought": round(days_since_last_bought, 1),
                "avg_cycle_days": round(avg_cycle_days, 1),
                "depletion_ratio": round(depletion_ratio, 2),
                "is_depleted": bool(depletion_ratio >= 0.85),
            }

    # Ground-truth validation baskets (using train orders of selected users)
    print("[5/5] Building validation test baskets and saving processed datasets...")
    val_baskets = {}
    train_orders_selected = user_orders[user_orders["eval_set"] == "train"]
    train_order_to_user = train_orders_selected.set_index("order_id")["user_id"].to_dict()

    train_groups = trains_df.groupby("order_id")
    for order_id, group in train_groups:
        uid = train_order_to_user.get(order_id)
        if uid and uid in user_to_idx:
            u_idx = user_to_idx[uid]
            val_baskets[u_idx] = {
                "user_id": uid,
                "target_items": list(group["item_idx"].values),
                "reordered_items": list(group[group["reordered"] == 1]["item_idx"].values),
            }

    # If some users didn't have a 'train' eval_set, use their last prior order for evaluation
    users_without_train = set(user_to_idx.keys()) - {v["user_id"] for v in val_baskets.values()}
    print(f"Users with official train orders: {len(val_baskets)}. Backfilling {len(users_without_train)} from last prior order.")

    for uid in users_without_train:
        u_orders = user_orders[(user_orders["user_id"] == uid) & (user_orders["eval_set"] == "prior")]
        if len(u_orders) >= 2:
            last_order_id = u_orders.iloc[-1]["order_id"]
            items = priors_df[priors_df["order_id"] == last_order_id]
            if len(items) > 0:
                u_idx = user_to_idx[uid]
                val_baskets[u_idx] = {
                    "user_id": uid,
                    "target_items": list(items["item_idx"].values),
                    "reordered_items": list(items[items["reordered"] == 1]["item_idx"].values),
                }

    # Format training dataframe
    train_df = pd.DataFrame(
        training_interactions,
        columns=["user_idx", "item_idx", "order_dow", "order_hour", "reordered"],
    )

    # Top co-occurrences (keep top 20 complements per product to keep size tiny)
    pruned_co_occurrence = {}
    for it1, paired in co_occurrence.items():
        top_pairs = sorted(paired.items(), key=lambda x: x[1], reverse=True)[:20]
        pruned_co_occurrence[it1] = dict(top_pairs)

    # Save outputs
    with open(processed_dir / "user_mappings.pkl", "wb") as f:
        pickle.dump({"user_to_idx": user_to_idx, "idx_to_user": idx_to_user}, f)

    with open(processed_dir / "user_profiles.pkl", "wb") as f:
        pickle.dump(
            {
                "user_dept_affinity": user_dept_affinity,
                "user_cadence": user_cadence,
                "user_item_depletion": dict(user_item_depletion),
            },
            f,
        )

    with open(processed_dir / "item_stats.pkl", "wb") as f:
        pickle.dump(item_stats.to_dict(orient="index"), f)

    with open(processed_dir / "val_baskets.pkl", "wb") as f:
        pickle.dump(val_baskets, f)

    with open(processed_dir / "co_occurrence.pkl", "wb") as f:
        pickle.dump(pruned_co_occurrence, f)

    train_df.to_parquet(processed_dir / "train_interactions.parquet", index=False)

    print(f"\n[SUCCESS] Preprocessing completed!")
    print(f"Total training interactions: {len(train_df):,}")
    print(f"Total validation users: {len(val_baskets):,}")
    print(f"Processed files saved in: {processed_dir}")


def main():
    parser = argparse.ArgumentParser(description="Preprocess Instacart Data")
    parser.add_argument("--max-users", type=int, default=5000, help="Number of active users to sample")
    parser.add_argument("--min-orders", type=int, default=4, help="Minimum prior orders per user")
    args = parser.parse_args()

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    catalog_mappings = build_catalog(RAW_DATA_DIR, PROCESSED_DATA_DIR)
    process_features(
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        catalog_mappings,
        max_users=args.max_users,
        min_user_orders=args.min_orders,
    )


if __name__ == "__main__":
    main()
