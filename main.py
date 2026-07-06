import logging
from simulator import run_simulation
from optimizer import optimize_policy
from visualizer import generate_dashboards
from logger import sim_logger

def main():
    print("=== Multi-Echelon Supply Chain Simulator ===")
    
    # 1. Run Baseline
    print("\nRunning Baseline Simulation (Default s, S policies)...")
    baseline_policies = {
        "Retail Store": (50, 150),
        "Regional Warehouse": (150, 400),
        "Distribution Center": (400, 1000)
    }
    # Using fixed seed for reproducibility across baseline/optimized run
    baseline_nodes = run_simulation(days=365, demand_mean=20, policies=baseline_policies, seed=100)
    
    # 2. Optimize Policy
    print("\nOptimizing Policies to minimize costs and dampen Bullwhip Effect...")
    # Reduce iterations for faster runs, increase for better optimization
    best_policy = optimize_policy(demand_mean=20, days=365, iterations=100)
    print("\nFound Optimal Policy:")
    for node, (s, S) in best_policy.items():
        print(f"  - {node}: s={s}, S={S}")
        
    # 3. Run Optimized
    print("\nRunning Optimized Simulation...")
    optimized_nodes = run_simulation(days=365, demand_mean=20, policies=best_policy, seed=100)
    
    # 4. Generate Visualizations
    print("\nGenerating Dashboards...")
    generate_dashboards(baseline_nodes, optimized_nodes)
    
    print("\nComplete! Open the generated HTML files in your browser.")

if __name__ == "__main__":
    main()
