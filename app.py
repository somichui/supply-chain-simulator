import streamlit as st
import numpy as np
from simulator import run_simulation
from optimizer import optimize_policy
from visualizer import generate_dashboards
from ml_forecaster import forecaster

st.set_page_config(page_title="Supply Chain Sandbox v2.0", layout="wide")

# Hide the default Streamlit Deploy button and menu for a cleaner UI
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("Multi-Echelon Supply Chain Simulator v2.0")
st.markdown("Stress test an AI-optimized supply chain against **Black Swan Shocks** and **Machine Learning Demand Forecasting**.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("Simulation Controls")

demand_mean = st.sidebar.slider("Avg Daily Customer Demand", min_value=5, max_value=100, value=20)
days = st.sidebar.slider("Simulation Days", min_value=30, max_value=365, value=365)

st.sidebar.header("Black Swan Shocks")
enable_port_strike = st.sidebar.checkbox("Inject Port Strike (DC Delay)", help="A Black Swan event. Shipments heading to the Distribution Center are massively delayed. Watch the safety stock collapse under stress!")
if enable_port_strike:
    strike_start = st.sidebar.slider("Strike Start Day", 1, days, 150)
    strike_delay = st.sidebar.slider("Delay Penalty (Days)", 1, 60, 20)
    st.sidebar.warning(f"Strike hits on Day {strike_start} (lasts 30 days) and delays DC shipments by {strike_delay} days!")
    shock_event = {"type": "Port Strike", "start": strike_start, "delay": strike_delay}
else:
    shock_event = None

st.sidebar.header("Chart Dimensions")
chart_height = st.sidebar.slider("Inventory Chart Height", min_value=400, max_value=2500, value=800, step=100)
chart_width = st.sidebar.slider("Chart Width (px)", min_value=600, max_value=2500, value=1200, step=100)
use_auto_width = st.sidebar.checkbox("Auto-Fit Width to Screen", value=True)

st.sidebar.header("Machine Learning")
enable_ml = st.sidebar.checkbox("Enable ML Forecaster (Store Level)", help="Uses a Machine Learning model (Random Forest) trained on 2 years of synthetic historical data to predict daily demand. The Store will dynamically adjust its Reorder Point (s) and Order-Up-To Level (S) based on the AI's prediction of weekly seasonality!")
if enable_ml:
    st.sidebar.success("Random Forest will dynamically adjust Retail Store's (s, S) policy based on predicted weekly seasonality.")

if st.sidebar.button("Run Simulation", type="primary"):
    with st.spinner("Training ML Models and Running Optimizer..."):
        
        # 1. Handle ML Training
        if enable_ml and not forecaster.is_trained:
            forecaster.demand_mean = demand_mean
            forecaster.train()

        # 2. Run Baseline (Naive policies)
        baseline_policies = {
            "Retail Store": (50, 150),
            "Regional Warehouse": (150, 400),
            "Distribution Center": (400, 1000)
        }
        baseline_nodes = run_simulation(days=days, demand_mean=demand_mean, policies=baseline_policies, 
                                        seed=100, use_ml=False, shock_event=shock_event)
        
        # 3. Optimization Phase
        st.toast("Optimizing policies via randomized search...")
        # Reduce iterations for web app speed
        best_policy = optimize_policy(demand_mean=demand_mean, days=days, iterations=30)
        
        st.success("Optimization Complete!")
        st.json(best_policy)

        # 4. Run Optimized
        optimized_nodes = run_simulation(days=days, demand_mean=demand_mean, policies=best_policy, 
                                         seed=100, use_ml=enable_ml, shock_event=shock_event)
        
        # 5. Generate and Display Visuals
        fig_cost, fig_bullwhip, fig_inv = generate_dashboards(baseline_nodes, optimized_nodes, chart_height)
        
        # Apply manual width if auto-fit is disabled
        if not use_auto_width:
            fig_cost.update_layout(width=chart_width/2)
            fig_bullwhip.update_layout(width=chart_width/2)
            fig_inv.update_layout(width=chart_width)
            
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_cost, use_container_width=use_auto_width)
        with col2:
            st.plotly_chart(fig_bullwhip, use_container_width=use_auto_width)
            
        st.plotly_chart(fig_inv, use_container_width=use_auto_width)
