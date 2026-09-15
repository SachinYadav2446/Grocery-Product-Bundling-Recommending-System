"""
Analytics page — department coverage, model benchmark, architecture deep-dive.
"""

import json
import streamlit as st
from pages.components import inject_css, nav_goto
from pages.sidebar import render_sidebar
from src.config import MODEL_DIR


@st.cache_resource(show_spinner=False)
def load_pipeline():
    from src.pipeline import GroceryRecommenderPipeline
    return GroceryRecommenderPipeline()


def render():
    inject_css()
    st.markdown("<style>section.main > div {padding-top:0!important;margin-left:240px;}</style>", unsafe_allow_html=True)
    render_sidebar("analytics")

    pipeline = load_pipeline()
    catalog_df = pipeline.catalog_df

    st.markdown("<div class='sb-dash-main'>", unsafe_allow_html=True)

    # ── Header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sb-dash-header">
        <h1>📈 Analytics & Model Diagnostics</h1>
        <p>Deep-dive into catalog structure, model benchmark metrics, and AI architecture details.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Catalog Analytics", "🤖 Model Benchmark", "🏗️ Architecture"])

    # ── Tab 1: Catalog Analytics ───────────────────────────────────────
    with tab1:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Summary stats
        a1, a2, a3, a4 = st.columns(4)
        for col, val, label in [
            (a1, f"{catalog_df['product_id'].nunique():,}", "Total Products"),
            (a2, f"{catalog_df['aisle_id'].nunique()}", "Unique Aisles"),
            (a3, f"{catalog_df['department_id'].nunique()}", "Departments"),
            (a4, f"{catalog_df['product_name'].notna().sum():,}", "Named Products"),
        ]:
            with col:
                st.markdown(f"""
                <div class="sb-stat">
                    <div class="sb-stat-value">{val}</div>
                    <div class="sb-stat-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        # Department breakdown
        left_a, right_a = st.columns([1.2, 1], gap="large")

        with left_a:
            st.markdown("<div class='sb-section-title'>Products by Department</div>", unsafe_allow_html=True)
            dept_counts = catalog_df.groupby("department")["product_id"].count().sort_values(ascending=False)
            total = dept_counts.sum()
            colors = ["#16a34a","#3b82f6","#f59e0b","#7c3aed","#ef4444","#0891b2",
                      "#db2777","#ea580c","#65a30d","#0d9488","#6366f1"]
            for i, (dept, cnt) in enumerate(dept_counts.items()):
                pct = cnt / total * 100
                c = colors[i % len(colors)]
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="font-size:0.82rem;font-weight:600;color:#0f172a;">{dept.title()}</span>
                        <span style="font-size:0.78rem;color:#64748b;">{cnt:,} ({pct:.1f}%)</span>
                    </div>
                    <div class="dep-bar-track">
                        <div class="dep-bar-fill" style="width:{pct:.1f}%;background:{c};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with right_a:
            st.markdown("<div class='sb-section-title'>Aisle Distribution (Top 10)</div>", unsafe_allow_html=True)
            aisle_counts = catalog_df.groupby("aisle")["product_id"].count().sort_values(ascending=False).head(10)
            for i, (aisle, cnt) in enumerate(aisle_counts.items()):
                c = colors[i % len(colors)]
                st.markdown(f"""
                <div style="background:#f8fafc;border-radius:10px;padding:12px 16px;margin-bottom:8px;
                     display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:10px;height:10px;border-radius:50%;background:{c};flex-shrink:0;"></div>
                        <span style="font-size:0.82rem;font-weight:500;color:#0f172a;">{aisle.title()}</span>
                    </div>
                    <span class="badge badge-slate">{cnt} products</span>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 2: Model Benchmark ─────────────────────────────────────────
    with tab2:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        eval_file = MODEL_DIR / "evaluation_metrics.json"

        if eval_file.exists():
            with open(eval_file) as f:
                m = json.load(f)

            # Metric cards
            mc1, mc2, mc3, mc4 = st.columns(4)
            mcard_data = [
                (mc1, "HitRate@10", f"{m.get('HitRate@10',0)*100:.2f}%", "Fraction of users who had at least 1 correct item in top 10", "#dcfce7", "#16a34a"),
                (mc2, "HitRate@20", f"{m.get('HitRate@20',0)*100:.2f}%", "Fraction of users who had at least 1 correct item in top 20", "#dbeafe", "#3b82f6"),
                (mc3, "NDCG@10",   f"{m.get('NDCG@10',0):.4f}",          "Normalized Discounted Cumulative Gain at 10", "#fef3c7", "#f59e0b"),
                (mc4, "MRR",       f"{m.get('MRR',0):.4f}",              "Mean Reciprocal Rank across all users", "#ede9fe", "#7c3aed"),
            ]
            for col, label, val, desc, bg, color in mcard_data:
                with col:
                    st.markdown(f"""
                    <div class="sb-card" style="border-top:3px solid {color};text-align:center;">
                        <div style="font-size:1.8rem;font-weight:800;color:{color};">{val}</div>
                        <div style="font-weight:700;font-size:0.85rem;color:#0f172a;margin:6px 0 4px;">{label}</div>
                        <div style="font-size:0.72rem;color:#64748b;line-height:1.5;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

            # Training configuration
            b_left, b_right = st.columns(2, gap="large")
            with b_left:
                st.markdown("<div class='sb-section-title'>Training Configuration</div>", unsafe_allow_html=True)
                config_rows = [
                    ("Model", "Hybrid Two-Tower Neural Network"),
                    ("User Tower", "User Embedding + Dept Affinity (21-dim) + Cadence + DOW + Hour"),
                    ("Item Tower", "Item + Aisle + Department Embeddings + Popularity Stats"),
                    ("Embedding Dim", "64 dimensions"),
                    ("Training Loss", "In-batch InfoNCE Contrastive (τ=0.07) + Binary Reorder CE"),
                    ("Optimizer", "AdamW (lr=0.001, weight_decay=1e-4)"),
                    ("LR Scheduler", "Cosine Annealing"),
                    ("Epochs", "6"),
                    ("Batch Size", "512"),
                    ("Interactions", "57,915 prior purchase pairs"),
                    ("Eval Users", f"{m.get('NumEvalUsers',0):,} held-out validation baskets"),
                ]
                for k, v in config_rows:
                    st.markdown(f"""
                    <div style="display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #f1f5f9;">
                        <div style="font-size:0.78rem;font-weight:700;color:#64748b;min-width:130px;">{k}</div>
                        <div style="font-size:0.78rem;color:#0f172a;">{v}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with b_right:
                st.markdown("<div class='sb-section-title'>Inference Pipeline Latency</div>", unsafe_allow_html=True)
                latency_items = [
                    ("Stage 1: Two-Tower Retrieval", "~150ms", "49,688-item cosine dot-product on CPU", "#fef3c7", "#f59e0b"),
                    ("Stage 2: Contextual Re-Ranker", "< 1ms",  "Cart affinity + depletion scoring", "#dcfce7", "#16a34a"),
                    ("Stage 3: Business Guardrails", "< 0.5ms", "Diversity + deduplication + explainability", "#dbeafe", "#3b82f6"),
                    ("Total End-to-End", "~150ms", "Sub-200ms on CPU, sub-20ms on GPU", "#ede9fe", "#7c3aed"),
                ]
                for label, latency, desc, bg, color in latency_items:
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:12px;padding:16px;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <div style="font-weight:700;font-size:0.85rem;color:#0f172a;">{label}</div>
                            <div style="font-weight:800;font-size:1.1rem;color:{color};">{latency}</div>
                        </div>
                        <div style="font-size:0.75rem;color:#64748b;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No benchmark data found. Please run `python -m src.models.train_two_tower` first.")

    # ── Tab 3: Architecture ────────────────────────────────────────────
    with tab3:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sb-section-title'>3-Stage Recommendation Funnel</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.85rem;color:#475569;line-height:1.8;max-width:800px;margin-bottom:28px;">
        SmartBasket AI replaces legacy Apriori/FP-Growth association rules with an enterprise-grade neural
        recommendation funnel used by Instacart, Walmart, and Ocado.
        </div>
        """, unsafe_allow_html=True)

        stages = [
            ("01", "#dcfce7", "#16a34a", "Candidate Retrieval — Hybrid Two-Tower Neural Network",
             [
                 "User Tower: User Embedding + 21-dim Department Affinity Profile + Order Cadence + Temporal Context (DOW, hour cyclic encoding)",
                 "Item Tower: Item Embedding + Aisle Embedding + Department Embedding + Global Popularity + Reorder Rate",
                 "In-batch InfoNCE Contrastive Loss (temperature τ=0.07) with auxiliary multi-task repeat-purchase head",
                 "Precomputed 64-dim item embeddings for all 49,688 catalog items → cosine dot-product retrieval in < 150ms",
             ]),
            ("02", "#dbeafe", "#3b82f6", "Contextual Basket Re-Ranker",
             [
                 "Live Cart Complementarity: Log-weighted PMI co-occurrence score for all cart × candidate item pairs",
                 "Depletion Urgency: Depletion Ratio = Days Since Last Purchase / Personalized Repurchase Cycle → boosts overdue staples",
                 "Substitute Suppression: Penalizes candidates from the same aisle when a similar item is already in the cart",
                 "Composite Score = 0.45 × Two-Tower + 0.30 × Cart Affinity + 0.25 × Depletion Boost − Substitute Penalty",
             ]),
            ("03", "#fef3c7", "#f59e0b", "Business Guardrails & Explainability",
             [
                 "Aisle Diversity Constraint: Maximum 2 products allowed per grocery aisle (prevents 8 types of bread)",
                 "Explainability Engine: Generates natural language reason badges (e.g. 'Pairs with Organic Bananas', 'Refill Due in 2 days')",
                 "Depletion urgency labels: Overdue / Due Soon / Regular based on depletion ratio thresholds",
                 "Final ranking merged from Two-Tower + Re-Ranker, then diversity-filtered to produce final Top-N",
             ]),
        ]

        for num, bg, color, title, points in stages:
            st.markdown(f"""
            <div class="sb-card" style="margin-bottom:20px;border-left:4px solid {color};">
                <div style="display:flex;gap:16px;align-items:flex-start;">
                    <div style="font-size:2rem;font-weight:900;color:{bg};min-width:48px;line-height:1;">{num}</div>
                    <div style="flex:1;">
                        <div style="font-weight:700;font-size:1rem;color:#0f172a;margin-bottom:12px;">{title}</div>
                        <div style="display:flex;flex-direction:column;gap:7px;">
                            {''.join(f'<div style="font-size:0.8rem;color:#475569;padding-left:14px;border-left:2px solid {color};">• {p}</div>' for p in points)}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sb-card" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#bbf7d0;">
            <div style="font-weight:700;color:#15803d;font-size:0.9rem;margin-bottom:8px;">📐 Mathematical Foundation</div>
            <div style="font-size:0.8rem;color:#166534;line-height:1.8;">
                <b>Two-Tower Retrieval:</b> cos(u, v) = (U·V) / (|U||V|) — both towers produce L2-normalized vectors on the unit sphere, enabling efficient dot-product lookup.<br>
                <b>InfoNCE Loss:</b> ℒ = −Σ log exp(uᵢᵀvᵢ / τ) / Σⱼ exp(uᵢᵀvⱼ / τ) — in-batch negative sampling with 511 negatives per positive at batch size 512.<br>
                <b>Depletion Ratio:</b> δ = Δt / T̄ᵤᵢ where Δt = days since last purchase and T̄ᵤᵢ = average inter-purchase interval for user u × item i.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
