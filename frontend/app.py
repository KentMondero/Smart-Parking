import streamlit as st
import requests
import time
import csv
import io
from datetime import datetime
import pytz
from PIL import Image
import base64

PH_TZ = pytz.timezone("Asia/Manila")

def get_logo():
    try:
        with open("frontend/Logo.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{data}" style="width:44px;height:44px;border-radius:10px;object-fit:contain;">'
    except:
        return "🏫"
# ── Config ────────────────────────────────────────────────────────────────────
import os
API_BASE = os.environ.get("BACKEND_URL", "http://localhost:8000")
REFRESH_INTERVAL = 5

st.set_page_config(
    page_title="Park-U — Smart Parking System",
    page_icon=Image.open("frontend/Logo.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme state ───────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark = st.session_state.dark_mode

# ── Theme variables ───────────────────────────────────────────────────────────
if dark:
    BG          = "#0a0e1a"
    CARD_BG     = "#131929"
    CARD_BORDER = "#1e2847"
    HEADER_BG   = "linear-gradient(135deg,#1a1f35 0%,#0d1528 100%)"
    HEADER_BDR  = "#2a3158"
    TEXT        = "#e8eaf0"
    MUTED       = "#8892b0"
    SECTION_CLR = "#c7d2fe"
    INPUT_BG    = "#0d1528"
    INPUT_BDR   = "#2a3158"
    LOG_HDR_BG  = "#0d1528"
    LOG_HDR_BDR = "#2a3158"
    BADGE_CLS   = "background:#312e81;color:#c7d2fe"
    BADGE_NOCLS = "background:#1e293b;color:#94a3b8"
    PROFILE_BG  = "#131929"
    PROFILE_BDR = "#1e2847"
else:
    BG          = "#f0f4ff"
    CARD_BG     = "#ffffff"
    CARD_BORDER = "#dce3f5"
    HEADER_BG   = "linear-gradient(135deg,#4f5fcc 0%,#6c7de8 100%)"
    HEADER_BDR  = "#4f5fcc"
    TEXT        = "#1a1f35"
    MUTED       = "#64748b"
    SECTION_CLR = "#3730a3"
    INPUT_BG    = "#ffffff"
    INPUT_BDR   = "#c7d2fe"
    LOG_HDR_BG  = "#e8edff"
    LOG_HDR_BDR = "#c7d2fe"
    BADGE_CLS   = "background:#c7d2fe;color:#312e81"
    BADGE_NOCLS = "background:#e2e8f0;color:#64748b"
    PROFILE_BG  = "#ffffff"
    PROFILE_BDR = "#dce3f5"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family: 'Syne', sans-serif; }}

.stApp {{ background: {BG}; color: {TEXT}; }}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* ── Header ── */
.park-header {{
    background: {HEADER_BG};
    border: 1px solid {HEADER_BDR};
    border-radius: 16px;
    padding: 22px 32px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}}
.park-header::before {{
    content: '';
    position: absolute;
    top: -50%; left: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
    pointer-events: none;
}}
.park-logo {{
    width: 52px; height: 52px;
    border-radius: 12px;
    background: rgba(255,255,255,0.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem;
    flex-shrink: 0;
}}
.park-title {{
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    margin: 0;
}}
.park-subtitle {{
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    margin: 3px 0 0 0;
    font-family: 'Space Mono', monospace;
}}
.park-badge {{
    background: rgba(255,255,255,0.2);
    color: white;
    font-size: 0.68rem;
    font-family: 'Space Mono', monospace;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 1px;
    border: 1px solid rgba(255,255,255,0.3);
}}

/* ── Capacity bar ── */
.cap-bar-wrap {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 18px;
}}
.cap-bar-label {{
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
    color: {MUTED};
    margin-bottom: 8px;
}}
.cap-bar-track {{
    background: {CARD_BORDER};
    border-radius: 99px;
    height: 10px;
    overflow: hidden;
}}
.cap-bar-fill {{
    height: 100%;
    border-radius: 99px;
    transition: width 0.4s ease;
}}

/* ── Stat Cards ── */
.stat-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 14px;
    padding: 20px 24px;
    text-align: center;
    transition: border-color 0.2s;
}}
.stat-card:hover {{ border-color: #6366f1; }}
.stat-number {{ font-size: 2.8rem; font-weight: 800; line-height: 1; margin-bottom: 5px; }}
.stat-label {{ font-size: 0.72rem; color: {MUTED}; font-family: 'Space Mono', monospace; text-transform: uppercase; letter-spacing: 1px; }}
.stat-available .stat-number {{ color: #34d399; }}
.stat-occupied  .stat-number {{ color: #f87171; }}
.stat-total     .stat-number {{ color: #818cf8; }}

/* ── Section title ── */
.section-title {{
    font-size: 0.85rem;
    font-weight: 700;
    color: {SECTION_CLR};
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'Space Mono', monospace;
    margin: 0 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid {CARD_BORDER};
}}

/* ── Slot Grid ── */
.slot-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(82px, 1fr)); gap: 8px; margin-top: 8px; }}
.slot-box {{
    padding: 10px 4px;
    border-radius: 9px;
    text-align: center;
    font-size: 0.68rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    border: 2px solid transparent;
    transition: transform 0.15s;
}}
.slot-box:hover {{ transform: scale(1.06); }}
.slot-available {{ background: rgba(52,211,153,0.12); border-color: #34d399; color: #34d399; }}
.slot-occupied  {{ background: rgba(248,113,113,0.12); border-color: #f87171; color: #f87171; }}

/* ── Response alerts ── */
.response-success {{ background: rgba(52,211,153,0.1); border: 1px solid #34d399; border-left: 4px solid #34d399; border-radius: 10px; padding: 14px 18px; color: #34d399; font-weight: 600; }}
.response-warning {{ background: rgba(251,191,36,0.1);  border: 1px solid #fbbf24; border-left: 4px solid #fbbf24; border-radius: 10px; padding: 14px 18px; color: #fbbf24; font-weight: 600; }}
.response-error   {{ background: rgba(248,113,113,0.1); border: 1px solid #f87171; border-left: 4px solid #f87171; border-radius: 10px; padding: 14px 18px; color: #f87171; font-weight: 600; }}
.slot-assigned {{ font-family: 'Space Mono', monospace; font-size: 1rem; font-weight: 700; margin-top: 5px; }}

/* ── Log table ── */
.log-header {{
    background: {LOG_HDR_BG};
    border: 1px solid {LOG_HDR_BDR};
    border-radius: 9px;
    padding: 9px 14px;
    margin-bottom: 5px;
    display: grid;
    grid-template-columns: 1.2fr 0.8fr 1fr 2fr;
    gap: 8px;
    font-size: 0.68rem;
    font-family: 'Space Mono', monospace;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.log-row {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 9px;
    padding: 11px 14px;
    margin-bottom: 6px;
    display: grid;
    grid-template-columns: 1.2fr 0.8fr 1fr 2fr;
    gap: 8px;
    align-items: center;
    font-size: 0.8rem;
    color: {TEXT};
}}

.parked-name  {{ font-weight: 700; color: {TEXT}; }}
.parked-slot  {{ font-family: 'Space Mono', monospace; color: #6366f1; font-size: 0.88rem; }}
.parked-meta  {{ font-size: 0.72rem; color: {MUTED}; font-family: 'Space Mono', monospace; margin-top: 2px; }}
.duration-pill {{
    display: inline-block;
    background: rgba(99,102,241,0.15);
    color: #818cf8;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 6px;
}}

/* ── Profile card ── */
.profile-card {{
    background: {PROFILE_BG};
    border: 1px solid {PROFILE_BDR};
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
}}
.profile-name  {{ font-size: 1.25rem; font-weight: 800; color: {TEXT}; margin: 0 0 4px 0; }}
.profile-meta  {{ font-size: 0.78rem; color: {MUTED}; font-family: 'Space Mono', monospace; }}
.profile-stat  {{ text-align: center; }}
.profile-stat-num {{ font-size: 1.8rem; font-weight: 800; }}
.profile-stat-lbl {{ font-size: 0.68rem; color: {MUTED}; font-family: 'Space Mono', monospace; text-transform: uppercase; }}

/* ── Input overrides ── */
.stTextInput > label {{ color: {MUTED} !important; font-size: 0.78rem !important; font-family: 'Space Mono', monospace !important; text-transform: uppercase; letter-spacing: 1px; }}

.stTextInput > div > div > input {{
    background: {INPUT_BG} !important;
    border: 1px solid {INPUT_BDR} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
    font-family: 'Space Mono', monospace !important;
}}

.stTextInput > div > div > input::placeholder {{
    color: {MUTED} !important;
    opacity: 0.7 !important;
}}

.stTextInput > div > div > input:focus {{ border-color: #6366f1 !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important; }}
.stButton > button {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important; border-radius: 9px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.9rem !important; padding: 0.6rem 1.6rem !important;
    width: 100% !important; transition: opacity 0.2s !important;
}}
.stButton > button:hover {{ opacity: 0.86 !important; }}
.stTabs [data-baseweb="tab-list"] {{ background: {CARD_BG}; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid {CARD_BORDER}; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 8px; font-family: 'Syne', sans-serif; font-weight: 600; color: {MUTED}; }}
.stTabs [aria-selected="true"] {{ background: #6366f1 !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

# ── API Helpers ───────────────────────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def api_post(path, payload={}):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=5)
        if r.content:
            return r.json(), r.status_code
        return {"detail": "Empty response from server"}, r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def fetch_dashboard():
    return api_get("/parking/dashboard") or {
        "total_slots": 0, "available_slots": 0,
        "occupied_slots": 0, "current_parked_students": [],
    }

def fetch_slots():
    return api_get("/parking/slots") or []

def fetch_logs():
    return api_get("/parking/logs") or []

# ═════════════════════════════ HEADER ══════════════════════
header_col, toggle_col = st.columns([5, 1])
with header_col: 
    st.markdown(f"""
    <div class="park-header">
        <div style="display:flex;align-items:center;gap:16px;">
            <div class="park-logo">{get_logo()}</div>
            <div>
                <p style="font-size:2.5rem;font-weight:800;letter-spacing:-0.5px;color:#ffffff;margin:0;">Park-U</p>
                <p style="font-size:0.82rem;color:rgba(255,255,255,0.65);margin:3px 0 0 0;font-family:'Space Mono',monospace;">
                    Smart Parking Management System &nbsp;|&nbsp; {datetime.now(PH_TZ).strftime("%A, %B %d %Y")}
                </p>
            </div>
        </div>
        <span class="park-badge">● LIVE</span>
    </div>
    """, unsafe_allow_html=True)

with toggle_col:
    st.markdown("<br>", unsafe_allow_html=True)
    theme_label = "Light" if dark else "Dark"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


# ════════════════════════════ TABS ═════════════════════════════════════════════════
tab_dashboard, tab_profile = st.tabs(["Dashboard", "Student Profile"])

with tab_dashboard:

    stats = fetch_dashboard()
    total    = stats["total_slots"]
    avail    = stats["available_slots"]
    occupied = stats["occupied_slots"]
    pct      = int((occupied / total * 100) if total else 0)

    # Capacity bar colour
    if pct < 50:
        bar_color = "#34d399"
    elif pct < 80:
        bar_color = "#fbbf24"
    else:
        bar_color = "#f87171"

    # ── Capacity bar ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="cap-bar-wrap">
        <div class="cap-bar-label">
            <span>Parking Capacity</span>
            <span>{occupied}/{total} slots occupied ({pct}%)</span>
        </div>
        <div class="cap-bar-track">
            <div class="cap-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat cards ────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card stat-total"><div class="stat-number">{total}</div><div class="stat-label">Total Slots</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card stat-available"><div class="stat-number">{avail}</div><div class="stat-label">Available</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card stat-occupied"><div class="stat-number">{occupied}</div><div class="stat-label">Occupied</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.6], gap="large")

    # ── LEFT COLUMN ───────────────────────────────────────────────────────────
    with left:
        # Parking request form
        st.markdown('<p class="section-title">Request Parking</p>', unsafe_allow_html=True)
        student_id   = st.text_input("Student ID",  placeholder="input here", key="sid")
        student_name = st.text_input("Full Name",   placeholder="input here",  key="sname")

        btn_left, btn_right = st.columns(2)
        with btn_left:
            if st.button("Request Parking Slot"):
                if not student_id.strip() or not student_name.strip():
                    st.markdown('<div class="response-warning">Please enter both Student ID and Name.</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Processing…"):
                        result, status = api_post("/parking/request", {
                        "student_id": student_id.strip(),
                        "name": student_name.strip(),
                        })
                    if status == 200:
                        msg     = result.get("message", "")
                        slot    = result.get("slot_name")
                        success = result.get("success", False)
                        if success:
                            css  = "response-success"
                            icon = ""
                        elif "cannot" in msg.lower():
                            css  = "response-error"
                            icon = ""
                        elif "wait" in msg.lower() or "chance" in msg.lower():
                            css  = "response-warning"
                            icon = ""
                        else:
                            css  = "response-warning"
                            icon = ""
                        slot_html = f'<div class="slot-assigned">Assigned: {slot}</div>' if slot else ""
                        st.markdown(f'<div class="{css}">{icon} {msg}{slot_html}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="response-error"> {result.get("detail","Error")}</div>', unsafe_allow_html=True)

        with btn_right:
            if st.button("Release My Slot"):
                if not student_id.strip():
                    st.markdown('<div class="response-warning">Enter your Student ID above.</div>', unsafe_allow_html=True)
                else:
                    result, status = api_post(f"/parking/release/{student_id.strip()}")
                    if status == 200:
                        st.markdown(f'<div class="response-success">{result.get("message")}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="response-error">{result.get("detail","Error")}</div>', unsafe_allow_html=True)
    # ── RIGHT COLUMN ──────────────────────────────────────────────────────────
    with right:
        # Slot map
        st.markdown('<p class="section-title">Parking Slot Map</p>', unsafe_allow_html=True)
        slots = fetch_slots()
        if slots:
            slot_html = '<div class="slot-grid">'
            for s in slots:
                css  = "slot-available" if s["status"] == "available" else "slot-occupied"
                icon = "🟢" if s["status"] == "available" else "🔴"
                slot_html += f'<div class="slot-box {css}">{icon}<br>{s["slot_name"]}</div>'
            slot_html += "</div>"
            st.markdown(slot_html, unsafe_allow_html=True)
            st.markdown(f'<div style="display:flex;gap:20px;margin-top:10px;font-size:0.72rem;color:{MUTED};font-family:\'Space Mono\',monospace;"><span>🟢 Available</span><span>🔴 Occupied</span></div>', unsafe_allow_html=True)
        else:
            st.info("Could not load slot data. Ensure the API is running.")

    # ── Footer / refresh ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    fc1, fc2 = st.columns([3, 1])
    with fc1:
        st.markdown(f'<span style="color:{MUTED};font-size:0.7rem;font-family:\'Space Mono\',monospace;">Last updated: {datetime.now(PH_TZ).strftime("%A, %B %d %Y")} &nbsp;|&nbsp; Auto-refreshes every {REFRESH_INTERVAL}s</span>', unsafe_allow_html=True)
    with fc2:
        if st.button("Refresh"):
            st.rerun()


# ─── TAB 2 — STUDENT PROFILE ────────────────────────────────────────────────
with tab_profile:

    # ── Admin Authentication ───────────────────────────────────────────────────
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown('<p class="section-title">Admin Access Required</p>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:{MUTED};font-size:0.85rem;margin-bottom:16px;">This section is restricted to authorized administrators only.</div>', unsafe_allow_html=True)

        admin_pass = st.text_input("Admin Password", type="password", placeholder="input here", key="admin_pass")

        if st.button("Login as Admin", key="admin_login"):
            if admin_pass == "admin1234":
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.markdown('<div class="response-error">Incorrect password. Access denied.</div>', unsafe_allow_html=True)

    else:
        col_title, col_logout = st.columns([4, 1])
        with col_title:
            st.markdown('<p class="section-title">Student Profile & Parking History</p>', unsafe_allow_html=True)
        with col_logout:
            if st.button("Logout", key="admin_logout"):
                st.session_state.admin_authenticated = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ── STEP 1: Student Profile Search (MOVED HERE) ──────────────────────────
        pid_col, btn_col = st.columns([3, 1])
        with pid_col:
            profile_id = st.text_input("Student ID", placeholder="Enter Student ID to look up", key="profile_id")
        with btn_col:
            st.markdown("<br>", unsafe_allow_html=True)
            lookup = st.button("Look Up", key="profile_lookup")

        if lookup and profile_id.strip():
            profile = api_get(f"/parking/profile/{profile_id.strip()}")

            if not profile:
                st.markdown('<div class="response-error">Student not found. Make sure the ID is correct and the student has used the system at least once.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="profile-card">
                    <p class="profile-name"> {profile['name']}</p>
                    <p class="profile-meta">
                        {profile['student_id']} &nbsp;|&nbsp;
                        {profile.get('course') or 'N/A'} &nbsp;|&nbsp;
                        Year {profile.get('year_level') or 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                s1, s2, s3 = st.columns(3)
                with s1:
                    st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#818cf8">{profile["total_requests"]}</div><div class="stat-label">Total Requests</div></div>', unsafe_allow_html=True)
                with s2:
                    st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#34d399">{profile["approved"]}</div><div class="stat-label">Approved</div></div>', unsafe_allow_html=True)
                with s3:
                    st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:#f87171">{profile["denied"]}</div><div class="stat-label">Denied</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<p class="section-title">Parking History</p>', unsafe_allow_html=True)

                history = profile.get("history", [])
                if history:
                    st.markdown(f"""
                    <div class="log-header" style="grid-template-columns:0.6fr 0.8fr 1.2fr 2fr;">
                        <span>#</span><span>Slot</span><span>Date & Time</span><span>Result</span>
                    </div>""", unsafe_allow_html=True)
                    for entry in history:
                        badge = f'<span style="font-size:0.65rem;padding:2px 7px;border-radius:20px;{BADGE_CLS}">CLASS</span>' if entry["has_class_today"] else f'<span style="font-size:0.65rem;padding:2px 7px;border-radius:20px;{BADGE_NOCLS}">NO CLASS</span>'
                        slot_color = "#818cf8" if entry["slot_name"] != "N/A" else MUTED
                        st.markdown(f"""
                        <div class="log-row" style="grid-template-columns:0.6fr 0.8fr 1.2fr 2fr;">
                            <span style="color:{MUTED};font-family:\'Space Mono\',monospace;font-size:0.72rem">#{entry['log_id']}</span>
                            <span style="font-family:\'Space Mono\',monospace;color:{slot_color}">{entry['slot_name']}</span>
                            <span style="color:{MUTED};font-size:0.72rem">{entry['request_time']}</span>
                            <span>{badge} <span style="font-size:0.75rem;color:{SECTION_CLR}">{entry['response_message'][:50]}</span></span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="color:{MUTED};font-size:0.85rem;padding:12px 0;">No parking history found for this student.</div>', unsafe_allow_html=True)

        elif lookup:
            st.markdown('<div class="response-warning">Please enter a Student ID.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{MUTED};font-size:0.85rem;padding:20px 0;text-align:center;">Enter a Student ID above and click Look Up to view their parking history.</div>', unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


        # ── STEP 2: Parking Logs (MOVED HERE) ────────────────────────────────────
        st.markdown('<p class="section-title">Parking Logs</p>', unsafe_allow_html=True)

        logs = fetch_logs()

        search_col, export_col = st.columns([3, 1])
        with search_col:
            search = st.text_input("Search", placeholder="Name, Student ID, or date (YYYY-MM-DD)", key="log_search", label_visibility="collapsed")
        with export_col:
            if st.button("Export Logs"):
                if logs:
                    buf = io.StringIO()
                    writer = csv.DictWriter(buf, fieldnames=["LOG NO.","STUDENT ID","NAME","SLOT","DATE&TIME","SCHEDULE"])
                    writer.writeheader()
                    for log in logs:
                        writer.writerow({
                            "LOG NO.":           log["log_id"],
                            "STUDENT ID":       log["student_id"],
                            "NAME":     log["student_name"],
                            "SLOT":        log["slot_name"],
                            "DATE&TIME":     log["request_time"][:19].replace("T"," "),
                            "SCHEDULE":  log["has_class_today"],
                        })
                    st.download_button(
                        label="Download",
                        data=buf.getvalue(),
                        file_name=f"parking_logs_{datetime.now(PH_TZ).strftime("%A, %B %d %Y")}.csv",
                        mime="text/csv",
                        key="csv_dl",
                    )

        filtered = logs
        if search.strip():
            q = search.strip().lower()
            filtered = [
                l for l in logs
                if q in l["student_name"].lower()
                or q in l["student_id"].lower()
                or q in l["request_time"][:10]
            ]

        if filtered:
            st.markdown(f"""
            <div class="log-header">
                <span>Student</span><span>Slot</span><span>Time</span><span>Status</span>
            </div>""", unsafe_allow_html=True)
            for log in filtered[:20]:
                time_str = log["request_time"][:19].replace("T", " ")
                badge    = f'<span style="font-size:0.65rem;padding:2px 7px;border-radius:20px;{BADGE_CLS}">CLASS</span>' if log["has_class_today"] else f'<span style="font-size:0.65rem;padding:2px 7px;border-radius:20px;{BADGE_NOCLS}">NO CLASS</span>'
                msg_s    = log["response_message"][:50] + ("…" if len(log["response_message"]) > 50 else "")
                st.markdown(f"""
                <div class="log-row">
                    <span><b>{log['student_name']}</b><br><span style="color:{MUTED};font-size:0.68rem;font-family:'Space Mono',monospace">{log['student_id']}</span></span>
                    <span style="font-family:'Space Mono',monospace;color:#818cf8">{log['slot_name']}</span>
                    <span style="color:{MUTED};font-size:0.72rem">{time_str}</span>
                    <span>{badge} <span style="font-size:0.75rem;color:{SECTION_CLR}">{msg_s}</span></span>
                </div>""", unsafe_allow_html=True)
            if search.strip():
                st.markdown(f'<div style="font-size:0.72rem;color:{MUTED};margin-top:6px;font-family:\'Space Mono\',monospace;">{len(filtered)} result(s) found</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{MUTED};font-size:0.85rem;padding:12px 0;">{"No matching logs found." if search.strip() else "No parking logs yet."}</div>', unsafe_allow_html=True)

# ── Auto-refresh (dashboard tab only) ────────────────────────────────────────
#time.sleep(REFRESH_INTERVAL)
#st.rerun()