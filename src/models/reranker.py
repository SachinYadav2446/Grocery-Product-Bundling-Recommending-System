"""
Contextual Basket Re-Ranker for Supermarket Recommendation.
Scores candidate products retrieved by the Two-Tower model using:
- Real-time cart complementarity (co-purchase strength with items currently in the basket)
- Depletion urgency (days since prior purchase relative to personalized repurchase cycle)
- Historical user-item affinity and reorder propensity
- Anti-cannibalization / substitute suppression
"""

import math
from typing import List, Dict, Any


class ContextualBasketReRanker:
    def __init__(
        self,
        co_occurrence: Dict[int, Dict[int, int]],
        item_stats: Dict[int, Dict[str, float]],
        catalog_dict: Dict[int, Dict[str, Any]],
    ):
        self.co_occurrence = co_occurrence
        self.item_stats = item_stats
        self.catalog_dict = catalog_dict

    def score_candidate(
        self,
        item_idx: int,
        two_tower_score: float,
        cart_item_indices: List[int],
        user_item_history: Dict[int, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Computes composite ranking score and explainability factors for a candidate product.
        """
        # 1. Base Retrieval Score (Normalized cosine similarity from Two-Tower)
        base_score = float(two_tower_score)

        # 2. Live Cart Complementarity
        cart_affinity = 0.0
        complement_pair = None
        max_pair_weight = 0

        if cart_item_indices:
            paired_dict = self.co_occurrence.get(item_idx, {})
            for cart_item in cart_item_indices:
                if cart_item == item_idx:
                    continue  # Already in cart
                co_count = paired_dict.get(cart_item, 0)
                if co_count > 0:
                    cart_affinity += math.log1p(co_count)
                    if co_count > max_pair_weight:
                        max_pair_weight = co_count
                        complement_pair = cart_item

        # 3. Depletion / Repurchase Cycle Urgency
        item_history = user_item_history.get(item_idx)
        depletion_boost = 0.0
        repurchase_reason = None

        if item_history:
            depletion_ratio = item_history.get("depletion_ratio", 0.0)
            purchase_count = item_history.get("purchase_count", 0)
            days_since = item_history.get("days_since_last_bought", 0)
            avg_cycle = item_history.get("avg_cycle_days", 7)

            if depletion_ratio >= 1.0:
                # Due or overdue for replenishment
                depletion_boost = 0.35 * min(depletion_ratio, 2.0)
                repurchase_reason = f"Due for refill (bought {days_since:.0f}d ago; cycle: {avg_cycle:.0f}d)"
            elif depletion_ratio >= 0.75:
                depletion_boost = 0.20
                repurchase_reason = f"Replenish soon (bought {days_since:.0f}d ago)"
            else:
                depletion_boost = 0.05 * min(purchase_count, 5)
                repurchase_reason = f"Frequently bought ({purchase_count}x)"

        # 4. Substitute Suppression (Anti-cannibalization)
        # If cart already contains a product in the same aisle, apply slight penalty unless complementary
        item_meta = self.catalog_dict.get(item_idx, {})
        aisle_id = item_meta.get("aisle_id")
        cart_aisles = [self.catalog_dict.get(c, {}).get("aisle_id") for c in cart_item_indices]

        substitute_penalty = 0.0
        if aisle_id in cart_aisles and cart_affinity < 0.1:
            # Similar item already in cart with low co-purchase correlation
            substitute_penalty = 0.25

        # 5. Composite Final Score
        # Blend Two-Tower semantic similarity + Cart Affinity + Depletion Urgency - Penalty
        final_score = (
            0.45 * base_score
            + 0.30 * (cart_affinity / (1.0 + cart_affinity))
            + 0.25 * depletion_boost
            - substitute_penalty
        )

        # Build Explainability Note
        reasons = []
        if complement_pair is not None:
            paired_meta = self.catalog_dict.get(complement_pair, {})
            reasons.append(f"Pairs with {paired_meta.get('product_name', 'item in cart')}")
        if repurchase_reason:
            reasons.append(repurchase_reason)
        if not reasons:
            reasons.append("Matches your shopping taste profile")

        return {
            "item_idx": item_idx,
            "final_score": float(final_score),
            "two_tower_score": float(two_tower_score),
            "cart_affinity": float(cart_affinity),
            "depletion_boost": float(depletion_boost),
            "substitute_penalty": float(substitute_penalty),
            "explanation": " • ".join(reasons),
        }

    def rerank(
        self,
        candidates: List[tuple[int, float]],
        cart_item_indices: List[int],
        user_item_history: Dict[int, Dict[str, Any]],
        top_n: int = 10,
        max_per_aisle: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Re-ranks top candidates and applies aisle diversity constraints.
        """
        cart_set = set(cart_item_indices)
        scored_candidates = []

        for item_idx, tt_score in candidates:
            if item_idx in cart_set:
                continue  # Don't recommend what's already in the cart

            scored = self.score_candidate(
                item_idx=item_idx,
                two_tower_score=tt_score,
                cart_item_indices=cart_item_indices,
                user_item_history=user_item_history,
            )
            scored_candidates.append(scored)

        # Sort by final score descending
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)

        # Apply category diversity constraint (e.g. max 2 items per aisle)
        diverse_recommendations = []
        aisle_counts = {}

        for cand in scored_candidates:
            it_idx = cand["item_idx"]
            aisle_id = self.catalog_dict.get(it_idx, {}).get("aisle_id", "default")

            count = aisle_counts.get(aisle_id, 0)
            if count < max_per_aisle:
                aisle_counts[aisle_id] = count + 1
                diverse_recommendations.append(cand)
                if len(diverse_recommendations) >= top_n:
                    break

        # If diversity constraint left us with fewer than top_n, fill with next best
        if len(diverse_recommendations) < top_n:
            for cand in scored_candidates:
                if cand not in diverse_recommendations:
                    diverse_recommendations.append(cand)
                    if len(diverse_recommendations) >= top_n:
                        break

        return diverse_recommendations
