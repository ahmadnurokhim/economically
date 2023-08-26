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
SIMULATION_PERIOD = 200 # Total simulation months
NUMBER_OF_AGENTS = 3000  # Initial number of agents

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
            target_job: m_jobs.Job = m_jobs.available_jobs[0]
        elif np.random.random() < 0.1:
            target_job: m_jobs.Job = m_jobs.available_jobs[1]
        else:
            target_job: m_jobs.Job = m_jobs.available_jobs[2]
        agent = m_agents.Agent(skill_level=skill_level, job=target_job)
        m_agents.agents_list.append(agent)
        print(agent.id)

    m_agents.agents_len_curr_predicted = len(m_agents.agents_list)

# Handle the calculation and logging of GDP


# Main simulation loop
def main():
    # Iterate through the simulation period
    for _ in range(SIMULATION_PERIOD):
        m_agents.update_monthly()
        m_goods.update_monthly()
        m_jobs.update_monthly()
        if _ % 10 == 0:
            print(f"Govt tax in: ${numerize(m_orgs.orgs_all['government'].tax_income)}")
        m_orgs.update_monthly()
        m_vars.update_gdp()
        if _ % 10 == 0:
            print(f"Month: {_}")
            print(f"GDP: ${numerize(m_vars.gdp_current_month)}")
        m_goods.reset_goods_supply_demand()
        m_vars.reset_gdp()
        m_vars.world_date += 1
        # time.sleep(0.1)

def logs_to_files():
    agents_log_df_1 = pd.DataFrame(m_agents.agents_count_log)
    agents_log_df_2 = pd.DataFrame(m_agents.agents_wealth_log)
    agents_log_df_3 = pd.DataFrame(m_agents.agents_consumption_factor_log)
    agents_log_df_4 = pd.DataFrame(m_agents.agents_avg_skill_log)
    agents_log_df = pd.concat([agents_log_df_1, agents_log_df_2, agents_log_df_3, agents_log_df_4], axis=1)
    agents_log_df.columns = ['ag_cout', 'wealth', 'cons_f', 'avg_skill']
    goods_log_df = pd.DataFrame(m_goods.goods_log)
    jobs_income_log_df = pd.DataFrame(m_jobs.jobs_incomes_log)
    jobs_type_log_df = pd.DataFrame(m_jobs.jobs_type_log)
    jobs_log_df = pd.concat([jobs_type_log_df, jobs_income_log_df], axis=1)
    return agents_log_df, goods_log_df, jobs_log_df

if __name__ == "__main__":
    initialize_agents()
    main()
    a, g, j = logs_to_files()
    a.to_excel('agents.xlsx')
    g.to_excel('goods.xlsx')
    j.to_excel('jobs.xlsx')

    # data = pd.DataFrame(m_goods.goods_log)
    # data['agents'] = m_agents.agents_count_log
    # data['gdp'] = m_vars.gdp_timeline
    # data['total_wealth'] = [sum(x) for x in m_agents.agents_wealth_log]
    # data['avg_cons_fac'] = m_agents.agents_consumption_factor_log
    # data = pd.concat([data, pd.DataFrame(m_jobs.jobs_incomes_log, columns=['farmer', 'retailer', 'driver'])], axis=1)
    # data['wealth_per_capita'] = data['total_wealth']/data['agents']
    # print(data)
    # print([{x.id: x.wealth} for x in agents])
    # data.to_excel('monthly_log.xlsx')