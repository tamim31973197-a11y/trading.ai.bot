import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import secrets
import string
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="AI Terminal & Admin Hub", layout="wide")

st.markdown("""
<style>
    .main { background-color: #090c10; color: #f0f6fc; }
    .stMetric { background: rgba(22, 27, 34, 0.8); border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 12px; }
    .warning-box { background: rgba(245, 158, 11, 0.2); border: 2px solid #f59e0b; padding: 15px; border-radius: 12px; font-weight: bold; color: #fbbf24; text-align: center; }
    .signal-buy { background: rgba(16, 185, 129, 0.2); border: 2px solid #10b981; padding: 20px; border-radius: 15px; text-align: center; }
    .signal-sell { background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; padding: 20px; border-radius: 15px; text-align: center; }
    .signal-wait { background: rgba(107, 114, 128, 0.2); border: 2px solid #6b7280; padding: 20px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=3000, key="data_refresh")

if 'master_passkey' not in st.session_state:
    st.session_state.master_passkey = "hayati2008"

if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "VIP-PASS-101": {"name": "Pro Trader", "device_locked": None, "role": "VIP Member", "access": ["Live Signals", "Charts", "1m Warning Alert"]}
    }

st.sidebar.title("🔐 ACCESS NAVIGATION")
app_mode = st.sidebar.radio("Go to Section:", ["📈 Live AI Trading Terminal", "🛡️ Master Admin Panel"])

if app_mode == "🛡️ Master Admin Panel":
    st.title("🛡️ MASTER ADMIN CONTROL CENTER")
    admin_input = st.text_input("Enter Master Admin Passkey:", type="password")

    if admin_input == st.session_state.master_passkey:
        st.success("✅ Access Granted: Master Admin")
        st.divider()

        tab1, tab2 = st.tabs(["🔑 Passkey Generator", "👥 Active Members"])

        with tab1:
            st.subheader("Generate Passkeys")
            custom_key = st.text_input("Create Custom Passkey:", placeholder="e.g. VIP-MEMBER-007")
            if st.button("➕ Create Passkey"):
                if custom_key and custom_key not in st.session_state.user_db:
                    st.session_state.user_db[custom_key] = {
                        "name": "Custom User", "device_locked": None,
                        "role": "Member", "access": ["Live Signals", "1m Warning Alert"]
                    }
                    st.success(f"Passkey '{custom_key}' created!")

        with tab2:
            st.subheader("Active Members Database")
            st.dataframe(pd.DataFrame(st.session_state.user_db).T, use_container_width=True)

    elif admin_input != "":
        st.error("Incorrect Admin Passkey.")

else:
    st.title("⚡ AI ADVANCED QUANTUM TERMINAL v6.0")
    user_pass = st.sidebar.text_input("🔑 Enter Passkey:", type="password")
    
    authenticated = False
    if user_pass in st.session_state.user_db or user_pass == st.session_state.master_passkey:
        authenticated = True
        st.sidebar.success("Access Granted")

    if authenticated:
        c1, c2 = st.columns(2)
        with c1: symbol = st.selectbox("Select Asset:", ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD", "GC=F"])
        with c2: timeframe = st.selectbox("Timeframe:", ["1m", "5m", "15m"])

        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval=timeframe)

        if not df.empty and len(df) > 15:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))

            price = float(df['Close'].iloc[-1])
            rsi = float(df['RSI'].iloc[-1])
            
            now = datetime.datetime.now()
            next_candle = (now + datetime.timedelta(minutes=1)).strftime("%H:%M")

            decision = "🟢 CALL / BUY" if rsi < 35 else ("🔴 PUT / SELL" if rsi > 65 else "⚪ WAIT / NEUTRAL")
            card_style = "signal-buy" if rsi < 35 else ("signal-sell" if rsi > 65 else "signal-wait")

            st.markdown(f'<div class="warning-box">⚠️ Target Candle Time: <b>{next_candle}</b></div>', unsafe_allow_html=True)
            st.write("")

            col_sig, col_m1, col_m2 = st.columns([2, 1, 1])
            with col_sig:
                st.markdown(f'<div class="{card_style}"><h2>{decision}</h2></div>', unsafe_allow_html=True)
            with col_m1: st.metric("Live Price", f"${price:.4f}")
            with col_m2: st.metric("RSI Level", f"{rsi:.1f}")

            st.divider()
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
