"""
Dashboard page — overview stats, top products, model metrics, quick actions.
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
    # Offset content for fixed sidebar
    st.markdown("<style>section.main > div {padding-top:0!important;margin-left:240px;}</style>", unsafe_allow_html=True)

    render_sidebar("dashboard")

    name = st.session_state.get("user_name", "User")
    pipeline = load_pipeline()
    personas = pipeline.get_sample_personas()
    catalog_df = pipeline.catalog_df

    st.markdown("<div class='sb-dash-main'>", unsafe_allow_html=True)

    # ── Header ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sb-dash-header">
        <h1>Good afternoon, {name.split()[0]} 👋</h1>
        <p>Here's an overview of your SmartBasket AI system — real-time, neural, personalized.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Stats Row ──────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("49,688",   "Catalog Products",      "+0 new today",     "#dcfce7", "#16a34a"),
        ("3,000",    "Active Customer Profiles", "across all personas", "#dbeafe", "#3b82f6"),
        ("< 150ms",  "Avg Recommendation Latency", "Two-Tower CPU retrieval", "#fef3c7", "#f59e0b"),
        ("5",        "Shopper Personas Detected", "auto-clustered by AI",   "#ede9fe", "#7c3aed"),
    ]
    for col, (val, label, sub, bg, color) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(f"""
            <div class="sb-card" style="border-top:3px solid {color};">
                <div style="font-size:1.9rem;font-weight:800;color:{color};margin-bottom:4px;">{val}</div>
                <div style="font-size:0.88rem;font-weight:700;color:#0f172a;margin-bottom:3px;">{label}</div>
                <div style="font-size:0.75rem;color:#64748b;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── Main Grid: Personas | Model Metrics ───────────────────────────
    col_personas, col_metrics = st.columns([1.2, 1], gap="large")

    with col_personas:
        st.markdown("<div class='sb-section-title'>👤 Shopper Personas Detected</div>", unsafe_allow_html=True)
        st.markdown("<div class='sb-section-sub'>AI-clustered customer archetypes from purchase history</div>", unsafe_allow_html=True)

        for i, persona in enumerate(personas):
            dept = persona["top_department"].title()
            share = persona["top_dept_share"]
            orders = persona["total_orders"]
            cadence = persona["cadence_days"]
            uid = persona["user_id"]

            # color per persona
            colors = ["#16a34a", "#3b82f6", "#f59e0b", "#7c3aed", "#ef4444"]
            color = colors[i % len(colors)]
            initials = dept[:2].upper()

            st.markdown(f"""
            <div class="sb-card" style="margin-bottom:12px;padding:18px 22px;cursor:pointer;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:44px;height:44px;background:{color};border-radius:12px;
                         display:flex;align-items:center;justify-content:center;
                         color:#fff;font-weight:800;font-size:0.9rem;flex-shrink:0;">
                        {initials}
                    </div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:700;color:#0f172a;font-size:0.9rem;">{persona['persona_name']}</div>
                        <div style="font-size:0.75rem;color:#64748b;margin-top:2px;">
                            {orders} orders · every {cadence}d · {share} {dept}
                        </div>
                    </div>
                    <span class="badge badge-primary">{dept}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🛒 Open Smart Shopper →", use_container_width=True, type="primary"):
            nav_goto("shop")

    with col_metrics:
        st.markdown("<div class='sb-section-title'>📊 Model Benchmark Metrics</div>", unsafe_allow_html=True)
        st.markdown("<div class='sb-section-sub'>Evaluated on 2,067 held-out customer validation baskets</div>", unsafe_allow_html=True)

        eval_file = MODEL_DIR / "evaluation_metrics.json"
        if eval_file.exists():
            with open(eval_file) as f:
                metrics = json.load(f)

            metric_items = [
                ("HitRate@10", f"{metrics.get('HitRate@10', 0)*100:.2f}%", "Items retrieved in top 10", "#dcfce7", "#16a34a"),
                ("HitRate@20", f"{metrics.get('HitRate@20', 0)*100:.2f}%", "Items retrieved in top 20", "#dbeafe", "#3b82f6"),
                ("NDCG@10",    f"{metrics.get('NDCG@10', 0):.4f}",         "Ranking quality metric",    "#fef3c7", "#f59e0b"),
                ("MRR",        f"{metrics.get('MRR', 0):.4f}",             "Mean Reciprocal Rank",      "#ede9fe", "#7c3aed"),
            ]
            for label, val, sub, bg, color in metric_items:
                st.markdown(f"""
                <div style="background:{bg};border-radius:12px;padding:16px 20px;margin-bottom:10px;
                     display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <div style="font-weight:700;color:#0f172a;font-size:0.88rem;">{label}</div>
                        <div style="font-size:0.75rem;color:#64748b;margin-top:2px;">{sub}</div>
                    </div>
                    <div style="font-size:1.5rem;font-weight:800;color:{color};">{val}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="sb-card" style="margin-top:4px;">
                <div style="font-size:0.78rem;color:#64748b;">
                    <b>Eval users:</b> {metrics.get('NumEvalUsers', 0):,} &nbsp;·&nbsp;
                    <b>Recall@10:</b> {metrics.get('Recall@10', 0):.4f} &nbsp;·&nbsp;
                    <b>Recall@20:</b> {metrics.get('Recall@20', 0):.4f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No evaluation metrics found. Run `train_two_tower.py` to generate them.")

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── Bottom Row: Top Depts + Quick Dept Search ──────────────────────
    col_dept, col_quick = st.columns([1, 1], gap="large")

    with col_dept:
        st.markdown("<div class='sb-section-title'>🏪 Top Departments in Catalog</div>", unsafe_allow_html=True)
        dept_counts = catalog_df.groupby("department")["product_id"].count().sort_values(ascending=False).head(8)
        total = dept_counts.sum()
        dept_colors = ["#16a34a","#3b82f6","#f59e0b","#7c3aed","#ef4444","#0891b2","#db2777","#ea580c"]
        for i, (dept, cnt) in enumerate(dept_counts.items()):
            pct = cnt / total * 100
            color = dept_colors[i % len(dept_colors)]
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:0.82rem;font-weight:600;color:#0f172a;">{dept.title()}</span>
                    <span style="font-size:0.78rem;color:#64748b;">{cnt:,} products ({pct:.1f}%)</span>
                </div>
                <div class="dep-bar-track">
                    <div class="dep-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_quick:
        st.markdown("<div class='sb-section-title'>⚡ Quick Actions</div>", unsafe_allow_html=True)

        qa_items = [
            ("🛒", "Open Live Cart Simulator", "Add items and watch AI recommendations adapt in real-time.", "shop"),
            ("📈", "View Analytics Report", "Deep-dive into category diversity, latency, and ranking analysis.", "analytics"),
        ]
        for icon, title, desc, target in qa_items:
            with st.container():
                st.markdown(f"""
                <div class="sb-card" style="margin-bottom:14px;">
                    <div style="display:flex;gap:16px;align-items:flex-start;">
                        <div style="font-size:1.8rem;">{icon}</div>
                        <div>
                            <div style="font-weight:700;color:#0f172a;font-size:0.9rem;margin-bottom:4px;">{title}</div>
                            <div style="font-size:0.78rem;color:#64748b;">{desc}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open →", key=f"qa_{target}", use_container_width=True):
                    nav_goto(target)

        st.markdown("""
        <div class="sb-card" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#bbf7d0;">
            <div style="font-size:0.8rem;font-weight:700;color:#15803d;margin-bottom:6px;">🧠 Model Info</div>
            <div style="font-size:0.78rem;color:#166534;line-height:1.65;">
                Trained on <b>57,915 interactions</b> · 6 epochs ·
                In-batch InfoNCE contrastive loss (τ=0.07) ·
                Multi-task reorder classification head
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
