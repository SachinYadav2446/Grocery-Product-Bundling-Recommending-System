# SmartBasket AI: Modern Supermarket Recommender Engine

> **Moving beyond legacy Apriori / FP-Growth:** A production-grade grocery recommendation system utilizing the **Instacart Market Basket Analysis** dataset and a **Hybrid Two-Tower Neural Network** with a **Contextual Basket Re-Ranker** and an interactive web simulator.

---

## 🚀 Why Not Apriori?

Traditional market basket analysis projects rely on Apriori or FP-Growth association rules. In real-world supermarket retail (Instacart, Walmart, Ocado, Target), these fail because:
1. **No User Personalization**: Everyone who buys pasta gets recommended pasta sauce, completely ignoring dietary profiles (organic vs budget vs vegan).
2. **Ignores Temporal Repurchase Cycles**: Groceries are consumable commodities. A customer buys milk every 4 days and olive oil every 45 days. Apriori treats baskets as static snapshots without time awareness.
3. **High Cardinality & Scalability**: Association rule mining explodes combinatorially when scaled across 50,000+ catalog items.

---

## 🏗️ System Architecture

Our solution deploys an enterprise-grade 3-stage recommendation funnel:

```
┌────────────────────────────────────────────────────────────────────────┐
│               Instacart Retail Dataset (49,688 Products)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Candidate Retrieval (Hybrid Two-Tower Neural Network)        │
│ • User Tower: Learns dense vector from user identity, 21-dim dept     │
│   affinity, order cadence, day-of-week, and trip hour.                 │
│ • Item Tower: Learns dense vector from item identity, aisle embedding, │
│   department embedding, and global purchase/reorder dynamics.          │
│ • Dot-Product Cosine Retrieval: Filters 49,688 items -> Top 100 in    │
│   < 150 ms using PyTorch vectorized similarity.                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                           Top 100 Candidates
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Contextual Basket Re-Ranker                                   │
│ • Live Cart Complementarity: Co-purchase affinity scores with items   │
│   currently in the basket.                                             │
│ • Depletion / Repurchase Urgency: Calculates:                          │
│     Depletion Ratio = (Days Since Last Order) / (Item Cycle Days)      │
│   Boosts items that the customer has run out of.                       │
│ • Substitute Suppression: Prevents redundant item recommendations.     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                              Top 20 Scored
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Business Logic & Guardrails                                   │
│ • Category Diversity: Enforces a maximum of 2 items per aisle.         │
│ • Explainability Engine: Generates real-time reasoning badges:          │
│   "Due for refill (bought 14d ago; cycle 7d)"                          │
│   "Pairs with Organic Bananas"                                         │
│   "Matches your Produce taste profile"                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Interactive Supermarket Simulator (Streamlit Web App)                  │
│ • Customer Persona Switcher (Produce Lover, Dairy Enthusiast, etc.)    │
│ • "Smart Replenish" predictive shelf with countdown indicators        │
│ • Live interactive shopping cart with dynamic real-time recommendations│
│ • Full architectural and latency diagnostics                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
grocery_recommander/
├── app.py                      # Interactive Streamlit Web Application
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── src/
│   ├── config.py               # Hyperparameters, paths, and settings
│   ├── data/
│   │   ├── download.py         # Automated streaming downloader for Instacart data
│   │   └── preprocess.py       # Feature engineering, depletion ratios, test baskets
│   ├── models/
│   │   ├── two_tower.py        # PyTorch User Tower, Item Tower, and InfoNCE loss
│   │   ├── train_two_tower.py  # Model training & validation benchmark evaluation
│   │   └── reranker.py         # Contextual basket re-ranker & diversity engine
│   └── pipeline.py             # Unified inference pipeline
└── tests/
    └── test_pipeline.py        # Automated unit test suite
```

---

## ⚡ Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Instacart Dataset
Download catalog files and a rich benchmark subset from Hugging Face:
```bash
python -m src.data.download
```
*(Optional: Use `--full` if you want to download the entire uncompressed 550MB dataset).*

### 3. Run Preprocessing & Feature Engineering
Extracts user shopping cadence, department affinity vectors, depletion ratios, and basket co-occurrences:
```bash
python -m src.data.preprocess --max-users 3000 --min-orders 4
```

### 4. Train the Hybrid Two-Tower Model
Trains the User and Item towers with in-batch InfoNCE contrastive loss and precomputes item embeddings:
```bash
python -m src.models.train_two_tower --epochs 6 --batch-size 512
```

### 5. Run Automated Unit Tests
```bash
python -m unittest discover tests
```

### 6. Launch the Interactive Web App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Evaluation & Validation Metrics

Evaluated on held-out customer baskets (`order_products__train.csv`):

| Metric | Score | Description |
| :--- | :--- | :--- |
| **HitRate@10** | **1.89%** | Ground-truth basket item retrieved in Top 10 |
| **HitRate@20** | **2.85%** | Ground-truth basket item retrieved in Top 20 |
| **MRR** | **0.0094** | Mean Reciprocal Rank across 49,688 products |
| **Retrieval Latency** | **~150 ms** | Two-Tower cosine similarity search on CPU |
| **Re-Ranking Latency** | **< 1 ms** | Real-time basket context scoring |

---

## 💡 Key Features of the Interactive App

1. **Shopper Persona Switcher**: Switch between customer profiles (e.g. *Produce Lover*, *Dairy Enthusiast*) and observe how recommendations dynamically specialize to their shopping habits.
2. **Smart Replenish Shelf**: Automatically flags items that the customer has run out of based on their replenishment cadence (e.g. *Overdue*, *Due Soon*).
3. **Live Shopping Basket**: Add items into the cart and watch the recommender instantly adapt to complementary products (e.g. adding pasta promotes pasta sauces and parmesan).
4. **Transparent Explainability**: Every recommendation discloses *why* it was selected (e.g. *Pairs with X*, *Due for refill*, *Matches taste profile*).
