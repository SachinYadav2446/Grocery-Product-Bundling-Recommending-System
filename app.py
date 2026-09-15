"""
SmartBasket AI - Main Entry Point (Login / Signup / Landing Router)
"""

import streamlit as st

st.set_page_config(
    page_title="SmartBasket AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Shared session state bootstrap
for key, default in [
    ("authenticated", False),
    ("user_email", ""),
    ("user_name", ""),
    ("current_page", "landing"),
    ("cart", []),
    ("selected_persona", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Router
if not st.session_state.authenticated:
    page = st.session_state.current_page
    if page == "signup":
        import pages.signup as signup
        signup.render()
    elif page == "login":
        import pages.login as login
        login.render()
    else:
        import pages.landing as landing
        landing.render()
else:
    page = st.session_state.current_page
    if page == "dashboard":
        import pages.dashboard as dashboard
        dashboard.render()
    elif page == "shop":
        import pages.shop as shop
        shop.render()
    elif page == "analytics":
        import pages.analytics as analytics
        analytics.render()
    else:
        st.session_state.current_page = "dashboard"
        import pages.dashboard as dashboard
        dashboard.render()
