import numpy as np
import logging
from simulator import run_simulation
from logger import sim_logger

def calculate_total_cost(nodes):
    total_cost = 0
    total_holding = 0
    total_ordering = 0
    total_stockout = 0
    
    for node in nodes:
        total_holding += node.holding_cost
        total_ordering += node.ordering_cost
        total_stockout += node.stockout_cost
        
    total_cost = total_holding + total_ordering + total_stockout
    return total_cost, total_holding, total_ordering, total_stockout

def optimize_policy(demand_mean=20, days=180, iterations=100):
    """
    Uses Randomized Search to explore the stochastic search space and find
    a good heuristic policy for (s, S) across the multi-echelon system.
    """
    # Suppress standard logs during simulation to avoid console spam
    sim_logger.setLevel(logging.CRITICAL)
    
    best_cost = float('inf')
    best_policy = None
    
    print(f"Starting optimization (Random Search, {iterations} iterations)...")
    
    # We use a fixed evaluation seed for each iteration so the demand/leadtime noise 
    # doesn't completely overwhelm the policy differences, but ideally we'd evaluate 
    # each policy on multiple seeds. For speed, we just use one seed per policy.
    for i in range(iterations):
        # Generate random plausible (s, S) policies
        # Store: s in [10, 100], S in [s+10, 200]
        s_store = np.random.randint(10, 100)
        S_store = np.random.randint(s_store + 10, 200)
        
        # Warehouse: s in [50, 200], S in [s+50, 500]
        s_warehouse = np.random.randint(50, 200)
        S_warehouse = np.random.randint(s_warehouse + 50, 500)
        
        # DC: s in [100, 400], S in [s+100, 1000]
        s_dc = np.random.randint(100, 400)
        S_dc = np.random.randint(s_dc + 100, 1000)
        
        policy = {
            "Retail Store": (s_store, S_store),
            "Regional Warehouse": (s_warehouse, S_warehouse),
            "Distribution Center": (s_dc, S_dc)
        }
        
        nodes = run_simulation(days=days, demand_mean=demand_mean, policies=policy, seed=42)
        cost, _, _, _ = calculate_total_cost(nodes)
        
        if cost < best_cost:
            best_cost = cost
            best_policy = policy
            
    # Restore log level
    sim_logger.setLevel(logging.INFO)
    print(f"Optimization complete. Best Simulated Cost (over {days} days): ${best_cost:.2f}")
    return best_policy
