"""
Login page — clean two-column auth layout.
"""

import streamlit as st
from pages.components import inject_css, nav_goto

# Demo credentials
DEMO_USERS = {
    "demo@smartbasket.ai": {"password": "demo1234", "name": "Alex Johnson"},
    "manager@store.com": {"password": "store2024", "name": "Priya Sharma"},
}


def render():
    inject_css()

    # Remove default padding for full-bleed layout
    st.markdown("<style>section.main > div {padding-top:0!important;}</style>", unsafe_allow_html=True)

    # Two-column layout: left brand panel + right form
    left, right = st.columns([1, 1])

    # ── Left Brand Panel ───────────────────────────────────────────────
    with left:
        st.markdown("""
        <div style="
            background: linear-gradient(145deg, #14532d 0%, #16a34a 60%, #22c55e 100%);
            min-height: 100vh;
            padding: 60px 56px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        ">
            <div>
                <div style="font-size:1.3rem;font-weight:800;color:#fff;margin-bottom:60px;">
                    🛒 SmartBasket <span style="color:#86efac;">AI</span>
                </div>
                <h2 style="color:#fff;font-size:2.2rem;font-weight:800;line-height:1.2;margin-bottom:16px;">
                    Welcome back,<br>supermarket innovator.
                </h2>
                <p style="color:rgba(255,255,255,.75);font-size:0.95rem;line-height:1.7;margin-bottom:48px;">
                    Sign in to access your AI-powered recommendation dashboard,
                    live cart simulator, and depletion analytics.
                </p>
                <div style="display:flex;flex-direction:column;gap:14px;">
                    <div style="display:flex;align-items:center;gap:12px;color:rgba(255,255,255,.9);font-size:0.875rem;">
                        <div style="width:36px;height:36px;background:rgba(255,255,255,.15);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;">⚡</div>
                        Real-time recommendations in &lt; 150ms
                    </div>
                    <div style="display:flex;align-items:center;gap:12px;color:rgba(255,255,255,.9);font-size:0.875rem;">
                        <div style="width:36px;height:36px;background:rgba(255,255,255,.15);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;">🧠</div>
                        Hybrid Two-Tower Neural AI
                    </div>
                    <div style="display:flex;align-items:center;gap:12px;color:rgba(255,255,255,.9);font-size:0.875rem;">
                        <div style="width:36px;height:36px;background:rgba(255,255,255,.15);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;">📊</div>
                        49,688 products · 3M+ order interactions
                    </div>
                </div>
            </div>
            <p style="color:rgba(255,255,255,.4);font-size:0.75rem;margin-top:60px;">
                © 2026 SmartBasket AI · Instacart Dataset
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Right Form Panel ───────────────────────────────────────────────
    with right:
        # Center the form vertically
        st.markdown("<div style='min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:60px 56px;'>", unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-bottom:32px;">
            <h1 style="font-size:1.8rem;font-weight:800;color:#0f172a;margin-bottom:6px;">Sign in to your account</h1>
            <p style="color:#64748b;font-size:0.88rem;">Enter your credentials to access your dashboard.</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick hint
        st.markdown("""
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 16px;margin-bottom:24px;">
            <p style="margin:0;font-size:0.8rem;color:#15803d;font-weight:500;">
                🔑 <strong>Demo:</strong> demo@smartbasket.ai / demo1234
            </p>
        </div>
        """, unsafe_allow_html=True)

        email = st.text_input("Email address", placeholder="you@example.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

        col_check, col_forgot = st.columns(2)
        with col_check:
            remember = st.checkbox("Remember me", value=True)
        with col_forgot:
            st.markdown("<p style='text-align:right;margin-top:6px;'><a href='#' style='color:#16a34a;font-size:0.82rem;text-decoration:none;font-weight:600;'>Forgot password?</a></p>", unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Please fill in all fields.")
            elif email in DEMO_USERS and DEMO_USERS[email]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_name = DEMO_USERS[email]["name"]
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid email or password. Try demo@smartbasket.ai / demo1234")

        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;color:#94a3b8;font-size:0.8rem;margin:18px 0;">
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
            or continue with
            <div style="flex:1;height:1px;background:#e2e8f0;"></div>
        </div>
        """, unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            if st.button("🔵  Google", use_container_width=True):
                st.info("OAuth integration coming soon!")
        with g2:
            if st.button("⬛  GitHub", use_container_width=True):
                st.info("OAuth integration coming soon!")

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#64748b;font-size:0.85rem;'>Don't have an account?</p>", unsafe_allow_html=True)

        if st.button("Create a free account", use_container_width=True):
            nav_goto("signup")

        if st.button("← Back to Home", use_container_width=True):
            nav_goto("landing")

        st.markdown("</div>", unsafe_allow_html=True)
