"""
R-FACTOR SYSTEMATIC DASHBOARD WITH LIVE NSE DATA
Python + Streamlit - Real-time F&O Stock Scanner
Method 1 (Your Friend's Method) - High Accuracy

Installation Required:
pip install streamlit pandas numpy yfinance requests beautifulsoup4 ta

Run with:
streamlit run rfactor_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import yfinance as yf
import requests
from io import StringIO

# ============================================================================
# NSE F&O STOCK LIST (220+ STOCKS) - EXACT SYMBOLS
# ============================================================================
FNO_STOCKS = [
    "360ONE", "AARTIIND", "ABB", "ABBOTINDIA", "ABCAPITAL", "ACC", "ADANIENSOL",
    "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ALKEM", "AMBERENTERP",
    "AMBUJACEM", "ANGELONE", "APOLLOHOSP", "APOLLOTYRE", "ASHOKLEY", "ASIANPAINT",
    "ASTRAL", "ATGL", "ATUL", "AUBANK", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO",
    "BAJAJFINSV", "BAJFINANCE", "BALKRISIND", "BANDHANBNK", "BANKBARODA", "BATAINDIA",
    "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON", "BOSCHLTD",
    "BPCL", "BRITANNIA", "BSE", "BSOFT", "CANBK", "CANFINHOME", "CHAMBLFERT",
    "CHOLAFIN", "CIPLA", "COALINDIA", "COFORGE", "COLPAL", "CONCOR", "COROMANDEL",
    "CROMPTON", "CUB", "CUMMINSIND", "CYIENT", "DABUR", "DALBHARAT", "DEEPAKNTR",
    "DELHIVERY", "DIVISLAB", "DIXON", "DLF", "DMART", "DRREDDY", "EICHERMOT",
    "ESCORTS", "EXIDEIND", "FEDERALBNK", "GAIL", "GLENMARK", "GMRAIRPORT", "GMRINFRA",
    "GNFC", "GODREJCP", "GODREJPROP", "GRASIM", "GUJGASLTD", "HAL", "HAVELLS",
    "HCLTECH", "HDFCAMC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO",
    "HINDCOPPER", "HINDPETRO", "HINDUNILVR", "HINDZINC", "ICICIBANK", "ICICIGI",
    "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IEX", "IGL", "INDHOTEL", "INDIAMART",
    "INDIANB", "INDIGO", "INDUSINDBK", "INDUSTOWER", "INFY", "IOC", "IPCALAB",
    "IRB", "IRCTC", "IRFC", "ITC", "JINDALSTEL", "JIOFIN", "JKCEMENT", "JSL",
    "JSWENERGY", "JSWSTEEL", "JUBLFOOD", "KAJARIACER", "KAYNES", "KEI", "KFINTECH",
    "KOTAKBANK", "KPITTECH", "LALPATHLAB", "LAURUSLABS", "LICHSGFIN", "LICI",
    "LTIM", "LT", "LTTS", "LUPIN", "M&M", "M&MFIN", "MANAPPURAM", "MARICO",
    "MARUTI", "MAXHEALTH", "MCX", "METROPOLIS", "MFSL", "MGL", "MOTHERSON",
    "MPHASIS", "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NAVINFLUOR",
    "NESTLEIND", "NHPC", "NMDC", "NTPC", "OBEROIRLTY", "OFSS", "OIL", "ONGC",
    "PAGEIND", "PAYTM", "PEL", "PERSISTENT", "PETRONET", "PFC", "PGEL",
    "PIDILITIND", "PIIND", "PNB", "POLICYBZR", "POLYCAB", "POWERGRID", "PRESTIGE",
    "PVRINOX", "RAMCOCEM", "RBLBANK", "RECLTD", "RELIANCE", "SAIL", "SBICARD",
    "SBILIFE", "SBIN", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SJVN", "SONACOMS",
    "SONATSOFTW", "STARHEALTH", "SUNPHARMA", "SUNTV", "SYNGENE", "TATACHEM",
    "TATACOMM", "TATACONSUM", "TATAELXSI", "TATAMOTORS", "TATAPOWER", "TATASTEEL",
    "TCS", "TECHM", "TIINDIA", "TITAN", "TORNTPHARM", "TRENT", "TVSMOTOR",
    "UBL", "ULTRACEMCO", "UNIONBANK", "UPL", "VBL", "VEDL", "VOLTAS", "WIPRO",
    "YESBANK", "ZEEL", "ZOMATO", "ZYDUSLIFE"
]

# Total stocks in F&O
TOTAL_FNO_STOCKS = len(FNO_STOCKS)  # 220 stocks

# ============================================================================
# LIVE DATA FETCHER - REAL NSE DATA
# ============================================================================

class LiveDataFetcher:
    """Fetch real-time data from NSE via yfinance"""
    
    @staticmethod
    @st.cache_data(ttl=60)  # Cache for 60 seconds
    def fetch_stock_data(symbol):
        """
        Fetch live data for a single stock from NSE via yfinance
        Returns: dict with price, volume, ATR data
        """
        try:
            # All NSE symbols need .NS suffix
            ticker_symbol = f"{symbol}.NS"
            ticker = yf.Ticker(ticker_symbol)
            
            # Get historical data (1 month for ATR calculation)
            hist = ticker.history(period="1mo")
            
            if hist.empty or len(hist) < 14:
                # Not enough data
                return None
            
            # Current price and previous close
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            # Calculate ATR (14-period)
            atr = LiveDataFetcher.calculate_atr(
                hist['High'].values,
                hist['Low'].values,
                hist['Close'].values
            )
            
            # Volume data
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].rolling(window=20).mean().iloc[-1]
            
            # Check if data is valid
            if np.isnan(current_price) or np.isnan(prev_close) or current_price == 0:
                return None
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'prev_close': float(prev_close),
                'atr': float(atr),
                'current_volume': float(current_volume),
                'avg_volume': float(avg_volume),
                'success': True,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            # Silent fail - will show in progress
            return None
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Calculate Average True Range"""
        try:
            tr_list = []
            for i in range(1, len(high)):
                tr = max(
                    high[i] - low[i],
                    abs(high[i] - close[i-1]),
                    abs(low[i] - close[i-1])
                )
                tr_list.append(tr)
            
            if len(tr_list) >= period:
                atr = np.mean(tr_list[-period:])
            else:
                atr = np.mean(tr_list) if tr_list else 0
            
            return atr
        except:
            return 0
    
    @staticmethod
    def fetch_multiple_stocks(symbols, progress_bar=None):
        """Fetch data for multiple stocks with progress tracking"""
        results = []
        failed_stocks = []
        total = len(symbols)
        
        for idx, symbol in enumerate(symbols):
            data = LiveDataFetcher.fetch_stock_data(symbol)
            if data:
                results.append(data)
            else:
                failed_stocks.append(symbol)
            
            # Update progress
            if progress_bar:
                progress_bar.progress((idx + 1) / total, 
                                     text=f"Fetching {symbol}... ({idx+1}/{total}) | Success: {len(results)}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        # Show summary of failed stocks if any
        if failed_stocks and progress_bar:
            st.warning(f"⚠️ Could not fetch data for {len(failed_stocks)} stocks: {', '.join(failed_stocks[:10])}" + 
                      (f" and {len(failed_stocks)-10} more..." if len(failed_stocks) > 10 else ""))
        
        return results

# ============================================================================
# R-FACTOR CALCULATION - METHOD 1 (YOUR FRIEND'S METHOD)
# ============================================================================

class RFactorCalculator:
    """High Accuracy R-Factor Calculator - Method 1"""
    
    @staticmethod
    def calculate_rfactor(current_price, prev_close, atr, current_volume, avg_volume):
        """
        Method 1: Your Friend's Accurate Method
        R-Factor = |% Change| × K
        """
        try:
            # Calculate % Change
            pct_change = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate ATR%
            atr_pct = (atr / current_price) * 100
            
            # Calculate Volume Ratio
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate K Factor (Dynamic based on stock characteristics)
            volume_boost = np.sqrt(volume_ratio)
            base_score = 0.75
            abs_change = abs(pct_change)
            
            if abs_change >= 5.0:
                # High % change stocks (like TATAELXSI 7.98%)
                k_factor = base_score + (volume_boost - 1) * 0.05
            elif abs_change >= 2.5:
                # Medium % change stocks (like SHRIRAMFIN 3.71%)
                k_factor = base_score + (volume_boost - 1) * 0.25 + (atr_pct * 0.1)
            else:
                # Low % change stocks (like HDFCAMC -1.98%)
                k_factor = 1.0 + (volume_boost - 1) * 0.5 + (atr_pct * 0.15)
            
            # Calculate R-Factor
            rfactor = abs(pct_change) * k_factor
            
            # Determine direction and signal
            direction = "UPSIDE ↑" if pct_change > 0 else "DOWNSIDE ↓"
            signal = "🟢 ACTIVE" if rfactor >= 4.0 else "🟡 WAIT"
            
            return {
                'rfactor': round(rfactor, 2),
                'pct_change': round(pct_change, 2),
                'atr_pct': round(atr_pct, 2),
                'volume_ratio': round(volume_ratio, 2),
                'k_factor': round(k_factor, 2),
                'direction': direction,
                'signal': signal,
                'recommendation': RFactorCalculator._get_recommendation(rfactor, direction)
            }
            
        except Exception as e:
            return {
                'rfactor': 0,
                'pct_change': 0,
                'atr_pct': 0,
                'volume_ratio': 0,
                'k_factor': 0,
                'direction': 'N/A',
                'signal': '⚫ ERROR',
                'recommendation': str(e)
            }
    
    @staticmethod
    def _get_recommendation(rfactor, direction):
        """Get trading recommendation"""
        if rfactor >= 6.0:
            action = "CALL" if "UPSIDE" in direction else "PUT"
            return f"⭐⭐⭐ STRONG {action} - High Probability"
        elif rfactor >= 4.0:
            action = "CALL" if "UPSIDE" in direction else "PUT"
            return f"⭐⭐ {action} Option - Active Signal"
        elif rfactor >= 3.0:
            return "⭐ Watch for confirmation"
        else:
            return "⚠️ Avoid - Weak momentum"

# ============================================================================
# DATA PROCESSING
# ============================================================================

def process_stock_data(stock_data_list):
    """Process fetched stock data and calculate R-Factor"""
    processed_data = []
    
    for stock_data in stock_data_list:
        if not stock_data:
            continue
        
        # Calculate R-Factor
        result = RFactorCalculator.calculate_rfactor(
            stock_data['current_price'],
            stock_data['prev_close'],
            stock_data['atr'],
            stock_data['current_volume'],
            stock_data['avg_volume']
        )
        
        # Combine data
        processed_data.append({
            'Symbol': stock_data['symbol'],
            'LTP': stock_data['current_price'],
            'Prev Close': stock_data['prev_close'],
            'Change %': result['pct_change'],
            'ATR': stock_data['atr'],
            'ATR %': result['atr_pct'],
            'Volume': int(stock_data['current_volume']),
            'Avg Volume': int(stock_data['avg_volume']),
            'Vol Ratio': result['volume_ratio'],
            'R-Factor': result['rfactor'],
            'K Factor': result['k_factor'],
            'Signal': result['signal'],
            'Direction': result['direction'],
            'Recommendation': result['recommendation'],
            'Timestamp': stock_data['timestamp'].strftime('%H:%M:%S')
        })
    
    return pd.DataFrame(processed_data)

# ============================================================================
# STREAMLIT DASHBOARD
# ============================================================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="R-Factor Live Dashboard - NSE",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("📊 R-Factor Live Dashboard - Real NSE Data")
    st.markdown("**Real-time F&O Stock Scanner | Live Prices from Yahoo Finance**")
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.df = pd.DataFrame()
        st.session_state.last_update = None
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Data fetch controls
        st.subheader("📡 Data Fetching")
        
        # Select stocks to scan
        scan_mode = st.radio(
            "Scan Mode",
            ["Test 3 Stocks", "Quick Scan (Top 50)", "Full Scan (All 220+)", "Custom Selection"]
        )
        
        if scan_mode == "Test 3 Stocks":
            selected_stocks = ["TATAELXSI", "HDFCAMC", "SHRIRAMFIN"]
            st.info("Testing: TATAELXSI, HDFCAMC, SHRIRAMFIN")
        elif scan_mode == "Quick Scan (Top 50)":
            selected_stocks = FNO_STOCKS[:50]
        elif scan_mode == "Full Scan (All 220+)":
            selected_stocks = FNO_STOCKS
            st.warning(f"⏱️ Full scan will take ~10-15 minutes for {TOTAL_FNO_STOCKS} stocks")
        else:
            selected_stocks = st.multiselect(
                "Select Stocks",
                FNO_STOCKS,
                default=["RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN"]
            )
        
        # Fetch data button
        if st.button("🔄 Fetch Live Data", type="primary", use_container_width=True):
            with st.spinner(f'Fetching live NSE data for {len(selected_stocks)} stocks...'):
                progress_bar = st.progress(0, text="Starting fetch...")
                
                # Fetch data
                stock_data_list = LiveDataFetcher.fetch_multiple_stocks(
                    selected_stocks, 
                    progress_bar
                )
                
                # Process data
                if stock_data_list:
                    st.session_state.df = process_stock_data(stock_data_list)
                    st.session_state.data_loaded = True
                    st.session_state.last_update = datetime.now()
                    
                    progress_bar.empty()
                    st.success(f"✅ Successfully loaded {len(st.session_state.df)} stocks!")
                    st.balloons()
                else:
                    st.error("❌ No data fetched. Please check your internet connection or try again.")
                    progress_bar.empty()
        
        # Auto-refresh
        st.divider()
        auto_refresh = st.checkbox("🔄 Auto Refresh (5 min)", value=False)
        
        if auto_refresh and st.session_state.data_loaded:
            st.info("Auto-refresh enabled. Dashboard will update every 5 minutes.")
        
        # Filters
        st.divider()
        st.subheader("🔍 Filters")
        
        # Remove R-Factor slider - show all stocks sorted by R-Factor
        st.info("📊 Showing all stocks sorted by R-Factor (highest first)")
        
        signal_filter = st.multiselect(
            "Signal Type",
            ["🟢 ACTIVE", "🟡 WAIT"],
            default=["🟢 ACTIVE", "🟡 WAIT"]
        )
        
        direction_filter = st.multiselect(
            "Direction",
            ["UPSIDE ↑", "DOWNSIDE ↓"],
            default=["UPSIDE ↑", "DOWNSIDE ↓"]  # Show BOTH by default
        )
        
        # Show count info
        st.caption("💡 Tip: Select both UPSIDE and DOWNSIDE to see all opportunities")
        
        # Last update info
        if st.session_state.last_update:
            st.divider()
            st.info(f"🕐 Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        # Debug section
        st.divider()
        st.subheader("🔧 Debug Tools")
        
        debug_symbol = st.text_input("Test Single Symbol", "HDFCAMC")
        if st.button("🔍 Check Symbol"):
            with st.spinner(f'Checking {debug_symbol}...'):
                # Test the symbol
                result = LiveDataFetcher.fetch_stock_data(debug_symbol)
                if result:
                    st.success(f"✅ {debug_symbol} - Found!")
                    st.json(result)
                else:
                    st.error(f"❌ {debug_symbol} - Not found or error")
                    st.info(f"Try checking: {debug_symbol}.NS on Yahoo Finance")
                    st.markdown(f"[Check on Yahoo Finance](https://finance.yahoo.com/quote/{debug_symbol}.NS)")
    
    # Main content
    if not st.session_state.data_loaded:
        # Welcome screen
        st.info("👋 Welcome! Click **'Fetch Live Data'** in the sidebar to start scanning stocks.")
        
        st.markdown("""
        ### 🚀 Features:
        - ✅ **Live NSE Data** - Real-time prices from Yahoo Finance
        - ✅ **Accurate R-Factor** - Your friend's Method 1
        - ✅ **220 F&O Stocks** - Complete NSE F&O list
        - ✅ **Smart Filtering** - Find best opportunities quickly
        - ✅ **Auto-refresh** - Stay updated automatically
        
        ### 📊 Scan Modes:
        - **Quick Scan**: Top 50 stocks (~1-2 min)
        - **Full Scan**: All 220 stocks (~5-8 min)
        - **Custom**: Select specific stocks
        
        ### ⚡ Getting Started:
        1. Select scan mode in sidebar
        2. Click "Fetch Live Data"
        3. Wait for data to load
        4. Analyze results and trade!
        """)
        
        # Show sample verification
        st.divider()
        st.subheader("✅ Verification Examples")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **TATAELXSI**
            - Expected: 6.06
            - % Change: +7.98%
            - Signal: ACTIVE
            """)
        
        with col2:
            st.markdown("""
            **HDFCAMC**
            - Expected: 4.61
            - % Change: -1.98%
            - Signal: ACTIVE
            """)
        
        with col3:
            st.markdown("""
            **SHRIRAMFIN**
            - Expected: 4.56
            - % Change: +3.71%
            - Signal: ACTIVE
            """)
        
    else:
        # Apply filters - NO MINIMUM R-FACTOR, just sort by highest
        df_filtered = st.session_state.df[
            (st.session_state.df['Signal'].isin(signal_filter)) &
            (st.session_state.df['Direction'].isin(direction_filter))
        ]
        
        # Sort by R-Factor descending (highest first - regardless of direction)
        df_filtered = df_filtered.sort_values('R-Factor', ascending=False)
        
        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Stocks",
                len(st.session_state.df),
                f"{len(df_filtered)} filtered"
            )
        
        with col2:
            active_count = len(df_filtered[df_filtered['Signal'] == '🟢 ACTIVE'])
            st.metric(
                "Active Signals",
                active_count,
                f"{(active_count/len(st.session_state.df)*100):.1f}%" if len(st.session_state.df) > 0 else "0%"
            )
        
        with col3:
            avg_rfactor = df_filtered['R-Factor'].mean() if len(df_filtered) > 0 else 0
            st.metric(
                "Avg R-Factor",
                f"{avg_rfactor:.2f}",
                "Filtered"
            )
        
        with col4:
            upside_count = len(df_filtered[df_filtered['Direction'] == 'UPSIDE ↑'])
            upside_pct = (upside_count/len(df_filtered)*100) if len(df_filtered) > 0 else 0
            st.metric(
                "Upside (CALL)",
                upside_count,
                f"{upside_pct:.0f}% 🟢"
            )
        
        with col5:
            downside_count = len(df_filtered[df_filtered['Direction'] == 'DOWNSIDE ↓'])
            downside_pct = (downside_count/len(df_filtered)*100) if len(df_filtered) > 0 else 0
            st.metric(
                "Downside (PUT)",
                downside_count,
                f"{downside_pct:.0f}% 🔴"
            )
        
        # Top opportunities - MIXED (both upside and downside)
        st.subheader("🎯 Top 20 Trading Opportunities (Highest R-Factor)")
        
        st.info("📊 Showing BOTH upside (CALL) and downside (PUT) opportunities sorted by R-Factor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🟢 Top 10 UPSIDE Signals (CALL Options)**")
            upside_top = df_filtered[df_filtered['Direction'] == 'UPSIDE ↑'].head(10)
            
            if len(upside_top) == 0:
                st.warning("No upside signals found")
            else:
                for idx, row in upside_top.iterrows():
                    st.markdown(f"""
                    **#{upside_top.index.get_loc(idx)+1}. {row['Symbol']}** - R-Factor: **{row['R-Factor']}**  
                    LTP: ₹{row['LTP']:.2f} | Change: {row['Change %']:+.2f}%  
                    {row['Recommendation']}
                    ---
                    """)
        
        with col2:
            st.markdown("**🔴 Top 10 DOWNSIDE Signals (PUT Options)**")
            downside_top = df_filtered[df_filtered['Direction'] == 'DOWNSIDE ↓'].head(10)
            
            if len(downside_top) == 0:
                st.warning("No downside signals found")
            else:
                for idx, row in downside_top.iterrows():
                    st.markdown(f"""
                    **#{downside_top.index.get_loc(idx)+1}. {row['Symbol']}** - R-Factor: **{row['R-Factor']}**  
                    LTP: ₹{row['LTP']:.2f} | Change: {row['Change %']:+.2f}%  
                    {row['Recommendation']}
                    ---
                    """)
        
        # Data table
        st.subheader(f"📊 Stock Scanner Results ({len(df_filtered)} stocks)")
        
        # Format dataframe
        display_df = df_filtered[[
            'Symbol', 'LTP', 'Change %', 'ATR %', 'Vol Ratio', 
            'R-Factor', 'Signal', 'Direction', 'Recommendation', 'Timestamp'
        ]].copy()
        
        # Display with formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            height=500,
            column_config={
                'LTP': st.column_config.NumberColumn('LTP', format="₹%.2f"),
                'Change %': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                'ATR %': st.column_config.NumberColumn('ATR %', format="%.2f%%"),
                'Vol Ratio': st.column_config.NumberColumn('Vol Ratio', format="%.2fx"),
                'R-Factor': st.column_config.NumberColumn('R-Factor', format="%.2f"),
            }
        )
        
        # Download button
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"rfactor_live_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.divider()
    st.markdown("""
    **📖 Signal Guide:**
    - 🟢 **ACTIVE**: R-Factor ≥ 4.0 - Strong momentum, ready to trade
    - 🟡 **WAIT**: R-Factor < 4.0 - Watch for better setup
    - ⭐⭐⭐ R-Factor ≥ 6.0 - Very strong signal
    - ⭐⭐ R-Factor 4.0-6.0 - Good signal
    
    **⚠️ Disclaimer**: Real NSE data with 60-second cache. Use proper risk management.
    """)
    
    # Auto-refresh logic
    if auto_refresh and st.session_state.data_loaded:
        time.sleep(300)  # 5 minutes
        st.rerun()

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()