import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ClickOptions - Growth & Conversion Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- API CONFIGURATION ---
TOKEN = "comon_live_rmJGEmHcu5UpdyTv6VEt4hva8MaZ-UqUqE29Ep_Eznc"
BASE_URL = "https://monitor-api.clickoptions.xyz/api/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "accept": "application/json"
}

# --- DATA FETCHING UTILITIES (From Jupyter Notebook) ---
@st.cache_data(ttl=300)  # 5-minute cache to respect working principles of reliability and efficiency
def fetch_api_data(endpoint, params=None):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching data from endpoint /{endpoint}: {e}")
        return None

# Pre-fetching all required data payloads
kpis_data = fetch_api_data("kpis", params={"filter": "all"})
analytics_data = fetch_api_data("analytics")
funnel_report_data = fetch_api_data("funnel-report")
charts_data = fetch_api_data("charts", params={"filter": "all", "limit": 5})
prices_data = fetch_api_data("prices", params={"filter": "all", "limit": 5})

# --- HEADER SECTION ---
st.title("📊 ClickOptions | Growth & Conversion Dashboard")
st.caption(f"Last updated on : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# --- NAVIGATION VIA TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Overview & Weekly KPIs", 
    "🌪️ Conversion Funnel Analysis", 
    "📣 Acquisition & KOL Performance", 
    "🎯 Product Usage & Asset Trends",
    "⚠️ Data Map & Tracking Gaps Diagnostic"
])

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW & WEEKLY KPIS
# ==========================================
with tab1:
    st.header("⚡ Core Performance Metrics (Leadership Set)")
    st.subheader("Weekly Strategic Indicators for Rapid Decision-Making")
    
    if kpis_data and funnel_report_data:
        # Layout metrics based on Executive Overview and Suggested KPI requirements
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total User Base", f"{kpis_data.get('totalUsers', 0):,}")
            st.metric("New Users (Today)", f"+{kpis_data.get('usersToday', 0)}")
        with col2:
            st.metric("Total Deposits Volume", f"${kpis_data.get('totalDepositsUsd', 0.0):,.2f}")
            st.metric("Deposits (Today)", f"${kpis_data.get('depositsTodayUsd', 0.0):,.2f}")
        with col3:
            st.metric("Total Withdrawals", f"${kpis_data.get('totalWithdrawalsUsd', 0.0):,.2f}")
            st.metric("Live Trading Vol (Today)", f"${kpis_data.get('realTradeVolumeTodayUsd', 0.0):,.2f}")
        with col4:
            st.metric("Open Live Positions", f"{kpis_data.get('openPositionsRealCount', 0)}")
            st.metric("Total Real Premium Volume", f"${kpis_data.get('totalRealPremiumUsd', 0.0):,.2f}")
            
        st.markdown("---")
        
        # Display analysis window timeframes 
        from_date = pd.to_datetime(funnel_report_data.get("fromMs"), unit='ms')
        to_date = pd.to_datetime(funnel_report_data.get("toMs"), unit='ms')
        st.info(f"📅 **Current Report Analysis Window:** From {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display global conversion platform milestones
        totals = funnel_report_data.get("totals", {})
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.metric("Unique Visitors", f"{totals.get('visitors', 0):,}")
        col_m2.metric("Signups", f"{totals.get('signups', 0):,}")
        col_m3.metric("KYC Passed", f"{totals.get('kycPassed', 0):,}")
        col_m4.metric("Depositors", f"{totals.get('deposited', 0):,}")
        col_m5.metric("Active Live Traders", f"{totals.get('realTraded', 0):,}")
    else:
        st.warning("Unable to fetch executive metrics from live production APIs.")

# ==========================================
# TAB 2: CONVERSION FUNNEL ANALYSIS
# ==========================================
with tab2:
    st.header("🌪️ User Journey Funnel & Drop-off Isolation")
    
    if analytics_data and "funnel" in analytics_data:
        stages = analytics_data["funnel"]["stages"]
        df_funnel = pd.DataFrame(stages)
        
        # Calculate rates dynamically based on assignment requirements
        df_funnel['Global Conv Rate (%)'] = (df_funnel['count'] / df_funnel['count'].iloc[0] * 100).round(2)
        df_funnel['Drop vs Previous Stage (%)'] = (df_funnel['count'].pct_change() * 100).round(2).fillna(0)
        
        # Plotly Funnel Chart
        fig = px.funnel(
            df_funnel, 
            x='count', 
            y='name', 
            title="Platform Interactive Conversion Funnel Flow",
            labels={'count': 'User Count', 'name': 'Funnel Stage'},
            color_discrete_sequence=['#1E3A8A']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table for detailed inspection
        st.subheader("Funnel Analytical Performance Ledger")
        st.dataframe(df_funnel, use_container_width=True, hide_index=True)
        
        # Automatic drop-off diagnostic note
        st.subheader("🚨 Automated Funnel Drop-off Identification")
        worst_drop = df_funnel.sort_values(by='Drop vs Previous Stage (%)').iloc[0]
        st.error(
            f"**The main friction point in the user flow occurs at the stage: '{worst_drop['name']}'** "
            f"with a drop of **{worst_drop['Drop vs Previous Stage (%)']}%** relative to its prior checkpoint. "
            f"Product development and customer onboarding priority flags should target this specific lifecycle block."
        )
    else:
        st.warning("Funnel analytical data structures are unavailable at this moment.")

# ==========================================
# TAB 3: ACQUISITION & KOL PERFORMANCE
# ==========================================
with tab3:
    st.header("📣 Traffic Channel Attribution & Affiliate Matrix")
    
    left_pane, right_pane = st.columns(2)
    
    with left_pane:
        st.subheader("🌐 Acquisition Channels Matrix")
        if funnel_report_data and "rows" in funnel_report_data:
            df_channels = pd.DataFrame(funnel_report_data["rows"])
            df_channels = df_channels.sort_values(by="signups", ascending=False)
            st.dataframe(df_channels, use_container_width=True, hide_index=True)
            
            fig_channels = px.bar(
                df_channels.head(10), x='source', y='signups', 
                title="Top 10 Channels by Total Reg. Signups",
                labels={'signups': 'Total Registrations', 'source': 'Attributed Channel'},
                color_discrete_sequence=['#10B981']
            )
            st.plotly_chart(fig_channels, use_container_width=True)
        else:
            st.info("No recorded channel traffic data logs returned.")
            
    with right_pane:
        st.subheader("👥 KOL & Affiliate Performance (Anonymized Codes)")
        if funnel_report_data and "affiliates" in funnel_report_data:
            df_affiliates = pd.DataFrame(funnel_report_data["affiliates"])
            df_affiliates = df_affiliates.sort_values(by="signups", ascending=False)
            st.dataframe(df_affiliates, use_container_width=True, hide_index=True)
            
            fig_aff = px.bar(
                df_affiliates.head(10), x='source', y='signups', 
                title="Top 10 Affiliates by Signups Generated",
                labels={'signups': 'Signups Count', 'source': 'Affiliate Code ID'},
                color_discrete_sequence=['#F59E0B']
            )
            st.plotly_chart(fig_aff, use_container_width=True)
        else:
            st.info("No partner or influencer affiliate rows returned.")

# ==========================================
# TAB 4: PRODUCT USAGE & ASSET TRENDS
# ==========================================
with tab4:
    st.header("🎯 Trading Behaviors & Market Activity")
    
    sub_col1, sub_col2 = st.columns([1, 2])
    
    with sub_col1:
        st.subheader("🔥 Most Traded Assets (Real Volume)")
        if analytics_data and "topSymbols" in analytics_data:
            df_symbols = pd.DataFrame(analytics_data["topSymbols"]["real"])
            st.dataframe(df_symbols, use_container_width=True, hide_index=True)
        else:
            st.info("Asset tracking metrics are empty or offline.")
            
        st.subheader("⚡ Real-time Live Price Ticker")
        if prices_data and "prices" in prices_data:
            df_prices = pd.DataFrame(prices_data["prices"])
            if "timestamp" in df_prices.columns:
                df_prices["timestamp"] = pd.to_datetime(df_prices["timestamp"], unit='ms')
            st.dataframe(df_prices, use_container_width=True, hide_index=True)
        else:
            st.info("Live currency price feeds are missing.")
            
    with sub_col2:
        st.subheader("📈 Daily Active Users (DAU) Series Ticker")
        if charts_data and "usersByDay" in charts_data:
            df_users_daily = pd.DataFrame(charts_data["usersByDay"])
            df_users_daily["date"] = pd.to_datetime(df_users_daily["date"])
            
            fig_line = px.line(
                df_users_daily, x='date', y='value', 
                title=f"Unique Platform DAU Trend (Window Range: {charts_data.get('range', '7d')})",
                labels={'value': 'Daily Active Users', 'date': 'Calendar Date'},
                markers=True
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("DAU chart tracking series data structure is currently empty.")

# ==========================================
# TAB 5: DATA MAP & TRACKING GAPS DIAGNOSTIC
# ==========================================
with tab5:
    st.header("📋 Requirement Compliance Map & Strategic Tracking Gaps List")
    
    # 1. Data Source Mapping & Audit (Addressing Deliverable 1 & 3)
    st.subheader("🔍 1. Live Data Availability Map Audit Log")
    
    status_matrix = {
        "Metric Segment / Data Requirement": [
            "Platform Funnel & Conversions Flow", 
            "Trading Volumes & Account Metrics (KPIs)", 
            "Web Traffic Attribution (UTM / Sources)", 
            "Partner / Affiliate Tracking Matrix", 
            "Community Scale & Activity (Telegram, Discord)", 
            "Social Content Metrics (X, YouTube, LinkedIn)",
            "Paid Ad Network Campaign Spend"
        ],
        "Tracking Status": [
            "✅ ACTIVE (Direct REST Endpoint)", 
            "✅ ACTIVE (Direct REST Endpoint)", 
            "✅ ACTIVE (Direct REST Endpoint)", 
            "✅ ACTIVE (Direct REST Endpoint)", 
            "❌ CRITICAL DATA GAP (Missing)", 
            "❌ CRITICAL DATA GAP (Missing)", 
            "⚠️ AT RISK / UNAVAILABLE"
        ],
        "Source Endpoint Linkage": [
            "REST API: /analytics & /funnel-report", 
            "REST API: /kpis & /prices", 
            "REST API: /funnel-report (rows payload)", 
            "REST API: /funnel-report (affiliates payload)", 
            "No endpoints provided by current Backend Platform", 
            "No endpoints provided by current Backend Platform", 
            "Excluded from corporate V1 API scope schemas"
        ],
        "Remediation Action Required": [
            "None. Fully structural.", 
            "None. Fully structural.", 
            "Ensure consistency in source parameter labels.", 
            "Cross-validate ID mapping against Airtable CRM entries.", 
            "Deploy manual community bot exports or routine file drops.", 
            "Incorporate periodic manual CSV upload modules for marketing.", 
            "Introduce spreadsheet entry forms for CAC/spend tracking."
        ]
    }
    df_status = pd.DataFrame(status_matrix)
    st.table(df_status)
    
    st.markdown("---")
    
    # 2. Executive Cadrage Diagnosis Note (Addressing Deliverable 4 & Working Principles)
    st.subheader("💡 2. Strategic Launch Note & Initial Diagnosis Report")
    st.markdown(
        """
        * **Attribution Observations:** Acquisition source details and anonymous affiliate parameters map natively across downstream registration loops. However, major web networks (Facebook, Meta, Instagram) reveal a critical drop-off: they capture initial registrations but reflect **0 total active deposits** inside this logging frame. Organic/Direct referrals remain the absolute primary drivers for retention, qualified funds, and continuous production volume.
        * **Critical Blockers Note:** As flagged in the *Live Data Availability Map* above, community platform engagement metrics (Telegram/Discord user volume counts) and social media impressions (X, YouTube) requested on page 1 of the brief are entirely absent from the internal telemetry network endpoints.
        * **Operational Recommandation:** In line with our core working principle to prioritize rapid clear delivery over perfection, this dashboard remains entirely functional on structured database fields. For the next weekly steering meeting, manual social media CSV file inputs should be processed alongside this system to patch external engagement gaps without delaying leadership evaluations.
        """
    )
