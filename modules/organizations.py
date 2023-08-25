class Organization:
    def __init__(self, org_id: str, employees_needed: dict):
        self.org_id: str = org_id
        self.cash = 0
        self.employees_needed: dict = employees_needed
        self.employee_ids = {key: [] for key in self.employees_needed.keys()}
        self.need_employees = True

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
    
    def pay_salary(self, salary: float):
        self.cash -= salary
        
class School(Organization):
    def __init__(self, org_id: str):
        super().__init__(org_id, employees_needed={"academics":2, "student": 40})
    
class Government(Organization):
    def __init__(self, org_id: str):
        super().__init__(org_id, employees_needed={'clerk': 100})
        self.tax_income = 0
    
    def update_cash(self):
        self.cash += self.tax_income
        self.tax_income = 0

orgs_all = {'school_1': School('school_1'), 'government': Government('government')}

def update_monthly():
    orgs_all['government'].update_cash()