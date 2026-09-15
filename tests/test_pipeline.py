"""
Automated unit tests for Supermarket Recommender Pipeline and Models.
"""

import unittest
import torch
from src.models.two_tower import HybridTwoTowerModel
from src.pipeline import GroceryRecommenderPipeline


class TestTwoTowerModel(unittest.TestCase):
    def setUp(self):
        self.model = HybridTwoTowerModel(
            num_users=100,
            num_items=500,
            num_aisles=50,
            num_depts=21,
            embedding_dim=64,
        )

    def test_forward_pass_and_loss(self):
        batch_size = 8
        user_inputs = {
            "user_idx": torch.randint(0, 100, (batch_size,)),
            "dept_affinity": torch.rand(batch_size, 21),
            "cadence_features": torch.rand(batch_size, 2),
            "dow": torch.randint(0, 7, (batch_size,)),
            "hour": torch.randint(0, 24, (batch_size,)),
        }
        item_inputs = {
            "item_idx": torch.randint(0, 500, (batch_size,)),
            "aisle_idx": torch.randint(0, 50, (batch_size,)),
            "dept_idx": torch.randint(0, 21, (batch_size,)),
            "item_features": torch.rand(batch_size, 3),
        }
        reordered = torch.randint(0, 2, (batch_size,))

        total_loss, loss_dict = self.model(user_inputs, item_inputs, reordered=reordered)
        self.assertGreater(total_loss.item(), 0.0)
        self.assertIn("retrieval_loss", loss_dict)
        self.assertIn("reorder_loss", loss_dict)


class TestRecommenderPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = GroceryRecommenderPipeline()
        cls.personas = cls.pipeline.get_sample_personas()

    def test_personas_available(self):
        self.assertGreater(len(self.personas), 0)

    def test_recommend_empty_cart(self):
        user_id = self.personas[0]["user_id"]
        res = self.pipeline.recommend(user_id=user_id, cart_product_ids=[], top_n=5)
        self.assertEqual(len(res["recommendations"]), 5)
        self.assertIn("total_latency_ms", res["metrics"])
        for rec in res["recommendations"]:
            self.assertIn("product_name", rec)
            self.assertIn("explanation", rec)

    def test_recommend_with_cart_items(self):
        user_id = self.personas[0]["user_id"]
        # Recommend with cart item
        first_recs = self.pipeline.recommend(user_id=user_id, cart_product_ids=[], top_n=3)
        cart_product = first_recs["recommendations"][0]["product_id"]

        cart_recs = self.pipeline.recommend(user_id=user_id, cart_product_ids=[cart_product], top_n=5)
        # Verify cart item itself is not recommended
        rec_ids = [r["product_id"] for r in cart_recs["recommendations"]]
        self.assertNotIn(cart_product, rec_ids)

    def test_smart_replenishments(self):
        user_id = self.personas[0]["user_id"]
        replenishments = self.pipeline.get_smart_replenishments(user_id, top_n=4)
        self.assertIsInstance(replenishments, list)
        for item in replenishments:
            self.assertIn("depletion_ratio", item)
            self.assertIn("urgency_label", item)


if __name__ == "__main__":
    unittest.main()
