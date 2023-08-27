import modules.agents as m_agents
import modules.jobs as m_jobs
import modules.goods as m_goods
class Organization:
    def __init__(self, org_id: str, employees_needed: dict, owner_id: str= '', produced: dict={}, consumed: dict={}, scaling_init=1.0, scaling_max=1.0):
        self.org_id: str = org_id
        self.owner_id: str = owner_id
        self.cash = 0
        self.employees_needed_init: dict = employees_needed.copy()
        self.employees_needed: dict = employees_needed.copy()
        self.employee_ids = {key: [] for key in self.employees_needed.keys()}
        self.produced_init: dict = produced.copy()
        self.produced: dict = produced.copy()
        self.consumed: dict = consumed
        self.revenue = 0
        self.spending = 0
        self.scaling_min: float = scaling_init
        self.scaling_curr: float = scaling_init
        self.scaling_max: float = scaling_max

    def get_vacancy_dict(self):
        # Calculate the difference between needed employees and the number of employees for each job
        vacancy = {key: self.employees_needed[key] - len(self.employee_ids[key]) for key in self.employees_needed.keys()}
        return vacancy # return a dict with job (key) and vacancy (value)

    def apply(self, employee_id: int, job: str):
        """This method will be called from agent's consider_change_job. In return, the agent will receive the job instace"""
        if job not in self.employee_ids.keys():
            self.employee_ids[job] = []
        self.employee_ids[job].append(employee_id)
        return True
    
    def resign(self, employee_id: int, job: str):
        """This method will be called from agent's consider_change_job"""
        self.employee_ids[job].remove(employee_id)
    
    def update(self):
        self.update_revenue()
        self.update_spending()
        self.update_cash()
        self.scaling()
    
    def update_revenue(self):
        for key, qty in self.produced.items():
            self.revenue += (qty * m_goods.goods_all[key].price)

    def update_spending(self):
        for key, qty in self.consumed.items(): # Spending on goods
            self.spending += (qty * m_goods.goods_all[key].price)

        for key, id_list in self.employee_ids.items(): # Spending on employee
            if m_jobs.jobs_all_income[key] < 0: # check if less than 0, e.g. student tuition
                self.revenue += (len(id_list) * m_jobs.jobs_all_income[key] * -1)
            else:
                self.spending += (len(id_list) * m_jobs.jobs_all_income[key])
        if self.org_id == 'government':
            print(f"this month spent {self.spending} for {len(self.employee_ids['clerk'])}clerks")

    def update_cash(self):
        self.cash = self.cash + self.revenue - self.spending

    def scaling(self):
        if (self.scaling_curr >= self.scaling_max) or (self.scaling_curr <= self.scaling_min): 
            # skip scaling if already max or min
            return
        capacity_change = 0.0
        for key in self.produced.keys():
            if m_goods.goods_all[key].demand > m_goods.goods_all[key].supply:
                capacity_change = 0.1
            elif m_goods.goods_all[key].demand < (0.9 * m_goods.goods_all[key].supply):
                capacity_change = -0.1

        if capacity_change != 0.0:
            self.scaling_curr += capacity_change
            self.employees_needed = {k: int(qty * self.scaling_curr) for k, qty in self.employees_needed_init.items()}
            self.produced = {k: int(qty * self.scaling_curr) for k, qty in self.produced_init.items()}
    
    def reset_rev_spe(self):
        self.revenue = 0
        self.spending = 0

class School(Organization):
    def __init__(self, org_id: str):
        super().__init__(org_id, employees_needed={"academics":2, "student": 40}, owner_id='government')
    
class Government(Organization):
    def __init__(self, org_id: str):
        super().__init__(org_id, employees_needed={'clerk': 20}, owner_id='government')
        self.tax_income = 0
    
    def scaling(self):
        for key in self.employees_needed.keys():
            self.employees_needed[key] = int(self.employees_needed_init[key]) + int(self.employees_needed_init[key] * len(m_agents.agents_list) / 2000)
    
    def update_revenue(self):
        super().update_revenue()
        self.revenue += self.tax_income
    
    def reset_rev_spe(self):
        super().reset_rev_spe()
        self.tax_income = 0

class Power_Plant(Organization):
    def __init__(self, org_id: str):
        super().__init__(
            org_id=org_id,
            employees_needed= {'clerk': 2,  'specialist': 1}, # 'worker': 5
            owner_id='government',
            produced={'energy': 30*24*1000}, # 30 days, 24 hours, 1000 kW
            scaling_max=2.0)
  

orgs_all = {
    'school_1': School('school_1'),
    'government': Government('government'),
    'power_plant_1': Power_Plant('power_plant_1')}
government_log = []

def update_monthly():
    global orgs_all
    org: Organization
    for org in orgs_all.values():
        org.update()

def log_government():
    global government_log
    global orgs_all
    government_log.append({
        'gov_cash': orgs_all['government'].cash,
        'gov_revenue': orgs_all['government'].revenue + orgs_all['government'].tax_income,
        'gov_spending': orgs_all['government'].spending,
        'gov_tax_income': orgs_all['government'].tax_income,
        'gov_clerk': len(orgs_all['government'].employee_ids['clerk'])})
        
def reset_orgs():
    global orgs_all
    org: Organization
    for org in orgs_all.values():
        org.reset_rev_spe()