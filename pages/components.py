"""
Shared styles, navigation bar, and utility components.
Color palette:
- Primary: #689D4B (Rich Leaf Green)
- Secondary: #91AE6E (Sage Olive Green)
- Coral Accent: #D96868 (Warm Coral Rose)
- Neutral Background: #F2F2F2 (Soft Off-White/Gray)
"""

import streamlit as st


GLOBAL_CSS = """
<style>
/* ── Google Fonts ─────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

/* ── Reset & Base ─────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #F2F2F2;
    color: #1F291E;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Design Tokens ────────────────────────── */
:root {
    --primary:        #689D4B;   /* Rich Leaf Green */
    --primary-dark:   #4B7336;   /* Deep Olive Leaf */
    --primary-light:  #EAF2E6;   /* Pale Sage Wash */
    --secondary:      #91AE6E;   /* Sage Olive Green */
    --secondary-light:#F1F6EC;   /* Delicate Sage Tint */
    --coral:          #D96868;   /* Warm Coral Rose */
    --coral-light:    #FCEEEE;   /* Soft Coral Wash */
    --coral-dark:     #B84D4D;   /* Deep Coral */
    --bg-main:        #F2F2F2;   /* Clean Off-White */
    --surface:        #FFFFFF;   /* Pure White */
    --surface-glass:  rgba(255, 255, 255, 0.85);
    --border:         #E2E7DE;
    --border-accent:  rgba(104, 157, 75, 0.35);
    --text-1:         #192416;   /* Dark Forest Slate */
    --text-2:         #4B5A47;   /* Muted Leaf Slate */
    --text-3:         #83947F;   /* Soft Sage Gray */
    --radius-sm:      8px;
    --radius-md:      16px;
    --radius-lg:      24px;
    --radius-pill:    9999px;
    --shadow-sm:      0 2px 8px rgba(31, 41, 30, 0.04);
    --shadow-md:      0 8px 24px rgba(31, 41, 30, 0.08);
    --shadow-lg:      0 16px 40px rgba(104, 157, 75, 0.12);
    --shadow-coral:   0 12px 32px rgba(217, 104, 104, 0.18);
}

/* ── Keyframe Animations ──────────────────── */
@keyframes floatSlow {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

@keyframes pulseDot {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.6; }
}

@keyframes shimmerGlow {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Classy Header / Navigation Bar ──────── */
.sb-header {
    position: fixed;
    top: 14px;
    left: 50%;
    transform: translateX(-50%);
    width: min(1180px, calc(100% - 32px));
    height: 68px;
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(145, 174, 110, 0.3);
    border-radius: var(--radius-pill);
    box-shadow: 0 10px 30px rgba(75, 115, 54, 0.08);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    transition: all 0.3s ease;
}

.sb-header-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    font-weight: 800;
    font-size: 1.22rem;
    color: var(--text-1);
    letter-spacing: -0.02em;
}

.sb-brand-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-size: 1.15rem;
    box-shadow: 0 4px 12px rgba(104, 157, 75, 0.3);
}

.sb-brand-tag {
    color: var(--coral);
    font-size: 0.72rem;
    background: var(--coral-light);
    border: 1px solid rgba(217, 104, 104, 0.25);
    padding: 2px 8px;
    border-radius: var(--radius-pill);
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.sb-header-nav {
    display: flex;
    align-items: center;
    gap: 8px;
}

.sb-nav-link {
    color: var(--text-2);
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: var(--radius-pill);
    transition: all 0.2s ease;
}

.sb-nav-link:hover {
    color: var(--primary-dark);
    background: var(--secondary-light);
}

.sb-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--primary-light);
    border: 1px solid rgba(104, 157, 75, 0.3);
    color: var(--primary-dark);
    font-size: 0.76rem;
    font-weight: 700;
    padding: 5px 12px;
    border-radius: var(--radius-pill);
}

.sb-pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--primary);
    animation: pulseDot 2s infinite ease-in-out;
}

/* ── Hero Container ───────────────────────── */
.sb-hero-wrap {
    padding: 130px 24px 70px;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
}

.sb-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    background: #FFFFFF;
    border: 1.5px solid var(--border-accent);
    border-radius: var(--radius-pill);
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--primary-dark);
    box-shadow: var(--shadow-sm);
    margin-bottom: 24px;
    animation: slideUpFade 0.6s ease;
}

.sb-hero-h1 {
    font-size: clamp(2.4rem, 5.2vw, 4.2rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.03em;
    color: var(--text-1);
    margin-bottom: 22px;
    animation: slideUpFade 0.8s ease;
}

.sb-hero-h1 .highlight-green {
    color: var(--primary);
    position: relative;
    display: inline-block;
}

.sb-hero-h1 .highlight-coral {
    color: var(--coral);
    position: relative;
    display: inline-block;
}

.sb-hero-desc {
    font-size: 1.12rem;
    line-height: 1.7;
    color: var(--text-2);
    max-width: 620px;
    margin-bottom: 36px;
    animation: slideUpFade 1s ease;
}

/* ── Interactive Live Simulation Card (Hero Visual) ── */
.sb-hero-card {
    background: #FFFFFF;
    border: 1.5px solid var(--border-accent);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    padding: 24px;
    animation: floatSlow 5s infinite ease-in-out;
    position: relative;
    overflow: hidden;
}

.sb-hero-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--coral), var(--secondary), var(--primary));
}

.sb-sim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 14px;
    margin-bottom: 16px;
}

.sb-sim-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: var(--secondary-light);
    border-radius: var(--radius-pill);
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--primary-dark);
}

.sb-item-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    background: #F9FBF8;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
    transition: all 0.25s ease;
}

.sb-item-row:hover {
    transform: translateX(4px);
    border-color: var(--primary);
    box-shadow: var(--shadow-sm);
}

.sb-rec-glow-row {
    background: linear-gradient(135deg, #FFFFFF, var(--primary-light));
    border: 1.5px solid var(--primary);
    box-shadow: 0 6px 18px rgba(104, 157, 75, 0.15);
    border-radius: var(--radius-md);
    padding: 14px;
    margin-top: 14px;
    position: relative;
}

/* ── Interactive Cards with Hover Elevate ── */
.sb-elevate-card {
    background: #FFFFFF;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 30px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: var(--shadow-sm);
    height: 100%;
    position: relative;
}

.sb-elevate-card:hover {
    transform: translateY(-8px);
    border-color: var(--secondary);
    box-shadow: var(--shadow-md);
}

.sb-card-icon-wrap {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 18px;
}

/* ── Apriori vs Neural Contrast Section ──── */
.sb-vs-card-old {
    background: #FFFFFF;
    border: 1.5px solid rgba(217, 104, 104, 0.35);
    border-radius: var(--radius-lg);
    padding: 28px;
    box-shadow: var(--shadow-sm);
    position: relative;
}

.sb-vs-card-old::before {
    content: "OUTDATED 1994";
    position: absolute;
    top: 16px;
    right: 20px;
    background: var(--coral-light);
    color: var(--coral-dark);
    font-size: 0.7rem;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: var(--radius-pill);
    letter-spacing: 0.05em;
}

.sb-vs-card-new {
    background: #FFFFFF;
    border: 2px solid var(--primary);
    border-radius: var(--radius-lg);
    padding: 28px;
    box-shadow: var(--shadow-lg);
    position: relative;
}

.sb-vs-card-new::before {
    content: "TWO-TOWER NEURAL";
    position: absolute;
    top: 16px;
    right: 20px;
    background: var(--primary-light);
    color: var(--primary-dark);
    font-size: 0.7rem;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: var(--radius-pill);
    letter-spacing: 0.05em;
}

/* ── Interactive Process Flow Steps ───────── */
.sb-step-card {
    background: #FFFFFF;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px;
    position: relative;
    transition: all 0.3s ease;
}

.sb-step-card:hover {
    border-color: var(--primary);
    transform: translateY(-6px);
    box-shadow: var(--shadow-md);
}

.sb-step-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 12px;
}

/* ── Form Inputs & Streamlit Button Overrides ── */
.stButton > button {
    border-radius: var(--radius-pill) !important;
    font-weight: 700 !important;
    padding: 12px 26px !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.01em !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: none !important;
}

/* Primary Button in #689D4B */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #689D4B, #56843E) !important;
    color: #FFFFFF !important;
    box-shadow: 0 8px 20px rgba(104, 157, 75, 0.3) !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px rgba(104, 157, 75, 0.45) !important;
}

/* Secondary Button in Clean White / Border */
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: var(--text-1) !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button[kind="secondary"]:hover {
    border-color: var(--secondary) !important;
    background: var(--secondary-light) !important;
    color: var(--primary-dark) !important;
    transform: translateY(-2px) !important;
}

/* ── Badges ───────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: var(--radius-pill);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}
.badge-green   { background: var(--primary-light); color: var(--primary-dark); }
.badge-sage    { background: var(--secondary-light); color: #445935; }
.badge-coral   { background: var(--coral-light); color: var(--coral-dark); }
.badge-neutral { background: #EAEAEA; color: var(--text-2); }

/* ── Sidebar Nav (authenticated dashboard) ── */
.sb-sidenav {
    position: fixed; left: 0; top: 0; bottom: 0;
    width: 240px;
    background: #23341E;
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
.sb-sidenav-logo .dot { color: var(--coral); }
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
.sb-sidenav-item.active { background: rgba(145, 174, 110, 0.25); color: #fff; font-weight: 700; border-left: 3px solid var(--primary); }
.sb-sidenav-bottom { margin-top: auto; padding: 16px; border-top: 1px solid rgba(255,255,255,.1); }

/* ── Dashboard Main Area ──────────────────── */
.sb-dash-main { margin-left: 240px; padding: 32px 36px; min-height: 100vh; background: var(--bg-main); }
.sb-dash-header { margin-bottom: 28px; }
.sb-dash-header h1 { font-size: 1.6rem; font-weight: 800; color: var(--text-1); margin: 0 0 4px 0; }
.sb-dash-header p  { font-size: 0.88rem; color: var(--text-2); margin: 0; }

/* ── Depletion Bar ────────────────────────── */
.dep-bar-track { background: #E5E9E2; border-radius: 50px; height: 8px; width: 100%; margin: 6px 0; }
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
    color: var(--primary-dark);
    font-weight: 700;
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 50px;
    white-space: nowrap;
}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def nav_goto(page: str):
    st.session_state.current_page = page
    st.rerun()
