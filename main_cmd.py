import entity
import random
import time
import numpy as np
import pandas as pd
from numerize.numerize import numerize

random.seed(20)
np.random.seed(20)

# Constants for simulation settings
SIMULATION_PERIOD = 600 # Total simulation months
NUMBER_OF_AGENTS = 3000  # Initial number of agents
POPULATION_GROWTH_RATE = 1.00105 # Monthly population growth factor

# Global variables
gdp_timeline = []   # Store GDP over time
agents = []         # List of agents in the economy
agents_len = 0
agents_num_timeline = []
agents_wealth = []  # Store agents' wealth over time
agents_consumption_factor = []
available_jobs = [entity.Farmer(), entity.Retailer(), entity.Driver()]  # Available job types
jobs_incomes = []
goods_data = []     # Store data about goods each month

# Initialize agents at the start of the simulation
def initialize_agents():
    global agents
    global agents_len
    for x in range(NUMBER_OF_AGENTS):
        # agent = entity.Agent(job=random.choice(available_jobs))
        skill_level = 1.0
        if np.random.random() < 0.01:
            skill_level = 3.0
        elif np.random.random() < 0.1:
            skill_level = 2.0
        
        target_job = 0
        if np.random.random() < 0.07:
            target_job = available_jobs[0]
        elif np.random.random() < 0.6:
            target_job = available_jobs[1]
        else:
            target_job = available_jobs[2]
        agent = entity.Agent(skill_level=skill_level, job=target_job)
        agents.append(agent)
        print(agent.id)

    agents_len = len(agents)

# Handle the calculation and logging of GDP
def handle_gdp():
    global gdp_timeline
    gdp_timeline.append(entity.global_gdp)
    entity.global_gdp = 0

# Update goods prices based on demand and supply ratios
def update_goods_prices():
    goods_this_month = {
        'food': 0,
        'goods_c': 0,
        'transport': 0,
        'energy': 0,
        'farmer': 0,
        'retailer': 0,
        'driver': 0,
        'academics': 0}
        
    for key, goods in entity.all_goods.items():
        goods.update_price()
        entity.update_price_ratio(key, goods)
        goods_this_month[key] = goods.price/goods.original_price
        goods.reset_value()
    return goods_this_month

# Log to file
def log_agent_data(agent, goods_and_jobs):
    if isinstance(agent.job, entity.Farmer):
        goods_and_jobs['farmer'] += 1   
    elif isinstance(agent.job, entity.Retailer):
        goods_and_jobs['retailer'] += 1
    elif isinstance(agent.job, entity.Driver):
        goods_and_jobs['driver'] += 1
    elif isinstance(agent.job, entity.Academics):
        goods_and_jobs['academics'] += 1
    
# Update agent activities, consumption, and record wealth
def update_agents(goods_and_jobs):
    global agents_len
    global agent_wealth
    global agents_consumption_factor
    agent_wealth = []
    agent_cons_factor = []
    for i, agent in enumerate(agents):
        agent.update()        
        agent_wealth.append(agent.wealth)
        
        # Track the number of agents in each job type for this month
        log_agent_data(agent, goods_and_jobs)
        agent_cons_factor.append(agent.consumption_factor)
   
    agents_wealth.append(agent_wealth) 
    agents_consumption_factor.append(np.mean(agent_cons_factor))
    goods_data.append(goods_and_jobs)
    agents_num_timeline.append(len(agents))

# Handle population growth by adding new agents
def handle_population_growth():
    global agents_len
    agents_len *= POPULATION_GROWTH_RATE
    needed_agent = round(agents_len-len(agents))
    if needed_agent >= 1:
        for x in range(needed_agent):
            job = np.random.random()
            if job < 0.6:
                job = entity.Farmer()
            elif job < 0.8:
                job = entity.Retailer()
            else:
                job = entity.Driver()
            agent = entity.Agent(job=random.choice(available_jobs))
            agents.append(agent)

def log_job_data():
    incomes = [
        entity.FARMER_OUTPUT_FOOD * entity.all_goods['food'].price,
        entity.RETAILER_OUTPUT_GOODS * entity.all_goods['goods_c'].price,
        entity.DRIVER_OUTPUT_TRANSPORT * entity.all_goods['transport'].price,
    ]
    jobs_incomes.append(incomes)


# Main simulation loop
def main():
    global agents
    global agents_len

    # Iterate through the simulation period
    for _ in range(SIMULATION_PERIOD):
        handle_gdp()        
        goods_this_month = update_goods_prices()
        update_agents(goods_this_month) # this variable is passed just for logging
        handle_population_growth()
        log_job_data()
        if _ % 10 == 0:
            print(f"Month: {_}")
        # time.sleep(0.1)

if __name__ == "__main__":
    initialize_agents()
    main()
    data = pd.DataFrame(goods_data)
    data['agents'] = agents_num_timeline
    data['gdp'] = gdp_timeline
    data['total_wealth'] = [sum(x) for x in agents_wealth]
    data['avg_cons_fac'] = agents_consumption_factor
    data = pd.concat([data, pd.DataFrame(jobs_incomes, columns=['farmer', 'retailer', 'driver'])], axis=1)
    data['wealth_per_capita'] = data['total_wealth']/data['agents']
    # print(data)
    # print([{x.id: x.wealth} for x in agents])
    data.to_excel('goods.xlsx')