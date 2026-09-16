"""
SmartBasket AI - Main Entry Point (Login / Signup / Landing Router)
"""

import importlib
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

# Router with dynamic reload to ensure hot-reloading works for submodules
if not st.session_state.authenticated:
    page = st.session_state.current_page
    if page == "signup":
        import pages.signup as signup
        importlib.reload(signup)
        signup.render()
    elif page == "login":
        import pages.login as login
        importlib.reload(login)
        login.render()
    else:
        import pages.landing as landing
        importlib.reload(landing)
        landing.render()
else:
    page = st.session_state.current_page
    if page == "dashboard":
        import pages.dashboard as dashboard
        importlib.reload(dashboard)
        dashboard.render()
    elif page == "shop":
        import pages.shop as shop
        importlib.reload(shop)
        shop.render()
    elif page == "analytics":
        import pages.analytics as analytics
        importlib.reload(analytics)
        analytics.render()
    else:
        st.session_state.current_page = "dashboard"
        import pages.dashboard as dashboard
        importlib.reload(dashboard)
        dashboard.render()
