"""
Shared styles, navigation bar, and utility components.
"""

import streamlit as st


GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ─────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Design Tokens ────────────────────────── */
:root {
    --primary:      #16a34a;   /* emerald-600  */
    --primary-dark: #14532d;   /* emerald-900  */
    --primary-light:#dcfce7;   /* emerald-100  */
    --accent:       #f59e0b;   /* amber-400    */
    --surface:      #ffffff;
    --surface-2:    #f8fafc;
    --surface-3:    #f1f5f9;
    --border:       #e2e8f0;
    --text-1:       #0f172a;
    --text-2:       #475569;
    --text-3:       #94a3b8;
    --danger:       #ef4444;
    --warning:      #f59e0b;
    --info:         #3b82f6;
    --radius:       14px;
    --shadow-sm:    0 1px 3px rgba(0,0,0,.08);
    --shadow-md:    0 4px 16px rgba(0,0,0,.10);
    --shadow-lg:    0 12px 40px rgba(0,0,0,.14);
}

/* ── Top Navigation Bar ───────────────────── */
.sb-navbar {
    position: fixed; top: 0; left: 0; right: 0;
    z-index: 9999;
    height: 64px;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center;
    padding: 0 40px;
    box-shadow: var(--shadow-sm);
}
.sb-navbar-logo {
    font-size: 1.25rem; font-weight: 800;
    color: var(--primary-dark);
    display: flex; align-items: center; gap: 8px;
    text-decoration: none;
}
.sb-navbar-logo span { color: var(--primary); }
.sb-navbar-links { display: flex; gap: 4px; margin-left: auto; align-items: center; }
.sb-nav-pill {
    padding: 8px 18px;
    border-radius: 50px;
    font-size: 0.875rem; font-weight: 500;
    cursor: pointer;
    border: none; background: transparent;
    color: var(--text-2);
    transition: all .18s;
}
.sb-nav-pill:hover { background: var(--surface-3); color: var(--text-1); }
.sb-nav-pill.active { background: var(--primary-light); color: var(--primary); }
.sb-nav-btn {
    padding: 9px 22px;
    border-radius: 50px;
    font-size: 0.875rem; font-weight: 600;
    cursor: pointer;
    border: 1.5px solid var(--primary);
    background: var(--primary);
    color: #fff;
    transition: all .18s;
    margin-left: 10px;
}
.sb-nav-btn:hover { background: var(--primary-dark); border-color: var(--primary-dark); }
.sb-nav-btn.ghost {
    background: transparent; color: var(--primary);
}
.sb-nav-btn.ghost:hover { background: var(--primary-light); }

/* ── Page Wrapper ─────────────────────────── */
.sb-page { padding-top: 80px; min-height: 100vh; background: var(--surface-2); }
.sb-container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.sb-section { padding: 60px 0; }

/* ── Card ─────────────────────────────────── */
.sb-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
    padding: 28px;
    transition: box-shadow .2s;
}
.sb-card:hover { box-shadow: var(--shadow-md); }
.sb-card-header { font-size: 1rem; font-weight: 700; color: var(--text-1); margin-bottom: 4px; }
.sb-card-sub { font-size: 0.8rem; color: var(--text-2); }

/* ── Stat Cards ───────────────────────────── */
.sb-stat {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    text-align: center;
}
.sb-stat-value { font-size: 2rem; font-weight: 800; color: var(--primary); }
.sb-stat-label { font-size: 0.78rem; color: var(--text-2); margin-top: 4px; font-weight: 500; }

/* ── Badges ───────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: .01em;
}
.badge-green   { background: #dcfce7; color: #15803d; }
.badge-amber   { background: #fef3c7; color: #b45309; }
.badge-red     { background: #fee2e2; color: #b91c1c; }
.badge-blue    { background: #dbeafe; color: #1d4ed8; }
.badge-slate   { background: #f1f5f9; color: #475569; }
.badge-primary { background: var(--primary-light); color: var(--primary); }

/* ── Depletion Bar ────────────────────────── */
.dep-bar-track { background: var(--surface-3); border-radius: 50px; height: 8px; width: 100%; margin: 6px 0; }
.dep-bar-fill  { border-radius: 50px; height: 8px; }

/* ── Recommendation Row ───────────────────── */
.rec-row {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid var(--border);
    gap: 12px;
}
.rec-row:last-child { border-bottom: none; }
.rec-row-name { font-size: 0.9rem; font-weight: 600; color: var(--text-1); }
.rec-row-meta { font-size: 0.76rem; color: var(--text-2); margin-top: 3px; }
.rec-row-reason { margin-top: 5px; }
.rec-score-pill {
    background: var(--primary-light);
    color: var(--primary);
    font-weight: 700;
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 50px;
    white-space: nowrap;
}

/* ── Form Inputs ──────────────────────────── */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid var(--border) !important;
    padding: 12px 16px !important;
    font-size: 0.9rem !important;
    background: var(--surface) !important;
    color: var(--text-1) !important;
    box-shadow: none !important;
    transition: border .18s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,.12) !important;
}
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 22px !important;
    font-size: 0.9rem !important;
    transition: all .18s !important;
}

/* ── Hero Section ─────────────────────────── */
.sb-hero { text-align: center; padding: 100px 24px 80px; }
.sb-hero-tag {
    display: inline-block;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 0.78rem; font-weight: 700;
    padding: 5px 16px; border-radius: 50px;
    letter-spacing: .04em; text-transform: uppercase;
    margin-bottom: 20px;
}
.sb-hero-title {
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 800;
    color: var(--text-1);
    line-height: 1.1;
    margin-bottom: 20px;
}
.sb-hero-title em { color: var(--primary); font-style: normal; }
.sb-hero-sub {
    font-size: 1.05rem; color: var(--text-2);
    max-width: 600px; margin: 0 auto 36px;
    line-height: 1.7;
}
.sb-hero-btns { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

/* ── Feature Grid ─────────────────────────── */
.sb-feature-icon {
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 14px;
}
.sb-feature-title { font-size: 1rem; font-weight: 700; color: var(--text-1); margin-bottom: 6px; }
.sb-feature-desc  { font-size: 0.85rem; color: var(--text-2); line-height: 1.65; }

/* ── Auth Page ────────────────────────────── */
.sb-auth-wrapper {
    min-height: 100vh;
    display: flex;
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 40%, #fff 100%);
}
.sb-auth-left {
    flex: 1;
    display: flex; align-items: center; justify-content: center;
    padding: 60px;
}
.sb-auth-right {
    width: 520px;
    background: var(--surface);
    display: flex; align-items: center; justify-content: center;
    padding: 60px 56px;
    box-shadow: -4px 0 30px rgba(0,0,0,.07);
}
.sb-auth-card { width: 100%; max-width: 380px; }
.sb-auth-title { font-size: 1.7rem; font-weight: 800; color: var(--text-1); margin-bottom: 8px; }
.sb-auth-sub   { font-size: 0.9rem; color: var(--text-2); margin-bottom: 32px; }
.sb-divider {
    display: flex; align-items: center; gap: 12px;
    color: var(--text-3); font-size: 0.8rem; font-weight: 500;
    margin: 18px 0;
}
.sb-divider::before, .sb-divider::after {
    content: ''; flex: 1; height: 1px; background: var(--border);
}

/* ── Sidebar Nav (dashboard) ──────────────── */
.sb-sidenav {
    position: fixed; left: 0; top: 0; bottom: 0;
    width: 240px;
    background: var(--primary-dark);
    padding: 0;
    z-index: 1000;
    display: flex; flex-direction: column;
}
.sb-sidenav-logo {
    padding: 24px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,.1);
    font-size: 1.15rem; font-weight: 800; color: #fff;
    display: flex; align-items: center; gap: 10px;
}
.sb-sidenav-logo .dot { color: var(--accent); }
.sb-sidenav-section { padding: 20px 16px 8px; font-size: 0.68rem; font-weight: 700; color: rgba(255,255,255,.4); text-transform: uppercase; letter-spacing: .08em; }
.sb-sidenav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 16px;
    margin: 2px 8px;
    border-radius: 10px;
    color: rgba(255,255,255,.7);
    font-size: 0.875rem; font-weight: 500;
    cursor: pointer;
    transition: all .15s;
}
.sb-sidenav-item:hover  { background: rgba(255,255,255,.1); color: #fff; }
.sb-sidenav-item.active { background: rgba(255,255,255,.18); color: #fff; font-weight: 700; }
.sb-sidenav-bottom { margin-top: auto; padding: 16px; border-top: 1px solid rgba(255,255,255,.1); }

/* ── Dashboard Main Area ──────────────────── */
.sb-dash-main { margin-left: 240px; padding: 32px 36px; min-height: 100vh; background: var(--surface-2); }
.sb-dash-header { margin-bottom: 28px; }
.sb-dash-header h1 { font-size: 1.6rem; font-weight: 800; color: var(--text-1); margin: 0 0 4px 0; }
.sb-dash-header p  { font-size: 0.88rem; color: var(--text-2); margin: 0; }

/* ── Cart Chip ────────────────────────────── */
.cart-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--surface); border: 1.5px solid var(--border);
    border-radius: 50px; padding: 6px 14px;
    font-size: 0.82rem; font-weight: 600; color: var(--text-1);
    cursor: pointer; transition: all .15s;
}
.cart-chip:hover { border-color: var(--primary); color: var(--primary); }

/* ── Section Title ────────────────────────── */
.sb-section-title { font-size: 1.05rem; font-weight: 700; color: var(--text-1); margin: 0 0 16px 0; }
.sb-section-sub   { font-size: 0.82rem; color: var(--text-2); margin: -12px 0 16px 0; }
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def nav_goto(page: str):
    st.session_state.current_page = page
    st.rerun()
