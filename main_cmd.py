import entity
import random
import time
import numpy as np
import pandas as pd
from numerize.numerize import numerize

# Constants for simulation settings
SIMULATION_PERIOD = 300 # Total simulation months
NUMBER_OF_AGENTS = 200  # Initial number of agents
POPULATION_GROWTH_RATE = 1.00105 # Monthly population growth factor

# Global variables
gdp_timeline = []   # Store GDP over time
agents = []         # List of agents in the economy
agents_len = 0
agents_num_timeline = []
agents_wealth = []  # Store agents' wealth over time
available_jobs = [entity.Farmer(), entity.Retailer(), entity.Driver()]  # Available job types
goods_data = []     # Store data about goods each month

# Initialize agents at the start of the simulation
def initialize_agents():
    global agents
    global agents_len
    for x in range(NUMBER_OF_AGENTS):
        agent = entity.Agent(job=random.choice(available_jobs))
        agents.append(agent)

    agents_len = len(agents)

# Handle the calculation and logging of GDP
def handle_gdp():
    global gdp_timeline
    gdp_timeline.append(entity.global_gdp)
    print(f"${numerize(entity.global_gdp)}")
    entity.global_gdp = 0

# Update goods prices based on demand and supply ratios
def update_goods_prices():
    goods_this_month = {}
    for key, goods in entity.all_goods.items():
        goods.update_price()
        entity.update_price_ratio(key, goods)
        goods_this_month[key] = goods.price/goods.original_price
        print(goods)
        goods.reset_value()
    return goods_this_month

# Log to file
def log_to_file(agent, goods_this_month):
    if isinstance(agent.job, entity.Farmer):
        if 'farmer' not in goods_this_month.keys():
            goods_this_month['farmer'] = 0
        goods_this_month['farmer'] += 1   
    elif isinstance(agent.job, entity.Retailer):
        if 'retailer' not in goods_this_month.keys():
            goods_this_month['retailer'] = 0
        goods_this_month['retailer'] += 1
    elif isinstance(agent.job, entity.Driver):
        if 'driver' not in goods_this_month.keys():
            goods_this_month['driver'] = 0
        goods_this_month['driver'] += 1
    
# Update agent activities, consumption, and record wealth
def update_agents(goods_this_month):
    global agents_len
    agent_wealth = []
    for i, agent in enumerate(agents):
        agent.update()        
        agent_wealth.append(agent.wealth)
        if i < 3:
            print(f"{i+1}. {agent}")
        
        # Track the number of agents in each job type for this month
        log_to_file(agent, goods_this_month)
   
    agents_wealth.append(agent_wealth) 
    goods_data.append(goods_this_month)
    agents_num_timeline.append(len(agents))

# Handle population growth by adding new agents
def handle_population_growth():
    global agents_len
    agents_len *= POPULATION_GROWTH_RATE
    needed_agent = round(agents_len-len(agents))
    if needed_agent >= 1:
        for x in range(needed_agent):
            agent = entity.Agent(job=random.choice(available_jobs))
            agents.append(agent)

# Main simulation loop
def main():
    global agents
    global agents_len

    # Iterate through the simulation period
    for _ in range(SIMULATION_PERIOD):
        print("===================================")
        handle_gdp()        
        goods_this_month = update_goods_prices()
        update_agents(goods_this_month)
        handle_population_growth()
        # time.sleep(1)

if __name__ == "__main__":
    initialize_agents()
    main()
    data = pd.DataFrame(goods_data)
    data['gdp'] = gdp_timeline
    data['agents'] = agents_num_timeline
    data['total_wealth'] = [sum(x) for x in agents_wealth]
    print(data)
    data.to_excel('goods.xlsx')