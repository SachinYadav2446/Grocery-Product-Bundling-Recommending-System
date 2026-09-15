"""
PyTorch Hybrid Two-Tower Neural Network for Supermarket Grocery Recommendation.
Features:
- User Tower: User identity + Department affinity profile + Shopping cadence + Temporal context
- Item Tower: Item identity + Hierarchical category embeddings (Aisle & Department) + Global purchase dynamics
- In-batch negative InfoNCE contrastive retrieval loss with temperature scaling
- Auxiliary multi-task replenishment head (reorder prediction)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class UserTower(nn.Module):
    """
    Encodes customer profile and contextual shopping trip intent into a dense vector.
    """
    def __init__(
        self,
        num_users: int,
        num_depts: int = 21,
        user_dim: int = 64,
        dow_dim: int = 8,
        output_dim: int = 64,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.user_embedding = nn.Embedding(num_users, user_dim)
        self.dow_embedding = nn.Embedding(7, dow_dim)

        # Input dimensions:
        # user_dim (64) + num_depts (21) + cadence (2) + dow_dim (8) + hour_sin_cos (2) = 97
        input_dim = user_dim + num_depts + 2 + dow_dim + 2

        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Dropout(dropout),
            nn.Linear(128, output_dim),
        )

    def forward(
        self,
        user_idx: torch.Tensor,
        dept_affinity: torch.Tensor,
        cadence_features: torch.Tensor,
        dow: torch.Tensor,
        hour: torch.Tensor,
    ) -> torch.Tensor:
        u_emb = self.user_embedding(user_idx)
        dow_emb = self.dow_embedding(dow)

        # Cyclical hour encoding: sin & cos
        hour_rad = hour.float() * (2.0 * math.pi / 24.0)
        hour_sin = torch.sin(hour_rad).unsqueeze(-1)
        hour_cos = torch.cos(hour_rad).unsqueeze(-1)

        x = torch.cat([u_emb, dept_affinity, cadence_features, dow_emb, hour_sin, hour_cos], dim=-1)
        user_vector = self.mlp(x)
        # Normalize to unit sphere for cosine similarity retrieval
        return F.normalize(user_vector, p=2, dim=-1)


class ItemTower(nn.Module):
    """
    Encodes product catalog hierarchy and global purchase dynamics into a dense vector.
    """
    def __init__(
        self,
        num_items: int,
        num_aisles: int,
        num_depts: int,
        item_dim: int = 64,
        aisle_dim: int = 32,
        dept_dim: int = 16,
        output_dim: int = 64,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.item_embedding = nn.Embedding(num_items, item_dim)
        self.aisle_embedding = nn.Embedding(num_aisles, aisle_dim)
        self.dept_embedding = nn.Embedding(num_depts, dept_dim)

        # item_dim (64) + aisle_dim (32) + dept_dim (16) + item_features (3) = 115
        input_dim = item_dim + aisle_dim + dept_dim + 3

        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.LayerNorm(128),
            nn.Dropout(dropout),
            nn.Linear(128, output_dim),
        )

    def forward(
        self,
        item_idx: torch.Tensor,
        aisle_idx: torch.Tensor,
        dept_idx: torch.Tensor,
        item_features: torch.Tensor,
    ) -> torch.Tensor:
        it_emb = self.item_embedding(item_idx)
        ai_emb = self.aisle_embedding(aisle_idx)
        dp_emb = self.dept_embedding(dept_idx)

        x = torch.cat([it_emb, ai_emb, dp_emb, item_features], dim=-1)
        item_vector = self.mlp(x)
        # Normalize to unit sphere for cosine similarity retrieval
        return F.normalize(item_vector, p=2, dim=-1)


class HybridTwoTowerModel(nn.Module):
    """
    Two-Tower Recommendation Model with in-batch contrastive loss and
    auxiliary repeat-purchase classification head.
    """
    def __init__(
        self,
        num_users: int,
        num_items: int,
        num_aisles: int,
        num_depts: int,
        embedding_dim: int = 64,
        temperature: float = 0.07,
    ):
        super().__init__()
        self.temperature = temperature
        self.user_tower = UserTower(
            num_users=num_users,
            num_depts=num_depts,
            user_dim=embedding_dim,
            output_dim=embedding_dim,
        )
        self.item_tower = ItemTower(
            num_items=num_items,
            num_aisles=num_aisles,
            num_depts=num_depts,
            item_dim=embedding_dim,
            output_dim=embedding_dim,
        )

        # Auxiliary replenishment head to predict if interaction is a repeat purchase
        self.reorder_head = nn.Sequential(
            nn.Linear(embedding_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(
        self,
        user_inputs: dict,
        item_inputs: dict,
        reordered: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, dict]:
        user_vecs = self.user_tower(
            user_idx=user_inputs["user_idx"],
            dept_affinity=user_inputs["dept_affinity"],
            cadence_features=user_inputs["cadence_features"],
            dow=user_inputs["dow"],
            hour=user_inputs["hour"],
        )

        item_vecs = self.item_tower(
            item_idx=item_inputs["item_idx"],
            aisle_idx=item_inputs["aisle_idx"],
            dept_idx=item_inputs["dept_idx"],
            item_features=item_inputs["item_features"],
        )

        # In-batch Cosine Similarity Matrix: (Batch_size, Batch_size)
        sim_matrix = torch.matmul(user_vecs, item_vecs.T) / self.temperature

        batch_size = user_vecs.size(0)
        labels = torch.arange(batch_size, device=user_vecs.device)
        retrieval_loss = F.cross_entropy(sim_matrix, labels)

        losses = {"retrieval_loss": retrieval_loss}
        total_loss = retrieval_loss

        if reordered is not None:
            # Pairwise elementwise interaction for reorder propensity
            interaction = user_vecs * item_vecs
            reorder_logits = self.reorder_head(interaction).squeeze(-1)
            reorder_loss = F.binary_cross_entropy_with_logits(reorder_logits, reordered.float())
            losses["reorder_loss"] = reorder_loss
            total_loss = retrieval_loss + 0.5 * reorder_loss

        losses["total_loss"] = total_loss
        return total_loss, losses

    def get_user_embedding(self, user_inputs: dict) -> torch.Tensor:
        return self.user_tower(
            user_idx=user_inputs["user_idx"],
            dept_affinity=user_inputs["dept_affinity"],
            cadence_features=user_inputs["cadence_features"],
            dow=user_inputs["dow"],
            hour=user_inputs["hour"],
        )

    def get_item_embedding(self, item_inputs: dict) -> torch.Tensor:
        return self.item_tower(
            item_idx=item_inputs["item_idx"],
            aisle_idx=item_inputs["aisle_idx"],
            dept_idx=item_inputs["dept_idx"],
            item_features=item_inputs["item_features"],
        )
