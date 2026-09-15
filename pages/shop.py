"""
Smart Shopper page — interactive cart simulator with live Two-Tower recommendations.
"""

import streamlit as st
from pages.components import inject_css, nav_goto
from pages.sidebar import render_sidebar


@st.cache_resource(show_spinner=False)
def load_pipeline():
    from src.pipeline import GroceryRecommenderPipeline
    return GroceryRecommenderPipeline()


DOW_MAP = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
URGENCY_BADGE = {
    "Overdue":  "badge-red",
    "Due Soon": "badge-amber",
    "Regular":  "badge-blue",
}


def render():
    inject_css()
    st.markdown("<style>section.main > div {padding-top:0!important;margin-left:240px;}</style>", unsafe_allow_html=True)
    render_sidebar("shop")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    pipeline = load_pipeline()
    personas = pipeline.get_sample_personas()

    st.markdown("<div class='sb-dash-main'>", unsafe_allow_html=True)

    # ── Page Header ────────────────────────────────────────────────────
    st.markdown("""
    <div class="sb-dash-header">
        <h1>🛒 Smart Shopper Simulator</h1>
        <p>Pick a customer persona, add items to the basket, and watch AI recommendations adapt in real-time.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Persona & Context Controls ─────────────────────────────────────
    ctrl1, ctrl2, ctrl3 = st.columns([2.5, 1.2, 1.2])

    with ctrl1:
        persona_names = [p["persona_name"] for p in personas]
        chosen_name = st.selectbox("👤 Active Shopper Persona", persona_names, key="persona_select")
        persona = next(p for p in personas if p["persona_name"] == chosen_name)
        user_id = persona["user_id"]

    with ctrl2:
        trip_dow = st.selectbox("📅 Day of Week", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], index=5)

    with ctrl3:
        trip_hour = st.slider("🕐 Trip Hour", 7, 22, 14)

    # Persona chip info
    st.markdown(f"""
    <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:12px 20px;margin-bottom:24px;display:flex;gap:24px;align-items:center;">
        <span style="font-size:1.4rem;">🧑‍🛒</span>
        <div>
            <b style="color:#15803d;">{persona['persona_name']}</b>
            <span style="color:#64748b;font-size:0.8rem;margin-left:12px;">
                &nbsp;Top category: <b>{persona['top_department'].title()}</b> ({persona['top_dept_share']}) &nbsp;·&nbsp;
                {persona['total_orders']} lifetime orders &nbsp;·&nbsp; shops every {persona['cadence_days']} days
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Smart Replenish Bar ────────────────────────────────────────────
    st.markdown("<div class='sb-section-title'>⚡ Smart Replenish — Depletion Alerts</div>", unsafe_allow_html=True)
    replenishments = pipeline.get_smart_replenishments(user_id, top_n=4)

    if replenishments:
        rep_cols = st.columns(len(replenishments))
        for col, item in zip(rep_cols, replenishments):
            urgency = item["urgency_label"]
            badge_cls = URGENCY_BADGE.get(urgency, "badge-slate")
            dep_ratio = min(item["depletion_ratio"], 1.5)
            bar_pct = min(dep_ratio / 1.5 * 100, 100)
            bar_color = "#ef4444" if urgency == "Overdue" else "#f59e0b" if urgency == "Due Soon" else "#3b82f6"
            name_truncated = item['product_name'][:32] + ("…" if len(item['product_name']) > 32 else "")
            with col:
                st.markdown(f"""
                <div class="sb-card" style="padding:18px;">
                    <span class="badge {badge_cls}">{urgency}</span>
                    <div style="font-weight:700;color:#0f172a;font-size:0.85rem;margin:8px 0 2px;">{name_truncated}</div>
                    <div style="font-size:0.72rem;color:#64748b;">{item['aisle'].title()}</div>
                    <div class="dep-bar-track" style="margin:10px 0 4px;">
                        <div class="dep-bar-fill" style="width:{bar_pct:.0f}%;background:{bar_color};"></div>
                    </div>
                    <div style="font-size:0.7rem;color:#64748b;">
                        Last: <b>{item['days_since_last_bought']:.0f}d ago</b> · Cycle: <b>{item['avg_cycle_days']:.0f}d</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("+ Add", key=f"rep_{item['product_id']}_{user_id}", use_container_width=True):
                    if not any(c.get("product_id") == item["product_id"] for c in st.session_state.cart):
                        st.session_state.cart.append(item)
                        st.rerun()
    else:
        st.info("No depletion alerts detected for this persona.")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Two-Column: Cart | Recommendations ────────────────────────────
    cart_col, rec_col = st.columns([1, 1.5], gap="large")

    with cart_col:
        st.markdown("<div class='sb-section-title'>🛒 Active Basket</div>", unsafe_allow_html=True)
        cart = st.session_state.cart

        if cart:
            for idx, item in enumerate(cart):
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"""
                    <div style="padding:10px 0;border-bottom:1px solid #e2e8f0;">
                        <div style="font-weight:600;font-size:0.85rem;color:#0f172a;">{item.get('product_name','?')}</div>
                        <div style="font-size:0.72rem;color:#64748b;margin-top:2px;">
                            {str(item.get('department','')).title()} · {str(item.get('aisle','')).title()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    if st.button("✕", key=f"rm_{idx}_{item.get('product_id')}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Clear Cart", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
        else:
            st.markdown("""
            <div style="background:#f8fafc;border:2px dashed #e2e8f0;border-radius:14px;
                 padding:40px;text-align:center;color:#94a3b8;">
                <div style="font-size:2.5rem;margin-bottom:12px;">🛒</div>
                <div style="font-size:0.875rem;font-weight:600;">Your basket is empty</div>
                <div style="font-size:0.78rem;margin-top:6px;">Add items from Replenish or search the catalog below.</div>
            </div>
            """, unsafe_allow_html=True)

        # Catalog mini search
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sb-section-title'>🔍 Search Catalog</div>", unsafe_allow_html=True)
        query = st.text_input("Product name", placeholder="e.g. Avocado, Pasta, Milk…", label_visibility="collapsed")
        if query and len(query) >= 2:
            matches = pipeline.catalog_df[
                pipeline.catalog_df["product_name"].str.contains(query, case=False, na=False)
            ].head(5)
            for _, row in matches.iterrows():
                sa, sb = st.columns([4, 1])
                with sa:
                    st.markdown(f"""
                    <div style="font-size:0.82rem;font-weight:600;color:#0f172a;">{row['product_name']}</div>
                    <div style="font-size:0.72rem;color:#64748b;">{row['department'].title()} · {row['aisle'].title()}</div>
                    """, unsafe_allow_html=True)
                with sb:
                    if st.button("＋", key=f"search_add_{row['product_id']}"):
                        item_dict = row.to_dict()
                        if not any(c.get("product_id") == item_dict["product_id"] for c in st.session_state.cart):
                            st.session_state.cart.append(item_dict)
                            st.rerun()

    # ── Recommendations Column ─────────────────────────────────────────
    with rec_col:
        cart_pids = [c.get("product_id") for c in st.session_state.cart if c.get("product_id")]
        result = pipeline.recommend(
            user_id=user_id,
            cart_product_ids=cart_pids,
            top_n=8,
            dow=DOW_MAP[trip_dow],
            hour=trip_hour,
        )
        metrics = result["metrics"]

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
            <div class="sb-section-title" style="margin:0;">🎯 AI Recommendations</div>
            <div style="font-size:0.75rem;color:#64748b;">
                ⚡ {metrics['total_latency_ms']:.1f}ms total &nbsp;·&nbsp;
                {metrics['candidates_evaluated']} candidates evaluated
            </div>
        </div>
        """, unsafe_allow_html=True)

        for rec in result["recommendations"]:
            score_pct = min(int(rec["final_score"] * 400), 100)
            ra, rb = st.columns([5, 1])
            with ra:
                st.markdown(f"""
                <div class="rec-row">
                    <div>
                        <div class="rec-row-name">{rec['product_name']}</div>
                        <div class="rec-row-meta">{rec['department'].title()} · {rec['aisle'].title()}</div>
                        <div class="rec-row-reason">
                            <span class="badge badge-green">{rec['explanation']}</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size:0.7rem;color:#64748b;text-align:right;margin-bottom:4px;">Match</div>
                        <span class="rec-score-pill">{score_pct}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with rb:
                if st.button("➕", key=f"rec_add_{rec['product_id']}_{user_id}"):
                    if not any(c.get("product_id") == rec["product_id"] for c in st.session_state.cart):
                        st.session_state.cart.append(rec)
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
