import numpy as np
import random
from modules.consts import *
import modules.jobs as m_jobs
from modules.jobs import job_mapping, level_1_jobs, level_2_jobs, level_3_jobs
import modules.goods as m_goods 
import modules.organizations as m_orgs
import modules.general_vars as m_vars

class Agent:
    def __init__(self, initial_wealth=200.0, skill_level=1.0, consumption=AGENT_DEFAULT_CONSUMPTION, job=None) -> None:
        """All consumption measured monthly. food in kg, goods_c in unit, and transport in km"""
        global AGENT_ID
        self.id = AGENT_ID
        self.wealth: float = max(0, np.random.normal(initial_wealth, initial_wealth/10))    # USD
        self.latest_spending = 0
        # self.skill_level: float = np.random.normal(skill_level, skill_level/5)
        self.skill_level = skill_level
        # self.consumption: dict = {key: min(value * AGENT_MIN_CONSUMPTION_FACTOR, max(value * AGENT_MAX_CONSUMPTION_FACTOR, np.random.normal(value, value/5))) for key, value in consumption.items()}
        self.consumption = consumption
        self.consumption_factor = 1.0
        self.job: m_jobs.Job = job
        
        AGENT_ID = AGENT_ID + 1
    
    def update(self):
        self.consume()
        self.update_consumption_factor()
        self.work()
        self.pay_tax()
        if not isinstance(self.job, m_jobs.Student): # Dont consider change job if student
            if np.random.random() < 0.01:
                self.consider_change_job()
           
    def consume(self):
        money_spent = 0
        for goods_name, value in self.consumption.items():
            actual_consumption = value * self.consumption_factor # actual consumption for current goods  
            self._update_global_demand(goods_name, actual_consumption)  # add this agent's demand to global demand
            money_spent_on_this_goods = m_goods.goods_all[goods_name].price * actual_consumption # calculate money spent on this goods
            self._update_wealth(money_spent_on_this_goods) # subtract money spent from wealth
            money_spent += money_spent_on_this_goods
        m_vars.gdp_current_month += money_spent # add this agent's spent to GDP
        self.latest_spending = money_spent # update this agent's latest spending
        
    def update_consumption_factor(self):
        # Based on self profit
        self_profit = self.job.income - self.latest_spending
        if self_profit > 100:
            self.consumption_factor = min(self.consumption_factor + 0.05, AGENT_MAX_CONSUMPTION_FACTOR)
        elif self_profit < 10:
            self.consumption_factor = max(self.consumption_factor - 0.05, AGENT_MIN_CONSUMPTION_FACTOR)
        else:
            self.consumption_factor = min(max(self.consumption_factor + np.random.choice([0.05, -0.05]), AGENT_MIN_CONSUMPTION_FACTOR), AGENT_MAX_CONSUMPTION_FACTOR)

    def work(self):
        self._perform_job()
        self._earn_income()
        if isinstance(self.job, m_jobs.Student):
            if self.job.is_graduated():
                self.skill_level += 1
                m_orgs.orgs_all[self.job.org_id].resign(self.id, self.job.title)
                self.job = m_jobs.Driver() # Student will become driver after graduated
            
    def consider_change_job(self):
        # Dict all the income of level 1 jobs, and add self income
        opportunity = level_1_jobs.copy() # Make a copy to prevent modifying the original dictionary
        opportunity.update({'self': self.job.income})

        # If agent skill is 2 or more, add level 2 jobs to the dictionary
        if self.skill_level >= 2.0:
            opportunity.update(level_2_jobs)
            if self.skill_level >= 3.0:
                opportunity.update(level_3_jobs)

        return self._search_for_vacancy_and_apply(opportunity) # Try to change job recursively

    def pay_tax(self):
        taxable_income = (self.job.income - TAX_UNTAXED_INCOME)
        if taxable_income > 0:
            tax = 0
            if taxable_income < TAX_LOW_THRESHOLD:
                tax = taxable_income * TAX_LOW_RATE
            elif taxable_income < TAX_MED_THRESHOLD:
                tax = taxable_income * TAX_MED_RATE
            elif taxable_income < TAX_HIG_THRESHOLD:
                tax = taxable_income * TAX_HIG_RATE
            else:
                tax = taxable_income * TAX_ULT_RATE
            self.wealth - tax
            m_orgs.orgs_all['government'].tax_income += tax

    def _update_global_demand(self, goods_name: str, value: float):
        m_goods.goods_all[goods_name].demand += value

    def _update_wealth(self, money: float):
        self.wealth -= money

    def _perform_job(self):
        self.job.do_the_job()

    def _earn_income(self):
        self.wealth += self.job.income #* np.random.normal(1, 0.01)
        if not isinstance(self.job, (m_jobs.Farmer, m_jobs.Retailer, m_jobs.Driver)):
            m_orgs.orgs_all[self.job.org_id].pay_salary(self.job.income)
    
    def _search_for_vacancy_and_apply(self, opportunity: dict): # Return true if job changing successful
        if not opportunity:  # Terminate recursion if no opportunities are left
            return False

        best_opportunity = max(opportunity, key=opportunity.get)

        if best_opportunity == 'self':
            return False  # Return false if the current job is best
        
        if opportunity[best_opportunity] < opportunity['self'] * 1.05:
            return False # Return false if best opportunity is not more than 5% higher income than current

        if 'student' in opportunity.keys() and (self.wealth > 2 * -INCOME_STUDENT * 48): # 48 months
            best_opportunity = 'student' # If student is in option, and enough wealth

        if best_opportunity not in level_1_jobs.keys() or best_opportunity == 'student': # check if the best is not level 1 jobs (because level 1 jobs dont need to apply)
            # List all org that has vacancy
            org_name_that_has_vacancy = [
                org_name for org_name, org in m_orgs.orgs_all.items()
                if best_opportunity in org.get_vacancy_dict().keys() and org.get_vacancy_dict()[best_opportunity] > 0
            ]

            if org_name_that_has_vacancy: # check if if there are vacancy and try to apply
                org_to_apply = np.random.choice(org_name_that_has_vacancy)
                if m_orgs.orgs_all[org_to_apply].apply(self.id, best_opportunity): # if application success
                    self.job = job_mapping[best_opportunity](org_id=org_to_apply)
                    return True
            else: # Do this instead if no vacancy available for current best opportunity
                opportunity.pop(best_opportunity)
                return self._search_for_vacancy_and_apply(opportunity) # Redo all again, with the same opportunity dict, but without the last job that has no vacancy

        else: # if the best opportunity is level 1 job
            self.job = job_mapping[best_opportunity]()
            return True
        

    def __str__(self) -> str:
        return f"Wealth: {self.wealth:.2f}"

agents_list = []         # List of agents in the economy
agents_len_curr_predicted = 0
agents_count_log = []   # Store agent count over time
agents_wealth_log = []  # Store agents' wealth over time
agents_consumption_factor_log = []
agents_avg_skill_log = []

def update_monthly():
    wealth_of_all_agents = []
    cons_factor_of_all_agents = []
    skill_of_all_agent = []

    jobs_of_all_agent = {key: 0 for key in m_jobs.job_mapping.keys()}
    agent: Agent
    for agent in agents_list:
        agent.update()
        wealth_of_all_agents.append(agent.wealth)
        cons_factor_of_all_agents.append(agent.consumption_factor)
        jobs_of_all_agent[agent.job.title] += 1
        skill_of_all_agent.append(agent.skill_level)
    
    agents_count_log.append(len(agents_list))
    agents_wealth_log.append(np.sum(wealth_of_all_agents))
    agents_consumption_factor_log.append(np.mean(cons_factor_of_all_agents))
    agents_avg_skill_log.append(np.mean(skill_of_all_agent))
    m_jobs.jobs_type_log.append(jobs_of_all_agent)
    handle_population_growth()

def handle_population_growth():
    global agents_len_curr_predicted
    agents_len_curr_predicted *= POPULATION_GROWTH_RATE
    needed_agent = round(agents_len_curr_predicted-len(agents_list))
    if needed_agent >= 1:
        for x in range(needed_agent):
            job = np.random.random()
            if job < 0.06:
                job = m_jobs.Farmer()
            elif job < 0.6:
                job = m_jobs.Retailer()
            else:
                job = m_jobs.Driver()
            agent = Agent(job=random.choice(m_jobs.available_jobs))
            agents_list.append(agent)