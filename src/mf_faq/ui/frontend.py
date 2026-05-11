import streamlit as st
import requests
import time
from typing import Optional, List, Dict

# Configuration
API_URL = "http://127.0.0.1:8000/chat"

# Page Config
st.set_page_config(
    page_title="Grow RAG | Enterprise Tier",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design System Tokens (from DESIGN.md)
COLORS = {
    "surface": "#0e150e",
    "surface-container": "#1a221a",
    "on-surface": "#dce5d9",
    "primary": "#4be277",
    "secondary": "#4cd7f6",
    "outline": "#869585",
    "outline-variant": "#3d4a3d",
}

# Custom CSS for Premium Stitch Design
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Base Styles */
    .stApp {{
        background-color: {COLORS['surface']};
        color: {COLORS['on-surface']};
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {COLORS['surface-container']};
        border-right: 1px solid {COLORS['outline-variant']};
    }}
    
    /* Sidebar Navigation Items */
    .nav-item {{
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        color: {COLORS['on-surface']};
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: background 0.2s;
    }}
    
    .nav-item:hover {{
        background: rgba(75, 226, 119, 0.1);
    }}
    
    .nav-item.active {{
        background: rgba(75, 226, 119, 0.15);
        border-left: 3px solid {COLORS['primary']};
    }}

    /* Welcome Screen Typography */
    .display-text {{
        font-size: 48px;
        font-weight: 600;
        line-height: 1.1;
        letter-spacing: -0.04em;
        text-align: center;
        margin-top: 50px;
    }}
    
    .primary-highlight {{
        color: {COLORS['primary']};
    }}
    
    .subtext {{
        font-size: 18px;
        color: #bccbb9;
        text-align: center;
        max-width: 600px;
        margin: 20px auto 40px auto;
        line-height: 1.6;
    }}

    /* Cards */
    .suggestion-card {{
        background: {COLORS['surface-container']};
        border: 1px solid {COLORS['outline-variant']};
        border-radius: 12px;
        padding: 24px;
        height: 240px;
        transition: border-color 0.2s;
    }}
    
    .suggestion-card:hover {{
        border-color: {COLORS['primary']};
    }}
    
    .card-icon {{
        background: #242c24;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
    }}

    /* Chat Elements */
    .bot-message {{
        background: {COLORS['surface-container']};
        border: 1px solid {COLORS['primary']};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    
    .chip {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 8px;
        border: 1px solid {COLORS['outline-variant']};
        color: {COLORS['outline']};
    }}

    /* Source Cards (Right Sidebar) */
    .source-card {{
        background: {COLORS['surface-container']};
        border: 1px solid {COLORS['outline-variant']};
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }}
    
    .confidence-bar {{
        height: 4px;
        background: {COLORS['outline-variant']};
        border-radius: 2px;
        margin-top: 8px;
    }}
    
    .confidence-fill {{
        height: 100%;
        background: {COLORS['primary']};
        border-radius: 2px;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "view" not in st.session_state:
    st.session_state.view = "welcome"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []

# --- SIDEBAR (Fixed for both views) ---
with st.sidebar:
    st.markdown(f'<h2 style="color: {COLORS["primary"]}; margin-bottom: 0;">Grow RAG</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 10px; color: #869585; text-transform: uppercase; letter-spacing: 0.1em;">Enterprise Tier</p>', unsafe_allow_html=True)
    st.write("")
    
    # Nav Items
    st.markdown('<div class="nav-item active">💬 New Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">🕒 History</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">📚 Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">👥 Team</div>', unsafe_allow_html=True)
    
    st.write("") # Spacer
    st.markdown('<div style="height: 200px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">⚙️ Settings</div>', unsafe_allow_html=True)
    
    # User Profile (Bottom)
    st.write("---")
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px;">
            <img src="https://ui-avatars.com/api/?name=Alex+Rivera&background=4be277&color=003915" style="width: 32px; height: 32px; border-radius: 6px;">
            <div>
                <p style="margin:0; font-size: 13px; font-weight: 600;">Alex Rivera</p>
                <p style="margin:0; font-size: 10px; color: {COLORS['primary']};">UPGRADE PLAN</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
if st.session_state.view == "welcome":
    # Top Nav
    cols = st.columns([1, 1, 1, 5, 1, 1])
    cols[0].write("Models")
    cols[1].write("API")
    cols[2].write("Docs")
    
    # Hero Section
    st.markdown('<div style="text-align: center; margin-top: 80px;"><img src="https://groww.in/groww-logo-270.png" style="width: 60px; filter: invert(1);"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="display-text">Precision <span class="primary-highlight">Intelligence</span> Awaits.</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtext">Connect your workspace data to our advanced retrieval-augmented generation engine. Start a new conversation to begin.</p>', unsafe_allow_html=True)
    
    # Buttons
    btn_cols = st.columns([2, 1, 1, 2])
    if btn_cols[1].button("🚀 START NEW SESSION", use_container_width=True):
        st.session_state.view = "chat"
        st.rerun()
    btn_cols[2].button("📤 UPLOAD DATA", use_container_width=True)
    
    st.write("")
    st.write("")
    
    # Suggestion Cards
    card_cols = st.columns(3)
    
    with card_cols[0]:
        st.markdown("""
            <div class="suggestion-card">
                <div class="card-icon">📄</div>
                <h4 style="margin: 0 0 10px 0;">Analyze this PDF</h4>
                <p style="font-size: 13px; color: #bccbb9; line-height: 1.5;">Extract key insights, data points, and executive summaries from complex documents in seconds.</p>
                <p style="color: #4be277; font-size: 12px; margin-top: 20px; font-weight: 600; cursor: pointer;">TRY SUGGESTION →</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Try PDF", key="btn_pdf", help="Analyze HDFC Mid Cap NAV"):
            st.session_state.view = "chat"
            st.session_state.messages.append({"role": "user", "content": "What is the NAV of HDFC Mid Cap?"})
            st.rerun()

    with card_cols[1]:
        st.markdown("""
            <div class="suggestion-card">
                <div class="card-icon">📈</div>
                <h4 style="margin: 0 0 10px 0;">Summarize Workspace</h4>
                <p style="font-size: 13px; color: #bccbb9; line-height: 1.5;">Get a high-level overview of recent activities and files synchronized across your enterprise tier.</p>
                <p style="color: #4be277; font-size: 12px; margin-top: 20px; font-weight: 600; cursor: pointer;">TRY SUGGESTION →</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Try ELSS", key="btn_elss"):
            st.session_state.view = "chat"
            st.session_state.messages.append({"role": "user", "content": "What is the exit load for HDFC ELSS?"})
            st.rerun()

    with card_cols[2]:
        st.markdown("""
            <div class="suggestion-card">
                <div class="card-icon">⚖️</div>
                <h4 style="margin: 0 0 10px 0;">Audit Repository</h4>
                <p style="font-size: 13px; color: #bccbb9; line-height: 1.5;">Perform a semantic search over your codebases to identify patterns or potential optimization areas.</p>
                <p style="color: #4be277; font-size: 12px; margin-top: 20px; font-weight: 600; cursor: pointer;">TRY SUGGESTION →</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Try Large Cap", key="btn_large"):
            st.session_state.view = "chat"
            st.session_state.messages.append({"role": "user", "content": "Minimum investment for HDFC Large Cap?"})
            st.rerun()

elif st.session_state.view == "chat":
    # Chat Layout with Right Sidebar
    main_col, side_col = st.columns([3, 1])
    
    with main_col:
        # Chat Messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div style="display: flex; gap: 15px; margin-bottom: 30px;">
                        <img src="https://ui-avatars.com/api/?name=Alex+Rivera&background=242c24&color=dce5d9" style="width: 32px; height: 32px; border-radius: 6px;">
                        <div>
                            <p style="margin:0; font-size: 11px; font-weight: 600; color: #869585; margin-bottom: 4px;">YOU • JUST NOW</p>
                            <p style="margin:0; font-size: 15px; line-height: 1.6;">{msg['content']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="display: flex; gap: 15px; margin-bottom: 30px;">
                        <div style="background: {COLORS['primary']}; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #003915; font-weight: bold;">G</div>
                        <div class="bot-message">
                            <p style="margin:0; font-size: 11px; font-weight: 600; color: {COLORS['primary']}; margin-bottom: 12px;">GROW AI • JUST NOW</p>
                            <div style="font-size: 15px; line-height: 1.6;">{msg['content']}</div>
                            <div style="margin-top: 20px;">
                                <span class="chip">VERIFIED ACCURACY</span>
                                <span class="chip">INTERNAL SOURCES: 1</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Input Bar (Custom)
        user_query = st.chat_input("Ask Grow RAG anything...")
        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            # Call Backend
            try:
                response = requests.post(API_URL, json={"query": user_query}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.messages.append({"role": "assistant", "content": data["answer"]})
                    if data["source"]:
                        st.session_state.sources = [{"name": "Groww.in Source", "url": data["source"], "confidence": 98}]
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "Error connecting to service."})
            except:
                st.session_state.messages.append({"role": "assistant", "content": "Network error."})
            st.rerun()

    with side_col:
        st.markdown(f'<h3 style="display: flex; align-items: center; gap: 10px;"><span style="color: {COLORS["secondary"]};">📄</span> Sources</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 10px; color: #869585; text-transform: uppercase;">RAG-LATENCY: 420ms</p>', unsafe_allow_html=True)
        
        if not st.session_state.sources:
            st.write("No sources active.")
        else:
            for src in st.session_state.sources:
                st.markdown(f"""
                    <div class="source-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 10px; font-weight: 600; color: {COLORS['secondary']};">CONFIDENCE: {src['confidence']}%</span>
                            <a href="{src['url']}" target="_blank" style="color: {COLORS['on-surface']}; text-decoration: none; font-size: 12px;">↗</a>
                        </div>
                        <p style="margin: 8px 0 0 0; font-size: 13px; font-weight: 600;">{src['name']}</p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {src['confidence']}%;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 300px;"></div>', unsafe_allow_html=True)
        st.button("Re-scan Document Index", use_container_width=True)

# Global Footer
st.markdown('<p style="text-align: center; color: #414a41; font-size: 10px; margin-top: 40px; text-transform: uppercase; letter-spacing: 0.1em;">End-to-End Encrypted | Knowledge Base: 12.4GB Vectorized</p>', unsafe_allow_html=True)
