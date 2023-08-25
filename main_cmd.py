import random
import numpy as np
import pandas as pd
from numerize.numerize import numerize
import modules.jobs as m_jobs 
import modules.agents as m_agents
import modules.general_vars as m_vars
import modules.goods as m_goods
import modules.consts as m_constants
import modules.organizations as m_orgs

# random.seed(20)
# np.random.seed(20)

# Constants for simulation settings
SIMULATION_PERIOD = 300 # Total simulation months
NUMBER_OF_AGENTS = 3000  # Initial number of agents
POPULATION_GROWTH_RATE = 1.00105 # Monthly population growth factor

# Initialize agents at the start of the simulation
def initialize_agents():
    for x in range(NUMBER_OF_AGENTS):
        # agent = entity.Agent(job=random.choice(available_jobs))
        skill_level = 1.0
        if np.random.random() < 0.005:
            skill_level = 2.0
        elif np.random.random() < 0.001:
            skill_level = 2.0
        
        target_job = 0
        if np.random.random() < 0.06:
            target_job = m_jobs.available_jobs[0]
        elif np.random.random() < 0.1:
            target_job = m_jobs.available_jobs[1]
        else:
            target_job = m_jobs.available_jobs[2]
        agent = m_agents.Agent(skill_level=skill_level, job=target_job)
        m_agents.agents_list.append(agent)
        print(agent.id)

    m_agents.agents_len = len(m_agents.agents_list)

# Handle the calculation and logging of GDP
def handle_gdp():
    m_vars.gdp_timeline.append(m_vars.gdp_current_month)
    m_vars.gdp_current_month = 0

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
        'academics': 0,
        'clerk': 0,
        'student': 0}
        
    for key, goods in m_goods.goods_all.items():
        goods.update_price()
        m_goods.update_price_ratio(key, goods)
        goods_this_month[key] = goods.price/goods.original_price
        goods.reset_value()
    return goods_this_month

# Log to file
def log_agent_data(agent, goods_and_jobs):
    if isinstance(agent.job, m_jobs.Farmer):
        goods_and_jobs['farmer'] += 1   
    elif isinstance(agent.job, m_jobs.Retailer):
        goods_and_jobs['retailer'] += 1
    elif isinstance(agent.job, m_jobs.Driver):
        goods_and_jobs['driver'] += 1
    elif isinstance(agent.job, m_jobs.Academics):
        goods_and_jobs['academics'] += 1
    elif isinstance(agent.job, m_jobs.Clerk):
        goods_and_jobs['clerk'] += 1
    elif isinstance(agent.job, m_jobs.Student):
        goods_and_jobs['student'] += 1
    
# Update agent activities, consumption, and record wealth
def update_agents(goods_and_jobs):
    agent_wealth = []
    agent_cons_factor = []
    for i, agent in enumerate(m_agents.agents_list):
        agent.update()        
        agent_wealth.append(agent.wealth)
        
        # Track the number of agents in each job type for this month
        log_agent_data(agent, goods_and_jobs)
        agent_cons_factor.append(agent.consumption_factor)
   
    m_agents.agents_wealth.append(agent_wealth) 
    m_agents.agents_consumption_factor.append(np.mean(agent_cons_factor))
    m_goods.goods_data.append(goods_and_jobs)
    m_agents.agents_num_timeline.append(len(m_agents.agents_list))

# Handle population growth by adding new agents
def handle_population_growth():
    m_agents.agents_len *= POPULATION_GROWTH_RATE
    needed_agent = round(m_agents.agents_len-len(m_agents.agents_list))
    if needed_agent >= 1:
        for x in range(needed_agent):
            job = np.random.random()
            if job < 0.06:
                job = m_jobs.Farmer()
            elif job < 0.6:
                job = m_jobs.Retailer()
            else:
                job = m_jobs.Driver()
            agent = m_agents.Agent(job=random.choice(m_jobs.available_jobs))
            m_agents.agents_list.append(agent)

def log_job_data():
    incomes = [
        m_constants.FARMER_OUTPUT_FOOD * m_goods.goods_all['food'].price,
        m_constants.RETAILER_OUTPUT_GOODS * m_goods.goods_all['goods_c'].price,
        m_constants.DRIVER_OUTPUT_TRANSPORT * m_goods.goods_all['transport'].price,
    ]
    m_jobs.jobs_incomes.append(incomes)


# Main simulation loop
def main():
    # Iterate through the simulation period
    for _ in range(SIMULATION_PERIOD):
        handle_gdp()        
        goods_this_month = update_goods_prices()
        update_agents(goods_this_month) # this variable is passed just for logging
        handle_population_growth()
        log_job_data()
        m_jobs.update_monthly()
        # print(entity.level_1_jobs)
        m_vars.gdp_current_month = m_vars.gdp_current_month + 1
        if _ % 10 == 0:
            print(f"Govt tax in: ${numerize(m_orgs.orgs_all['government'].tax_income)}")
        m_orgs.update_monthly()
        if _ % 10 == 0:
            print(f"Month: {_}")
            print(f"GDP: ${numerize(m_vars.gdp_current_month)}")
            # print(entity.level_1_jobs)
        m_vars.world_date += 1
        # time.sleep(0.1)

if __name__ == "__main__":
    initialize_agents()
    main()
    data = pd.DataFrame(m_goods.goods_data)
    data['agents'] = m_agents.agents_num_timeline
    data['gdp'] = m_vars.gdp_timeline
    data['total_wealth'] = [sum(x) for x in m_agents.agents_wealth]
    data['avg_cons_fac'] = m_agents.agents_consumption_factor
    data = pd.concat([data, pd.DataFrame(m_jobs.jobs_incomes, columns=['farmer', 'retailer', 'driver'])], axis=1)
    data['wealth_per_capita'] = data['total_wealth']/data['agents']
    # print(data)
    # print([{x.id: x.wealth} for x in agents])
    data.to_excel('monthly_log.xlsx')