"""
Landing page — public-facing hero + features + CTA.
"""

import streamlit as st
from pages.components import inject_css, nav_goto


def render():
    inject_css()

    # ── Top Navbar ────────────────────────────────────────────────────
    st.markdown("""
    <div class="sb-navbar">
        <div class="sb-navbar-logo">🛒 Smart<span>Basket</span> AI</div>
        <div class="sb-navbar-links">
            <span class="sb-nav-pill">Features</span>
            <span class="sb-nav-pill">How It Works</span>
            <span class="sb-nav-pill">About</span>
        </div>
    </div>
    <div style="height:64px"></div>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sb-hero">
        <div class="sb-hero-tag">⚡ Powered by Two-Tower Neural AI</div>
        <h1 class="sb-hero-title">
            Supermarket Intelligence<br>
            That Actually <em>Knows</em> Your Customers
        </h1>
        <p class="sb-hero-sub">
            Move beyond outdated Apriori rules. SmartBasket AI delivers hyper-personalized
            grocery recommendations — in real-time — using the same deep learning architecture
            trusted by Instacart, Walmart, and Ocado.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # CTA Buttons — centered using 3 columns
    pad_l, btn_area, pad_r = st.columns([3, 3, 3])
    with btn_area:
        if st.button("🚀  Get Started — It's Free", use_container_width=True, type="primary"):
            nav_goto("signup")
        if st.button("🔐  Sign In", use_container_width=True):
            nav_goto("login")

    # ── Stats Bar ─────────────────────────────────────────────────────
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, val, label in [
        (sc1, "49,688", "Catalog Products"),
        (sc2, "3 M+", "Order Interactions"),
        (sc3, "<150ms", "Inference Latency"),
        (sc4, "3-Stage", "AI Recommendation Funnel"),
    ]:
        with col:
            st.markdown(f"""
            <div class="sb-stat">
                <div class="sb-stat-value">{val}</div>
                <div class="sb-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Features ──────────────────────────────────────────────────────
    st.markdown("<div style='height:64px'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;font-size:1.9rem;font-weight:800;color:#0f172a;margin-bottom:8px;'>Why SmartBasket AI?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#475569;font-size:0.95rem;margin-bottom:40px;'>Three reasons enterprises replace Apriori with us.</p>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="large")
    features = [
        ("🧠", "#dcfce7", "Hybrid Two-Tower Neural Net",
         "Learns separate dense representations for every customer and product. Real-time cosine similarity retrieves the top 100 candidates across 49,688 items in under 150ms."),
        ("🔄", "#dbeafe", "Depletion & Repurchase Engine",
         "Tracks each customer's buying cadence per product. Surfaces refill alerts exactly when staples like milk, eggs, or coffee are predicted to run out."),
        ("🛒", "#fef3c7", "Contextual Live Cart Re-Ranker",
         "As customers add items, our ranker dynamically boosts complementary products (pasta → sauce → parmesan) using basket co-occurrence graphs, in under 1ms."),
    ]
    for col, (icon, bg, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="sb-card">
                <div class="sb-feature-icon" style="background:{bg}">{icon}</div>
                <div class="sb-feature-title">{title}</div>
                <div class="sb-feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────────────────
    st.markdown("<div style='height:72px'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;font-size:1.9rem;font-weight:800;color:#0f172a;margin-bottom:40px;'>3-Stage Recommendation Funnel</h2>", unsafe_allow_html=True)

    h1, h2, h3 = st.columns(3, gap="large")
    stages = [
        ("01", "Candidate Retrieval", "Two-Tower neural network maps users & items to a shared 64-dim semantic space. Dot-product similarity retrieves the most relevant 100 candidates instantly."),
        ("02", "Contextual Re-Ranking", "A real-time ranker blends Two-Tower similarity with live cart affinity, personalized depletion urgency, and temporal signals like day-of-week."),
        ("03", "Business Guardrails", "Category diversity enforcement, substitute suppression, and an explainability engine that generates natural-language reasons for every recommendation."),
    ]
    for col, (num, title, desc) in zip([h1, h2, h3], stages):
        with col:
            st.markdown(f"""
            <div class="sb-card">
                <div style="font-size:2.5rem;font-weight:900;color:#dcfce7;line-height:1;margin-bottom:10px;">{num}</div>
                <div class="sb-feature-title">{title}</div>
                <div class="sb-feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Footer CTA ────────────────────────────────────────────────────
    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:linear-gradient(135deg,#14532d,#16a34a);border-radius:20px;padding:60px 40px;text-align:center;margin-bottom:60px;">
        <h2 style="color:#fff;font-size:2rem;font-weight:800;margin-bottom:12px;">Ready to transform your supermarket?</h2>
        <p style="color:rgba(255,255,255,.8);font-size:0.95rem;margin-bottom:32px;">Start your free account and run live recommendations in minutes.</p>
    </div>
    """, unsafe_allow_html=True)
    ca, cb, cc = st.columns([4, 2, 4])
    with cb:
        if st.button("🚀 Create Free Account", use_container_width=True, type="primary"):
            nav_goto("signup")

    st.markdown("<p style='text-align:center;color:#94a3b8;font-size:0.78rem;padding:20px;'>© 2026 SmartBasket AI · Built on Instacart Market Basket Analysis Dataset</p>", unsafe_allow_html=True)
