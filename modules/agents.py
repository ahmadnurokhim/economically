import numpy as np
from modules.consts import *
from modules.jobs import Job, Driver, Student
from modules.jobs import job_mapping, level_1_jobs, level_2_jobs, level_3_jobs
from modules.goods import all_goods
from modules.organizations import global_orgs
import modules.general_vars as general_vars

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
        self.job: Job = job
        
        AGENT_ID = AGENT_ID + 1
    
    def update(self):
        self.consume()
        self.update_consumption_factor()
        self.work()
        if not isinstance(self.job, Student): # Dont consider change job if student
            if np.random.random() < 0.05:
                self.consider_change_job()
           
    def consume(self):
        money_spent = 0
        for goods_name, value in self.consumption.items():
            actual_consumption = value * self.consumption_factor # actual consumption for current goods  
            self._update_global_demand(goods_name, actual_consumption)
            money_spent_on_this_goods = all_goods[goods_name].price * actual_consumption
            self._update_wealth(money_spent_on_this_goods)
            money_spent += money_spent_on_this_goods
            general_vars.global_gdp += money_spent_on_this_goods
        self.latest_spending = money_spent
        
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
        if isinstance(self.job, Student):
            if self.job.is_graduated():
                self.skill_level += 1
                global_orgs[self.job.org_id].resign(self.id, self.job.title)
                self.job = Driver() # Student will become driver after graduated
            
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

    def _update_global_demand(self, goods_name: str, value: float):
        all_goods[goods_name].demand += value

    def _update_wealth(self, money: float):
        self.wealth -= money

    def _perform_job(self):
        self.job.do_the_job()

    def _earn_income(self):
        self.wealth += self.job.income #* np.random.normal(1, 0.01)
    
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
                org_name for org_name, org in global_orgs.items()
                if best_opportunity in org.get_vacancy_dict().keys() and org.get_vacancy_dict()[best_opportunity] > 0
            ]

            if org_name_that_has_vacancy: # check if if there are vacancy and try to apply
                org_to_apply = np.random.choice(org_name_that_has_vacancy)
                if global_orgs[org_to_apply].apply(self.id, best_opportunity): # if application success
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
