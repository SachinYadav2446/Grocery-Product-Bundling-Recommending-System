"""
Unified Production Inference Engine for Supermarket Grocery Recommendation.
Integrates:
1. Stage 1: Fast Two-Tower Retrieval across 49,000+ catalog products
2. Stage 2: Contextual Basket Re-Ranker with live cart complementarity
3. Stage 3: Business Logic (Aisle Diversity & Substitute Suppression)
4. Explainability & Shopper Persona management
"""

import math
import pickle
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import torch

from src.config import PROCESSED_DATA_DIR, MODEL_DIR, TOP_K_CANDIDATES, FINAL_RECOMMENDATIONS_COUNT
from src.models.two_tower import HybridTwoTowerModel
from src.models.reranker import ContextualBasketReRanker


class GroceryRecommenderPipeline:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.load_artifacts()

    def load_artifacts(self):
        """Loads catalog, user profiles, models, and precomputed embeddings."""
        # 1. Catalog mappings
        with open(PROCESSED_DATA_DIR / "catalog.pkl", "rb") as f:
            self.catalog_mappings = pickle.load(f)
        self.catalog_df = self.catalog_mappings["catalog_df"]
        self.catalog_dict = self.catalog_mappings["catalog_dict"]
        self.product_to_idx = self.catalog_mappings["product_to_idx"]
        self.idx_to_product = self.catalog_mappings["idx_to_product"]

        # 2. User mappings and profiles
        with open(PROCESSED_DATA_DIR / "user_mappings.pkl", "rb") as f:
            self.user_mappings = pickle.load(f)
        self.user_to_idx = self.user_mappings["user_to_idx"]
        self.idx_to_user = self.user_mappings["idx_to_user"]

        with open(PROCESSED_DATA_DIR / "user_profiles.pkl", "rb") as f:
            self.user_profiles = pickle.load(f)
        self.user_dept_affinity = self.user_profiles["user_dept_affinity"]
        self.user_cadence = self.user_profiles["user_cadence"]
        self.user_item_depletion = self.user_profiles["user_item_depletion"]

        # 3. Item stats & Co-occurrences
        with open(PROCESSED_DATA_DIR / "item_stats.pkl", "rb") as f:
            self.item_stats = pickle.load(f)

        with open(PROCESSED_DATA_DIR / "co_occurrence.pkl", "rb") as f:
            self.co_occurrence = pickle.load(f)

        # 4. Neural Model & Precomputed Item Embeddings
        self.item_embeddings = torch.load(MODEL_DIR / "item_embeddings.pt", map_location=self.device)
        
        self.model = HybridTwoTowerModel(
            num_users=len(self.user_to_idx),
            num_items=self.catalog_mappings["num_items"],
            num_aisles=self.catalog_mappings["num_aisles"],
            num_depts=self.catalog_mappings["num_departments"],
        ).to(self.device)

        weights = torch.load(MODEL_DIR / "two_tower_weights.pt", map_location=self.device)
        self.model.load_state_dict(weights)
        self.model.eval()

        # 5. Contextual Re-Ranker
        self.reranker = ContextualBasketReRanker(
            co_occurrence=self.co_occurrence,
            item_stats=self.item_stats,
            catalog_dict=self.catalog_dict,
        )

        self.default_affinity = np.ones(self.catalog_mappings["num_departments"], dtype=np.float32) / self.catalog_mappings["num_departments"]

    def get_user_vector(self, user_id: int, dow: int = 2, hour: int = 14) -> torch.Tensor:
        """Encodes user identity, preferences, and context into a 64-dim vector."""
        u_idx = self.user_to_idx.get(user_id, 0)
        aff = self.user_dept_affinity.get(user_id, self.default_affinity)
        cad = self.user_cadence.get(user_id, {"total_orders": 10, "avg_days_between_orders": 10.0})
        cad_feat = [math.log1p(cad["total_orders"]), min(cad["avg_days_between_orders"], 30.0) / 30.0]

        user_inputs = {
            "user_idx": torch.tensor([u_idx], dtype=torch.long, device=self.device),
            "dept_affinity": torch.tensor(np.array([aff]), dtype=torch.float32, device=self.device),
            "cadence_features": torch.tensor(np.array([cad_feat]), dtype=torch.float32, device=self.device),
            "dow": torch.tensor([dow], dtype=torch.long, device=self.device),
            "hour": torch.tensor([hour], dtype=torch.long, device=self.device),
        }

        with torch.no_grad():
            u_emb = self.model.get_user_embedding(user_inputs)
        return u_emb

    def retrieve_candidates(self, user_id: int, top_k: int = TOP_K_CANDIDATES, dow: int = 2, hour: int = 14) -> List[tuple[int, float]]:
        """Stage 1: Fast vector similarity retrieval against entire product catalog."""
        u_emb = self.get_user_vector(user_id, dow=dow, hour=hour)  # (1, D)
        scores = torch.matmul(u_emb, self.item_embeddings.T).squeeze(0)  # (num_items)
        top_scores, top_indices = torch.topk(scores, k=top_k)

        candidates = [
            (int(idx), float(score))
            for idx, score in zip(top_indices.cpu().numpy(), top_scores.cpu().numpy())
        ]
        return candidates

    def get_smart_replenishments(self, user_id: int, top_n: int = 6) -> List[Dict[str, Any]]:
        """
        Predicts items the customer is running out of based on their replenishment cadence.
        """
        depletion_dict = self.user_item_depletion.get(user_id, {})
        if not depletion_dict:
            return []

        # Sort by depletion_ratio descending
        sorted_items = sorted(
            depletion_dict.items(),
            key=lambda x: (x[1]["depletion_ratio"], x[1]["purchase_count"]),
            reverse=True,
        )

        replenishments = []
        for it_idx, metrics in sorted_items[:top_n]:
            meta = self.catalog_dict.get(it_idx, {})
            replenishments.append({
                "item_idx": it_idx,
                "product_id": meta.get("product_id"),
                "product_name": meta.get("product_name"),
                "aisle": meta.get("aisle"),
                "department": meta.get("department"),
                "purchase_count": metrics["purchase_count"],
                "days_since_last_bought": metrics["days_since_last_bought"],
                "avg_cycle_days": metrics["avg_cycle_days"],
                "depletion_ratio": metrics["depletion_ratio"],
                "is_depleted": metrics["is_depleted"],
                "urgency_label": "Overdue" if metrics["depletion_ratio"] >= 1.0 else "Due Soon" if metrics["depletion_ratio"] >= 0.75 else "Regular",
            })

        return replenishments

    def recommend(
        self,
        user_id: int,
        cart_product_ids: Optional[List[int]] = None,
        top_n: int = FINAL_RECOMMENDATIONS_COUNT,
        dow: int = 2,
        hour: int = 14,
        include_replenishment_blend: bool = True,
    ) -> Dict[str, Any]:
        """
        Full End-to-End Recommendation pipeline:
        1. Retrieval (Two-Tower)
        2. Re-Ranking (Cart Context + Depletion + Substitute suppression)
        3. Explainability generation
        """
        start_time = time.perf_counter()

        cart_product_ids = cart_product_ids or []
        cart_item_indices = [
            self.product_to_idx[pid]
            for pid in cart_product_ids
            if pid in self.product_to_idx
        ]

        # 1. Retrieval
        retrieval_start = time.perf_counter()
        candidates = self.retrieve_candidates(user_id, top_k=TOP_K_CANDIDATES, dow=dow, hour=hour)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        # Inject high-urgency replenishment candidates if available
        user_history = self.user_item_depletion.get(user_id, {})
        if include_replenishment_blend and user_history:
            cand_indices = {c[0] for c in candidates}
            for it_idx, hist in user_history.items():
                if hist.get("depletion_ratio", 0) >= 0.9 and it_idx not in cand_indices:
                    # Give it a baseline similarity score so ranker can evaluate it
                    candidates.append((it_idx, 0.40))

        # 2. Re-Ranking
        rerank_start = time.perf_counter()
        ranked_results = self.reranker.rerank(
            candidates=candidates,
            cart_item_indices=cart_item_indices,
            user_item_history=user_history,
            top_n=top_n,
        )
        rerank_ms = (time.perf_counter() - rerank_start) * 1000

        # 3. Enrich with metadata
        recommendations = []
        for r in ranked_results:
            it_idx = r["item_idx"]
            meta = self.catalog_dict.get(it_idx, {})
            recommendations.append({
                "product_id": meta.get("product_id"),
                "product_name": meta.get("product_name"),
                "aisle": meta.get("aisle"),
                "department": meta.get("department"),
                "final_score": round(r["final_score"], 3),
                "two_tower_score": round(r["two_tower_score"], 3),
                "cart_affinity": round(r["cart_affinity"], 3),
                "explanation": r["explanation"],
            })

        total_ms = (time.perf_counter() - start_time) * 1000

        return {
            "user_id": user_id,
            "cart_count": len(cart_product_ids),
            "recommendations": recommendations,
            "metrics": {
                "retrieval_latency_ms": round(retrieval_ms, 2),
                "rerank_latency_ms": round(rerank_ms, 2),
                "total_latency_ms": round(total_ms, 2),
                "candidates_evaluated": len(candidates),
            },
        }

    def get_sample_personas(self) -> List[Dict[str, Any]]:
        """Identifies distinct customer shopping personas for interactive demonstration."""
        personas = []
        user_ids = list(self.user_to_idx.keys())
        
        # Scan users to find distinct behavioral archetypes
        for uid in user_ids[:50]:
            aff = self.user_dept_affinity.get(uid)
            if aff is None:
                continue
            cad = self.user_cadence.get(uid, {})
            # Department indices: produce (typically idx 19), dairy (typically idx 16), snacks (idx 19/etc)
            # Find dominant department
            top_dept_idx = int(np.argmax(aff))
            top_dept_share = float(aff[top_dept_idx])

            # Look up department name
            sample_product = self.catalog_df[self.catalog_df["dept_idx"] == top_dept_idx].iloc[0]
            top_dept_name = sample_product["department"]

            if top_dept_share >= 0.30 and len(personas) < 5:
                personas.append({
                    "user_id": uid,
                    "persona_name": f"{top_dept_name.title()} Lover (User #{uid})",
                    "top_department": top_dept_name,
                    "top_dept_share": f"{int(top_dept_share * 100)}%",
                    "total_orders": cad.get("total_orders", 10),
                    "cadence_days": round(cad.get("avg_days_between_orders", 10), 1),
                })

        if not personas:
            # Fallback
            personas = [
                {"user_id": user_ids[0], "persona_name": f"Regular Shopper (#{user_ids[0]})", "top_department": "produce", "top_dept_share": "30%", "total_orders": 12, "cadence_days": 7.0}
            ]
        return personas
