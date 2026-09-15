"""
Signup page — registration with plan selection.
"""

import streamlit as st
from pages.components import inject_css, nav_goto

DEMO_USERS_REF = {
    "demo@smartbasket.ai": "demo1234",
    "manager@store.com": "store2024",
}


def render():
    inject_css()
    st.markdown("<style>section.main > div {padding-top:0!important;}</style>", unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    # ── Left Brand Panel ───────────────────────────────────────────────
    with left:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, #0c4a6e 0%, #0284c7 70%, #38bdf8 100%);
            min-height: 100vh;
            padding: 60px 56px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <div>
                <div style="font-size:1.3rem;font-weight:800;color:#fff;margin-bottom:60px;">
                    🛒 SmartBasket <span style="color:#7dd3fc;">AI</span>
                </div>
                <h2 style="color:#fff;font-size:2.2rem;font-weight:800;line-height:1.2;margin-bottom:16px;">
                    Join 500+ retailers<br>using AI-first recommendations.
                </h2>
                <p style="color:rgba(255,255,255,.75);font-size:0.95rem;line-height:1.7;margin-bottom:48px;">
                    Create your free account and get access to the full 3-stage
                    neural recommendation engine, depletion analytics, and live cart simulator.
                </p>
                <div style="background:rgba(255,255,255,.1);border-radius:16px;padding:24px;">
                    <p style="color:rgba(255,255,255,.6);font-size:0.75rem;text-transform:uppercase;font-weight:700;letter-spacing:.06em;margin-bottom:14px;">What you get</p>
                    <div style="display:flex;flex-direction:column;gap:10px;">
                        <div style="color:#fff;font-size:0.875rem;">✅ &nbsp;Hybrid Two-Tower Neural Recommendations</div>
                        <div style="color:#fff;font-size:0.875rem;">✅ &nbsp;Smart Replenish Depletion Engine</div>
                        <div style="color:#fff;font-size:0.875rem;">✅ &nbsp;Live Cart Context Simulator</div>
                        <div style="color:#fff;font-size:0.875rem;">✅ &nbsp;Customer Segment Analytics Dashboard</div>
                        <div style="color:#fff;font-size:0.875rem;">✅ &nbsp;Benchmark Metrics (HitRate, MRR, NDCG)</div>
                    </div>
                </div>
            </div>
            <p style="color:rgba(255,255,255,.4);font-size:0.75rem;margin-top:60px;">
                No credit card required · Free forever for solo stores
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Right Form Panel ───────────────────────────────────────────────
    with right:
        st.markdown("<div style='min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:60px 56px;'>", unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-bottom:28px;">
            <h1 style="font-size:1.8rem;font-weight:800;color:#0f172a;margin-bottom:6px;">Create your account</h1>
            <p style="color:#64748b;font-size:0.88rem;">Free forever for independent stores. Upgrade anytime.</p>
        </div>
        """, unsafe_allow_html=True)

        name = st.text_input("Full name", placeholder="Alex Johnson", key="signup_name")
        email = st.text_input("Email address", placeholder="you@example.com", key="signup_email")
        store = st.text_input("Store / Company name", placeholder="FreshMart Ltd.", key="signup_store")

        c1, c2 = st.columns(2)
        with c1:
            password = st.text_input("Password", type="password", placeholder="Min. 8 characters", key="signup_password")
        with c2:
            confirm = st.text_input("Confirm password", type="password", placeholder="Repeat password", key="signup_confirm")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Terms
        agree = st.checkbox("I agree to the **Terms of Service** and **Privacy Policy**")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Create Account →", use_container_width=True, type="primary"):
            if not all([name, email, password, confirm]):
                st.error("Please fill in all required fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            elif not agree:
                st.error("Please agree to the terms to continue.")
            else:
                # In a real app this would persist to a DB; we just log in immediately
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state.current_page = "dashboard"
                st.rerun()

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;color:#94a3b8;font-size:0.8rem;margin:18px 0;">
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
            or sign up with
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
        </div>
        """, unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            if st.button("🔵  Google", use_container_width=True, key="google_signup"):
                st.info("OAuth integration coming soon!")
        with g2:
            if st.button("⬛  GitHub", use_container_width=True, key="github_signup"):
                st.info("OAuth integration coming soon!")

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#64748b;font-size:0.85rem;'>Already have an account?</p>", unsafe_allow_html=True)

        if st.button("Sign in instead", use_container_width=True):
            nav_goto("login")

        if st.button("← Back to Home", use_container_width=True, key="back_landing_signup"):
            nav_goto("landing")

        st.markdown("</div>", unsafe_allow_html=True)
