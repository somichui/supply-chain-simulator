import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def generate_dashboards(baseline_nodes, optimized_nodes, chart_height=800):
    """
    Generates and returns Plotly figure objects for the Streamlit App.
    """
    b_dc, b_warehouse, b_store = baseline_nodes
    o_dc, o_warehouse, o_store = optimized_nodes
    
    # --- 1. Cost Comparison ---
    b_cost = sum(n.holding_cost + n.ordering_cost + n.stockout_cost for n in baseline_nodes)
    b_holding = sum(n.holding_cost for n in baseline_nodes)
    b_stockout = sum(n.stockout_cost for n in baseline_nodes)
    
    o_cost = sum(n.holding_cost + n.ordering_cost + n.stockout_cost for n in optimized_nodes)
    o_holding = sum(n.holding_cost for n in optimized_nodes)
    o_stockout = sum(n.stockout_cost for n in optimized_nodes)
    
    fig_cost = go.Figure(data=[
        go.Bar(name='Total Cost', x=['Baseline', 'Optimized'], y=[b_cost, o_cost]),
        go.Bar(name='Holding', x=['Baseline', 'Optimized'], y=[b_holding, o_holding]),
        go.Bar(name='Stockout', x=['Baseline', 'Optimized'], y=[b_stockout, o_stockout])
    ])
    fig_cost.update_layout(barmode='group', title='Cost Comparison: Baseline vs Optimized', template='plotly_dark')
    
    # --- 2. Bullwhip Effect (Variance of orders at each tier) ---
    b_variances = [
        np.var(b_store.customer_demand),
        np.var(b_store.orders_placed),
        np.var(b_warehouse.orders_placed),
        np.var(b_dc.orders_placed)
    ]
    
    o_variances = [
        np.var(o_store.customer_demand),
        np.var(o_store.orders_placed),
        np.var(o_warehouse.orders_placed),
        np.var(o_dc.orders_placed)
    ]
    
    stages = ['Customer Demand', 'Store Orders', 'Warehouse Orders', 'DC Orders']
    
    fig_bullwhip = go.Figure()
    fig_bullwhip.add_trace(go.Scatter(x=stages, y=b_variances, mode='lines+markers', name='Baseline Variance', 
                                      line=dict(color='red', width=3), marker=dict(size=10)))
    fig_bullwhip.add_trace(go.Scatter(x=stages, y=o_variances, mode='lines+markers', name='Optimized Variance', 
                                      line=dict(color='green', width=3), marker=dict(size=10)))
    fig_bullwhip.update_layout(title='Bullwhip Effect: Order Variance across Echelons',
                               yaxis_title='Variance of Order Quantity',
                               template='plotly_dark')
    
    # --- 3. Inventory Levels Over Time ---
    fig_inv = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            subplot_titles=("Distribution Center Inventory", "Warehouse Inventory", "Store Inventory"))
    
    # Baseline traces
    fig_inv.add_trace(go.Scatter(y=[h['inventory'] for h in b_dc.history], mode='lines', name='Baseline DC', line=dict(color='lightcoral')), row=1, col=1)
    fig_inv.add_trace(go.Scatter(y=[h['inventory'] for h in b_warehouse.history], mode='lines', name='Baseline WH', line=dict(color='lightcoral')), row=2, col=1)
    fig_inv.add_trace(go.Scatter(y=[h['inventory'] for h in b_store.history], mode='lines', name='Baseline Store', line=dict(color='lightcoral')), row=3, col=1)
    
    # Optimized traces
    fig_inv.add_trace(go.Scatter(y=[h['inventory'] for h in o_dc.history], mode='lines', name='Optimized DC', line=dict(color='lightgreen')), row=1, col=1)
    fig_inv.add_trace(go.Scatter(y=[h['inventory'] for h in o_warehouse.history], mode='lines', name='Optimized WH', line=dict(color='lightgreen')), row=2, col=1)
    fig_inv.add_trace(go.Scatter(y=[h['inventory'] for h in o_store.history], mode='lines', name='Optimized Store', line=dict(color='lightgreen')), row=3, col=1)
    
    fig_inv.update_layout(height=800, title_text="Inventory Levels Over Time", template='plotly_dark')
    fig_inv.update_xaxes(rangeslider_visible=True, row=3, col=1) # Adds a horizontal slider to the bottom chart that controls all 3
    
    return fig_cost, fig_bullwhip, fig_inv
