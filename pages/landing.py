"""
SmartBasket AI - High-End Animated Landing Page
Color Palette:
- #689D4B (Primary Rich Leaf Green)
- #91AE6E (Secondary Sage Olive Green)
- #D96868 (Coral Warm Rose Accent)
- #F2F2F2 (Neutral Off-White Background)
"""

import streamlit as st
from pages.components import inject_css, nav_goto


def render():
    inject_css()

    # ── 1. Classy Floating Header ─────────────────────────────────────
    st.markdown("""
    <div class="sb-header">
        <div class="sb-header-brand">
            <div class="sb-brand-icon">🛒</div>
            <div>Smart<span style="color:var(--primary);">Basket</span></div>
            <span class="sb-brand-tag">AI v2.4</span>
        </div>
        <div class="sb-header-nav">
            <span class="sb-status-pill">
                <span class="sb-pulse-dot"></span>
                Two-Tower Model Active
            </span>
        </div>
    </div>
    <div style="height:48px;"></div>
    """, unsafe_allow_html=True)

    # ── 2. Animated Hero Section ──────────────────────────────────────
    st.markdown("""
    <div class="sb-hero-wrap">
        <div style="display:flex; flex-direction:column; align-items:center; text-align:center;">
            <div class="sb-badge-pill">
                <span>⚡ Next-Generation Retail Recommendation</span>
                <span style="color:var(--coral);font-weight:800;">•</span>
                <span style="color:var(--text-2);">Instacart Benchmark</span>
            </div>
            <h1 class="sb-hero-h1">
                The Neural Engine for<br>
                <span class="highlight-green">Next-Basket</span> Supermarket Intelligence
            </h1>
            <p class="sb-hero-desc">
                Traditional Apriori rules treat all customers the same. SmartBasket AI uses a 
                <b>Hybrid Two-Tower Neural Network</b> and <b>Depletion Cadence Modeling</b> 
                to predict the exact products customers need before they even search.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Primary Action Buttons (Centered & Responsive)
    pad_l, btn1, btn2, pad_r = st.columns([3.2, 1.8, 1.8, 3.2])
    with btn1:
        if st.button("🚀  Launch System", use_container_width=True, type="primary"):
            nav_goto("signup")
    with btn2:
        if st.button("🔐  Sign In", use_container_width=True):
            nav_goto("login")

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # ── Interactive Live Simulation Card (Floating Preview) ───────────
    preview_l, preview_mid, preview_r = st.columns([1, 6, 1])
    with preview_mid:
        st.markdown("""
        <div class="sb-hero-card">
            <div class="sb-sim-header">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:var(--primary);box-shadow:0 0 10px var(--primary);"></div>
                    <span style="font-weight:800;font-size:0.88rem;color:var(--text-1);letter-spacing:0.02em;">REAL-TIME NEURAL BASKET SIMULATION</span>
                </div>
                <div class="sb-sim-chip">
                    <span>Shopper DNA: Organic Produce Enthusiast</span>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <!-- Left: Active Basket -->
                <div style="background:#FFFFFF; border:1px solid var(--border); border-radius:14px; padding:16px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                        <span style="font-size:0.8rem;font-weight:700;color:var(--text-2);text-transform:uppercase;">Currently In Basket</span>
                        <span class="badge badge-green">2 Items</span>
                    </div>
                    
                    <div class="sb-item-row">
                        <div>
                            <div style="font-weight:700;font-size:0.85rem;color:var(--text-1);">Organic Hass Avocado</div>
                            <div style="font-size:0.72rem;color:var(--text-3);">Produce • Fresh Fruits</div>
                        </div>
                        <span style="font-size:0.75rem;font-weight:700;color:var(--primary);">Added ✓</span>
                    </div>

                    <div class="sb-item-row">
                        <div>
                            <div style="font-weight:700;font-size:0.85rem;color:var(--text-1);">Artisan Sourdough Loaf</div>
                            <div style="font-size:0.72rem;color:var(--text-3);">Bakery • Fresh Breads</div>
                        </div>
                        <span style="font-size:0.75rem;font-weight:700;color:var(--primary);">Added ✓</span>
                    </div>
                </div>

                <!-- Right: Real-time Neural Recommendations -->
                <div style="background:#FFFFFF; border:1px solid var(--border); border-radius:14px; padding:16px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
                        <span style="font-size:0.8rem;font-weight:700;color:var(--primary-dark);text-transform:uppercase;">Two-Tower Dynamic Recs</span>
                        <span style="font-size:0.72rem;font-weight:700;color:var(--text-3);">Latency: 142ms</span>
                    </div>

                    <!-- Recommended Item 1: Complementary -->
                    <div class="sb-rec-glow-row" style="margin-top:0;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div>
                                <div style="font-weight:800;font-size:0.88rem;color:var(--text-1);">Organic Extra Virgin Olive Oil</div>
                                <div style="font-size:0.72rem;color:var(--text-2);margin-top:2px;">Pantry • Oils & Vinegars</div>
                            </div>
                            <span class="badge badge-green" style="background:#689D4B;color:#FFFFFF;">96.4% Match</span>
                        </div>
                        <div style="margin-top:6px;font-size:0.72rem;color:var(--primary-dark);font-weight:600;">
                            ✨ Pairs with Sourdough & Avocado (Cart Co-occurrence)
                        </div>
                    </div>

                    <!-- Recommended Item 2: Depletion Urgency -->
                    <div style="background:#FFF9F9; border:1.5px solid var(--coral); border-radius:12px; padding:12px;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                            <div>
                                <div style="font-weight:800;font-size:0.88rem;color:var(--text-1);">Organic Whole Milk</div>
                                <div style="font-size:0.72rem;color:var(--text-2);margin-top:2px;">Dairy Eggs • Milk</div>
                            </div>
                            <span class="badge badge-coral">Depleted (Due Now)</span>
                        </div>
                        <div style="margin-top:6px;font-size:0.72rem;color:var(--coral-dark);font-weight:600;">
                            ⏱️ Cadence: Bought 7 days ago (User Cycle: 6.2 days)
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:70px;'></div>", unsafe_allow_html=True)

    # ── 3. Metrics Strip with Brand Palette ────────────────────────────
    st.markdown("<div style='max-width:1160px;margin:0 auto;'>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    stat_items = [
        ("49,688", "Catalog Items", "Full Instacart taxonomy", "var(--primary)"),
        ("3,733,948", "Prior Interactions", "Trained on authentic retail data", "var(--secondary)"),
        ("< 150 ms", "Retrieval Latency", "Vectorized PyTorch cosine engine", "var(--coral)"),
        ("3-Stage", "Production Funnel", "Retrieval → Re-rank → Guardrails", "var(--primary-dark)"),
    ]
    for col, (val, label, sub, color) in zip([m1, m2, m3, m4], stat_items):
        with col:
            st.markdown(f"""
            <div class="sb-elevate-card" style="text-align:center;padding:24px 18px;border-top:4px solid {color};">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:2.2rem;font-weight:800;color:{color};margin-bottom:4px;">{val}</div>
                <div style="font-size:0.92rem;font-weight:700;color:var(--text-1);margin-bottom:4px;">{label}</div>
                <div style="font-size:0.74rem;color:var(--text-3);">{sub}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

    # ── 4. Section: Why Apriori Fails vs Two-Tower AI ───────────────────
    st.markdown("""
    <div style="max-width:1160px;margin:0 auto;text-align:center;">
        <span class="sb-brand-tag" style="font-size:0.75rem;padding:4px 14px;">Algorithmic Evolution</span>
        <h2 style="font-size:2.2rem;font-weight:800;color:var(--text-1);margin:12px 0 8px 0;letter-spacing:-0.02em;">
            Why Supermarkets Are Retiring Apriori
        </h2>
        <p style="color:var(--text-2);font-size:0.98rem;max-width:640px;margin:0 auto 40px auto;line-height:1.6;">
            Association rule mining from 1994 cannot handle personalized recurring grocery consumption.
            Here is how our deep neural architecture solves what Apriori cannot.
        </p>
    </div>
    """, unsafe_allow_html=True)

    vs_l, vs_r = st.columns(2, gap="large")
    with vs_l:
        st.markdown("""
        <div class="sb-vs-card-old">
            <div style="font-size:1.25rem;font-weight:800;color:var(--coral-dark);margin-bottom:14px;display:flex;align-items:center;gap:8px;">
                <span>⚠️ Legacy Apriori / FP-Growth</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:14px;">
                <div style="display:flex;gap:12px;font-size:0.87rem;color:var(--text-2);line-height:1.5;">
                    <span style="color:var(--coral);font-weight:800;">✕</span>
                    <span><b>Zero Personalization:</b> Everyone buying pasta gets recommended pasta sauce, completely ignoring dietary profiles, organic preferences, or price tier.</span>
                </div>
                <div style="display:flex;gap:12px;font-size:0.87rem;color:var(--text-2);line-height:1.5;">
                    <span style="color:var(--coral);font-weight:800;">✕</span>
                    <span><b>Blind to Repurchase Cadence:</b> Groceries are consumable staples. Milk is bought every 4 days, olive oil every 45 days. Apriori treats all baskets as static snapshots.</span>
                </div>
                <div style="display:flex;gap:12px;font-size:0.87rem;color:var(--text-2);line-height:1.5;">
                    <span style="color:var(--coral);font-weight:800;">✕</span>
                    <span><b>Combinatorial Collapse:</b> Generating itemsets for 50,000 products requires exponential compute and fails under real supermarket scale.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with vs_r:
        st.markdown("""
        <div class="sb-vs-card-new">
            <div style="font-size:1.25rem;font-weight:800;color:var(--primary-dark);margin-bottom:14px;display:flex;align-items:center;gap:8px;">
                <span>🧠 SmartBasket Two-Tower AI</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:14px;">
                <div style="display:flex;gap:12px;font-size:0.87rem;color:var(--text-1);line-height:1.5;">
                    <span style="color:var(--primary);font-weight:800;">✓</span>
                    <span><b>User + Context Representation:</b> Learns dense 64-dimensional vectors from customer purchase histories, 21-department affinity vectors, and trip context.</span>
                </div>
                <div style="display:flex;gap:12px;font-size:0.87rem;color:var(--text-1);line-height:1.5;">
                    <span style="color:var(--primary);font-weight:800;">✓</span>
                    <span><b>Predictive Depletion Engine:</b> Models user-item purchase intervals (Δt / Cycle) to alert customers exactly when milk, eggs, or coffee run out.</span>
                </div>
                <div style="display:flex;gap:12px;font-size:0.87rem;color:var(--text-1);line-height:1.5;">
                    <span style="color:var(--primary);font-weight:800;">✓</span>
                    <span><b>Sub-Second Vectorized Search:</b> Performs dot-product cosine similarity over 49,688 items in &lt;150ms on standard CPUs.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

    # ── 5. Section: The 3-Stage Enterprise Recommendation Funnel ─────
    st.markdown("""
    <div style="max-width:1160px;margin:0 auto;text-align:center;">
        <span class="sb-brand-tag" style="background:var(--secondary-light);color:var(--primary-dark);border-color:rgba(145,174,110,0.4);">
            Enterprise Architecture
        </span>
        <h2 style="font-size:2.2rem;font-weight:800;color:var(--text-1);margin:12px 0 8px 0;letter-spacing:-0.02em;">
            The 3-Stage Recommendation Funnel
        </h2>
        <p style="color:var(--text-2);font-size:0.98rem;max-width:620px;margin:0 auto 40px auto;line-height:1.6;">
            Modeled directly on modern architectures used by Instacart, Walmart, and Ocado.
        </p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="large")
    steps = [
        ("01", "var(--primary)", "Stage 1: Two-Tower Retrieval",
         "Dual neural network mapping user profile (history, dept affinity, hour, dow) and catalog items into a normalized 64-dim unit sphere.",
         ["49,688 catalog items evaluated", "In-batch InfoNCE contrastive loss", "Retrieves Top 100 in <150ms"]),
        ("02", "var(--secondary)", "Stage 2: Contextual Re-Ranker",
         "Real-time basket scoring that blends Two-Tower similarity with live cart co-purchase affinity and personalized depletion urgency.",
         ["Live cart co-purchase graph", "Depletion ratio (Δt / Cycle)", "Sub-millisecond scoring (<1ms)"]),
        ("03", "var(--coral)", "Stage 3: Guardrails & Badging",
         "Business constraint enforcement including anti-cannibalization (no 2 whole milks) and transparent natural-language reasons.",
         ["Max 2 items per aisle (Diversity)", "Substitute suppression", "Explainability badges generation"]),
    ]

    for col, (num, color, title, desc, bullets) in zip([f1, f2, f3], steps):
        with col:
            st.markdown(f"""
            <div class="sb-step-card">
                <div class="sb-step-num" style="color:{color};">{num}</div>
                <div style="font-weight:800;font-size:1.05rem;color:var(--text-1);margin-bottom:8px;">{title}</div>
                <div style="font-size:0.85rem;color:var(--text-2);line-height:1.6;margin-bottom:16px;">{desc}</div>
                <div style="border-top:1px solid var(--border);padding-top:12px;display:flex;flex-direction:column;gap:6px;">
                    {''.join(f'<div style="font-size:0.78rem;font-weight:600;color:var(--text-1);">• {b}</div>' for b in bullets)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

    # ── 6. Section: Shopper Archetypes (DNA Clustering) ───────────────
    st.markdown("""
    <div style="max-width:1160px;margin:0 auto;text-align:center;">
        <span class="sb-brand-tag" style="background:var(--primary-light);color:var(--primary-dark);border-color:rgba(104,157,75,0.4);">
            Personalization Engine
        </span>
        <h2 style="font-size:2.2rem;font-weight:800;color:var(--text-1);margin:12px 0 8px 0;letter-spacing:-0.02em;">
            AI Learns Customer Shopping DNA
        </h2>
        <p style="color:var(--text-2);font-size:0.98rem;max-width:620px;margin:0 auto 36px auto;line-height:1.6;">
            Every shopper has unique cadences, department affinities, and repurchase habits.
            SmartBasket AI automatically personalizes for distinct customer archetypes:
        </p>
    </div>
    """, unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3, gap="large")
    personas_showcase = [
        ("🥗", "Produce & Organic Lover", "User #4", "Every 4.5 days", "72% Fresh Produce", "var(--primary)",
         "Avocados, organic baby spinach, limes, cilantro, olive oil."),
        ("🥛", "Dairy & Pantry Household", "User #12", "Every 6.8 days", "58% Dairy & Pantry", "var(--secondary)",
         "Whole milk, Greek yogurt, shredded cheddar, sourdough bread."),
        ("🍿", "Snack & Beverage Explorer", "User #29", "Every 11.2 days", "64% Snacks & Drinks", "var(--coral)",
         "Sparkling water, pita chips, organic dark chocolate, cold brew."),
    ]
    for col, (emoji, name, uid, cadence, affinity, color, sample_items) in zip([p1, p2, p3], personas_showcase):
        with col:
            st.markdown(f"""
            <div class="sb-elevate-card">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                    <div style="width:48px;height:48px;border-radius:14px;background:var(--bg-main);display:flex;align-items:center;justify-content:center;font-size:1.5rem;">
                        {emoji}
                    </div>
                    <div>
                        <div style="font-weight:800;font-size:0.95rem;color:var(--text-1);">{name}</div>
                        <div style="font-size:0.74rem;color:var(--text-3);">{uid} • Trip Cadence: {cadence}</div>
                    </div>
                </div>
                <div style="background:var(--bg-main);border-radius:10px;padding:10px 12px;margin-bottom:12px;">
                    <div style="font-size:0.72rem;font-weight:700;color:var(--text-2);margin-bottom:4px;">Dominant Category Affinity</div>
                    <div style="font-size:0.85rem;font-weight:800;color:{color};">{affinity}</div>
                </div>
                <div style="font-size:0.78rem;color:var(--text-2);line-height:1.5;">
                    <b>Sample Recommendations:</b><br>{sample_items}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)

    # ── 7. Classy High-Impact CTA Banner ──────────────────────────────
    st.markdown("""
    <div style="max-width:1160px;margin:0 auto;">
        <div style="
            background: linear-gradient(135deg, #4B7336 0%, #689D4B 55%, #91AE6E 100%);
            border-radius: 28px;
            padding: 56px 40px;
            text-align: center;
            box-shadow: 0 20px 48px rgba(75, 115, 54, 0.22);
            position: relative;
            overflow: hidden;
        ">
            <div style="display:inline-block;padding:4px 14px;background:rgba(255,255,255,0.18);border-radius:9999px;font-size:0.75rem;font-weight:800;color:#FFFFFF;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:16px;">
                Ready For Modern Supermarket Recommenders?
            </div>
            <h2 style="color:#FFFFFF;font-size:clamp(1.8rem, 3.8vw, 2.6rem);font-weight:800;margin-bottom:12px;letter-spacing:-0.02em;">
                Test Live Customer Baskets Right Now
            </h2>
            <p style="color:rgba(255,255,255,0.88);font-size:1.02rem;max-width:580px;margin:0 auto 32px auto;line-height:1.6;">
                Switch between shopper personas, add items to your live cart, and watch
                neural recommendations and depletion alerts update in sub-second time.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered CTA button
    cta_l, cta_btn, cta_r = st.columns([3.5, 3, 3.5])
    with cta_btn:
        if st.button("🚀  Enter SmartBasket Simulator", use_container_width=True, type="primary"):
            nav_goto("signup")

    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:24px 0;color:var(--text-3);font-size:0.8rem;border-top:1px solid var(--border);">
        SmartBasket AI • Powered by Hybrid Two-Tower PyTorch Architecture • Instacart Retail Benchmark
    </div>
    """, unsafe_allow_html=True)
