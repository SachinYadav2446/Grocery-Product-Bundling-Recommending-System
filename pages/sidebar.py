"""
Shared sidebar navigation used across all authenticated pages.
"""

import streamlit as st
from pages.components import nav_goto


def render_sidebar(active_page: str = "dashboard"):
    nav_items = [
        ("dashboard",  "📊", "Dashboard"),
        ("shop",       "🛒", "Smart Shopper"),
        ("analytics",  "📈", "Analytics"),
    ]

    name = st.session_state.get("user_name", "User")
    email = st.session_state.get("user_email", "")
    initials = "".join(w[0].upper() for w in name.split()[:2])

    # Sidebar HTML
    links_html = ""
    for page_id, icon, label in nav_items:
        cls = "active" if active_page == page_id else ""
        links_html += f"""
        <div class="sb-sidenav-item {cls}" id="nav-{page_id}">
            <span style="font-size:1.1rem;">{icon}</span>
            <span>{label}</span>
        </div>
        """

    st.markdown(f"""
    <div class="sb-sidenav">
        <div class="sb-sidenav-logo">🛒 Smart<span class="dot">Basket</span></div>
        <div class="sb-sidenav-section">Navigation</div>
        {links_html}
        <div class="sb-sidenav-bottom">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:36px;height:36px;background:rgba(255,255,255,.2);border-radius:50%;
                     display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:0.85rem;flex-shrink:0;">
                    {initials}
                </div>
                <div style="overflow:hidden;">
                    <div style="color:#fff;font-size:0.82rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</div>
                    <div style="color:rgba(255,255,255,.45);font-size:0.7rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{email}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons (invisible, rendered below sidebar for click handling)
    st.markdown("<div style='position:fixed;left:0;top:80px;width:240px;z-index:1001;'>", unsafe_allow_html=True)

    with st.container():
        for page_id, icon, label in nav_items:
            if st.button(
                f"{icon} {label}",
                key=f"sidenav_{page_id}",
                use_container_width=True,
                type="primary" if active_page == page_id else "secondary",
            ):
                nav_goto(page_id)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🔓 Sign Out", use_container_width=True, key="signout_btn"):
            for k in ["authenticated", "user_email", "user_name", "cart", "selected_persona"]:
                if k in st.session_state:
                    del st.session_state[k]
            nav_goto("landing")

    st.markdown("</div>", unsafe_allow_html=True)
