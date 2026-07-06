# Multi-Echelon Inventory Optimization Simulator

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)

A Python-based digital twin that simulates a multi-echelon supply chain (Supplier → Distribution Center → Regional Warehouse → Retail Store). This project uses discrete-event simulation (**SimPy**) to model stochastic demand and lead times, and applies heuristic optimization to find the optimal `(s, S)` inventory policies that minimize total supply chain costs while mitigating the **Bullwhip Effect**.

## Features
- **Discrete-Event Simulation**: Built with SimPy to model daily operations, order processing, and random shipping delays across multiple echelons.
- **Stochastic Modeling**: Uses Poisson distributions to accurately model daily retail foot-traffic/demand, and Normal distributions to model logistics transit times.
- **Lost Sales Policy**: Accurately models the financial penalty of unmet demand in fashion/retail contexts.
- **AI/Heuristic Optimization**: Implements a Randomized Grid Search to navigate the complex stochastic parameter space and find optimal Reorder Points `(s)` and Order-Up-To Levels `(S)`.
- **Interactive Dashboards**: Uses Plotly to generate interactive HTML visualizations comparing Baseline vs. Optimized policies across Total Costs, Inventory Levels, and Order Variances (Bullwhip Effect).

## Tech Stack
- **Simulation**: `simpy`
- **Data Manipulation**: `numpy`, `pandas`, `scipy`
- **Visualization**: `plotly`
- **Logging**: Python `logging`

## How to Run

1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main simulation script:
   ```bash
   python main.py
   ```
4. Open the generated HTML files in any web browser to view the interactive dashboards:
   - `cost_comparison.html`
   - `bullwhip_effect.html`
   - `inventory_levels.html`

## The Bullwhip Effect & Optimization
In unoptimized supply chains, small fluctuations in retail demand cause massive, chaotic order spikes upstream at the factory level (The Bullwhip Effect). By algorithmically tuning the `(s, S)` policies at each node, this simulator demonstrates how to dampen order variance by acting as a shock-absorber, saving significant capital in holding costs and stockout penalties.
