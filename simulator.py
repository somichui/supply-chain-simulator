import simpy
import numpy as np
import pandas as pd
from logger import sim_logger
from ml_forecaster import forecaster

# Cost weights
HOLDING_COST = 0.10
ORDERING_COST = 50.0
STOCKOUT_COST = 25.0

class SupplyChainNode:
    def __init__(self, env, name, upstream, s, S, lead_time_mean, lead_time_std, is_supplier=False, use_ml=False):
        self.env = env
        self.name = name
        self.upstream = upstream
        
        self.s = s
        self.S = S
        self.lead_time_mean = lead_time_mean
        self.lead_time_std = lead_time_std
        self.is_supplier = is_supplier
        self.use_ml = use_ml
        self.shock_event = None # Can be injected
        
        self.inventory = S if not is_supplier else 999999
        self.on_order = 0
        
        # Metrics
        self.holding_cost = 0.0
        self.ordering_cost = 0.0
        self.stockout_cost = 0.0
        self.total_demand_received = 0
        self.total_shortage = 0
        
        # Daily history for visualization and Bullwhip effect
        self.history = []
        self.orders_placed = [] 
        
        if not self.is_supplier:
            self.env.process(self.daily_review())
            
    def daily_review(self):
        while True:
            # If ML is enabled and this is the Store, dynamically adjust s and S
            if self.use_ml and self.name == "Retail Store":
                predicted_demand = forecaster.predict(self.env.now)
                # Dynamic policy based on predicted demand (e.g., 2 days safety, 6 days order-up-to)
                self.s = predicted_demand * 2
                self.S = predicted_demand * 6

            # 1. Holding cost calculation
            self.holding_cost += self.inventory * HOLDING_COST
            
            # 2. Check inventory policy (s, S)
            inventory_position = self.inventory + self.on_order
            if inventory_position <= self.s:
                order_qty = max(0, self.S - inventory_position)
                if order_qty > 0:
                    self.place_order(order_qty)
            else:
                self.orders_placed.append(0)
                    
            # 3. Log daily state
            self.history.append({
                'day': self.env.now,
                'name': self.name,
                'inventory': self.inventory,
                'on_order': self.on_order,
                'holding_cost': self.holding_cost,
                'ordering_cost': self.ordering_cost,
                'stockout_cost': self.stockout_cost,
                'order_qty': self.orders_placed[-1] if self.orders_placed else 0,
                's': self.s,
                'S': self.S
            })
            
            yield self.env.timeout(1)
            
    def place_order(self, qty):
        self.on_order += qty
        self.ordering_cost += ORDERING_COST
        self.orders_placed.append(qty)
        
        sim_logger.info(f"Day {self.env.now}: {self.name} ordered {qty} units from {self.upstream.name if self.upstream else 'External'}.")
        
        if self.upstream:
            self.upstream.receive_demand(qty, self)
            
    def receive_demand(self, qty, downstream_node=None):
        if self.is_supplier:
            shipped = qty
        else:
            self.total_demand_received += qty
            if self.inventory >= qty:
                self.inventory -= qty
                shipped = qty
            else:
                shipped = self.inventory
                shortage = qty - self.inventory
                self.inventory = 0
                
                # Lost Sales Rule
                self.stockout_cost += shortage * STOCKOUT_COST
                self.total_shortage += shortage
                sim_logger.warning(f"Day {self.env.now}: {self.name} stockout! Shortage of {shortage} units (Lost Sales).")
                
                # CRITICAL BUG FIX: If an internal warehouse runs out of stock and loses the sale, 
                # we MUST tell the downstream node (who placed the order) that the items are not coming.
                # Otherwise, their `on_order` variable gets permanently bloated with ghost orders, 
                # and they stop ordering forever (flatlining the simulation).
                if downstream_node:
                    downstream_node.on_order -= shortage
            
        if downstream_node and shipped > 0:
            downstream_node.env.process(downstream_node.shipment_arrival(shipped))

    def shipment_arrival(self, qty):
        # Calculate random lead time
        lead_time = max(1, int(np.round(np.random.normal(self.lead_time_mean, self.lead_time_std))))
        
        # Inject Black Swan Shock (Port Strike at the DC)
        if isinstance(self.shock_event, dict) and self.shock_event.get("type") == "Port Strike" and self.name == "Distribution Center":
            start_day = self.shock_event["start"]
            delay = self.shock_event["delay"]
            if start_day <= self.env.now <= start_day + 30: # Strike lasts for 30 days
                sim_logger.warning(f"Day {self.env.now}: PORT STRIKE ACTIVE! Delaying shipment to DC by {delay} days.")
                lead_time += delay
                
        yield self.env.timeout(lead_time)
        
        self.inventory += qty
        self.on_order -= qty
        sim_logger.info(f"Day {self.env.now}: {self.name} received shipment of {qty} units.")

def run_simulation(days=365, demand_mean=20, policies=None, seed=42, use_ml=False, shock_event=None):
    if seed is not None:
        np.random.seed(seed)
        
    env = simpy.Environment()
    
    if policies is None:
        policies = {
            "Retail Store": (50, 150),
            "Regional Warehouse": (150, 400),
            "Distribution Center": (400, 1000)
        }
        
    supplier = SupplyChainNode(env, "Supplier", None, s=0, S=0, lead_time_mean=0, lead_time_std=0, is_supplier=True)
    
    dc = SupplyChainNode(env, "Distribution Center", supplier, 
                         s=policies["Distribution Center"][0], S=policies["Distribution Center"][1], 
                         lead_time_mean=7, lead_time_std=1)
    dc.shock_event = shock_event
    
    warehouse = SupplyChainNode(env, "Regional Warehouse", dc, 
                                s=policies["Regional Warehouse"][0], S=policies["Regional Warehouse"][1], 
                                lead_time_mean=3, lead_time_std=1)
    
    store = SupplyChainNode(env, "Retail Store", warehouse, 
                            s=policies["Retail Store"][0], S=policies["Retail Store"][1], 
                            lead_time_mean=2, lead_time_std=0.5, use_ml=use_ml)
    
    store.customer_demand = []
    
    def recorded_customer_demand(env, store, demand_mean):
        while True:
            # We add weekly seasonality to the actual simulation demand to match our ML training data
            day_of_week = env.now % 7
            base = demand_mean * 1.5 if day_of_week >= 5 else demand_mean * 0.8
            qty = np.random.poisson(base)
            
            store.customer_demand.append(qty)
            if qty > 0:
                sim_logger.info(f"Day {env.now}: Customer demand at Store is {qty} units.")
                store.receive_demand(qty)
            yield env.timeout(1)

    env.process(recorded_customer_demand(env, store, demand_mean))
    
    env.run(until=days)
    
    return [dc, warehouse, store]
