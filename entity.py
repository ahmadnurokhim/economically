import numpy as np

GOODS_MAX_PRICE_MULTIPLIER = 2
GOODS_MIN_PRICE_MULTIPLIER = 0.25

ENERGY_PRICE = 0.1  # USD/KWh
UTILITY = 1         # Based    
STABLE_GOODS = ['energy']                      

INCOME_ACADEMICS = 550
INCOME_STUDENT = -50
INCOME_CLERK = 350
INCOME_WORKER = 280

FARMER_OUTPUT_FOOD = 160.0          # 150
RETAILER_OUTPUT_GOODS = 120.0       # 130
DRIVER_OUTPUT_TRANSPORT = 1500.0    # 1500

AGENT_DEFAULT_CONSUMPTION = {
    'food': 7.0,
    'goods_c': 30.0,
    'transport': 240.0,
    'energy': 10}

AGENT_MIN_CONSUMPTION_FACTOR = 0.4
AGENT_MAX_CONSUMPTION_FACTOR = 4.0

AGENT_LOW_WEALTH_THRESHOLD = 500 # IN USD
AGENT_HIGH_WEALTH_THRESHOLD = 5000 # IN USD
AGENT_ID = 0

global_gdp = 0

class Goods:
    def __init__(self, name:str, price:float) -> None:
        self.name = name
        self.previous_supply = 0
        self.supply = 0
        self.demand = 0
        self.original_price = price
        self.price = price
        self.max_price = price * GOODS_MAX_PRICE_MULTIPLIER
        self.min_price = price * GOODS_MIN_PRICE_MULTIPLIER

    def update_price(self):
        if self.name in STABLE_GOODS:
            return
        
        if self.previous_supply != 0:
            multiplier = self.demand / self.previous_supply
        else:
            multiplier = 1
        
        new_price = self.original_price * multiplier
        if new_price > self.max_price:
            self.price = min(self.price * 0.1 + new_price * 0.9, self.max_price) 
        elif new_price < self.min_price:
            self.price = max(self.price * 0.1 + new_price * 0.9, self.min_price)
        else:
            self.price = self.price * 0.3 + new_price * 0.7
    
    def __str__(self) -> str:
        ratio = self.price / self.original_price
        return f"{self.name}\t{self.supply} \t {self.demand} \t ${self.price:.2f}\t{ratio*100:.2f}%"
    
    def reset_value(self):
        self.previous_supply = self.supply
        self.supply = 0
        self.demand = 0

all_goods = {
    'food': Goods('food', 1),
    'goods_c': Goods('goods_c', 2),
    'transport': Goods('transport', 0.12),
    'energy': Goods('energy', ENERGY_PRICE)
}
all_goods_price_ratio = {}

def update_price_ratio(key, goods: Goods):
    all_goods_price_ratio[key] = goods.price / goods.original_price

"""==========================================================================="""


class Job:
    def __init__(self, title: str, required_skill: float, produced: dict, consumed: dict) -> None:
        self.title = title
        self.income = 0
        self.required_skill = required_skill
        self.produced = produced
        self.consumed = consumed
        self.update_income()

    def do_the_job(self):
        global global_gdp
        for goods_name, value in self.produced.items():
            all_goods[goods_name].supply += value
        for goods_name, value in self.consumed.items():
            all_goods[goods_name].demand += value
            global_gdp += all_goods[goods_name].price * value
        self.update_income()

    def update_income(self):
        return

class Farmer(Job):
    def __init__(self) -> None:
        """Farm measured in 1 ha. 1 ha produced 5400 kg of food per semester, which worked by 6 people.
        So, monthly, it produces 150 kg per person"""
        super().__init__("Farner", 1.0, {'food': FARMER_OUTPUT_FOOD}, {'transport': 0.5})
    
    def update_income(self):
        self.income = all_goods['food'].price * FARMER_OUTPUT_FOOD
    
class Retailer(Job):
    def __init__(self) -> None:
        super().__init__("Retailer", 1.0, {'goods_c': RETAILER_OUTPUT_GOODS}, {}) # goods_c stands for goods for consumer

    def update_income(self):
        self.income = all_goods['goods_c'].price * RETAILER_OUTPUT_GOODS

class Driver(Job):
    def __init__(self) -> None:
        super().__init__("Driver", 1.0, {'transport': DRIVER_OUTPUT_TRANSPORT}, {})

    def update_income(self):
        self.income = all_goods['transport'].price * DRIVER_OUTPUT_TRANSPORT

class Academics(Job):
    def __init__(self):
        super().__init__("Academics", 3.0, produced={}, consumed={})
        self.income = INCOME_ACADEMICS

class Student(Job):
    def __init__(self):
        super().__init__("Student", 1.0, produced={}, consumed={})
        self.income = INCOME_STUDENT

class Clerk(Job):
    def __init__(self) -> None:
        super().__init__("Clerk", 2.0, produced={}, consumed={})
        self.income = INCOME_CLERK

job_mapping = {
    'farmer': Farmer,
    'retailer': Retailer,
    'driver': Driver,
    'academics': Academics,
    'student': Student,
    'clerk': Clerk
}

level_1_jobs = {
            'farmer': all_goods['food'].price * FARMER_OUTPUT_FOOD,
            'retailer': all_goods['goods_c'].price * RETAILER_OUTPUT_GOODS,
            'driver': all_goods['transport'].price * DRIVER_OUTPUT_TRANSPORT,
        }
level_2_jobs = {'clerk': INCOME_CLERK}
level_3_jobs = {'academics': INCOME_ACADEMICS}

def update_level_1_jobs():
    global level_1_jobs
    level_1_jobs = {
            'farmer': all_goods['food'].price * FARMER_OUTPUT_FOOD,
            'retailer': all_goods['goods_c'].price * RETAILER_OUTPUT_GOODS,
            'driver': all_goods['transport'].price * DRIVER_OUTPUT_TRANSPORT,
        }

"""==========================================================================="""


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
        if np.random.random() < 0.01:
            self.consider_change_job()
           
    def consume(self):
        global global_gdp
        money_spent = 0
        for goods_name, value in self.consumption.items():
            actual_consumption = value * self.consumption_factor # actual consumption for current goods  
            self._update_global_demand(goods_name, actual_consumption)
            money_spent_on_this_goods = all_goods[goods_name].price * actual_consumption
            self._update_wealth(money_spent_on_this_goods)
            money_spent += money_spent_on_this_goods
            global_gdp += money_spent_on_this_goods
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
            return False # Return false if best opportunity is not more than 10% higher income than current
        
        if best_opportunity not in level_1_jobs.keys(): # check if the best is not level 1 jobs (because level 1 jobs dont need to apply)
            # List all org that has vacancy
            org_name_that_has_vacancy = [
                org_name for org_name, org in global_orgs.items()
                if best_opportunity in org.get_vacancy_dict().keys() and org.get_vacancy_dict()[best_opportunity] > 0
            ]
            
            if org_name_that_has_vacancy: # check if if there are vacancy and try to apply
                org_to_apply = np.random.choice(org_name_that_has_vacancy)
                self.job = global_orgs[org_to_apply].apply(self.id, best_opportunity)
                return True
            else: # Do this instead if no vacancy available for current best opportunity
                opportunity.pop(best_opportunity)
                return self._search_for_vacancy_and_apply(opportunity) # Redo all again, with the same opportunity dict, but without the last job that has no vacancy

        else: # if the best opportunity is level 1 job
            self.job = job_mapping[best_opportunity]()
            return True
        

    def __str__(self) -> str:
        return f"Wealth: {self.wealth:.2f}"


"""==========================================================================="""


class Organization:
    def __init__(self, name: str, employees_needed: dict):
        self.name: str = name
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
        return job_mapping[job]()
    
    def resign(self, employee_id: int, job: str):
        """This method will be called from agent's consider_change_job"""
        self.employee_ids[job].remove(employee_id)
    
    def update_cash(self):
        pass
        
class School(Organization):
    def __init__(self):
        super().__init__("School", employees_needed={"academics":2, "student": 40})
    
class Government(Organization):
    def __init__(self):
        super().__init__('Government', employees_needed={'clerk': 100})

global_orgs = {'school_1': School(), 'government': Government()}

# farm*
# produce: food
# consume: -
# employee: farmer

# retail*
# produce: goods_c
# consume: -
# employee: retailer

# tranport*
# produce: transport
# consume: -
# employee: driver

# school*
# produce: -
# consume: energy
# employee: 2 academics, 40 students

# government
# produce: -
# consume: energy
# employee: 20 clerks

# manufacturing
# produce: goods_r
# consume: energy
# employee: 4 clerks, 20 worker

# mining
# produce: coal
# consume: energy
# employee: 4 clerk, 20 worker

# power plant
# produce: energy
# consume: coal
# employee: 4 clerks, 10 worker, 2 specialist

# monthly incomes in USD/month based on indonesian income
# farmer    : food price * food output (avg 160)
# retailer  : goods_c price * goods_c output (avg 240)
# driver    : transport price * transport output (avg 180)
# academics : 550
# student   : -50
# clerks    : 350
# worker    : 280
# specialist: 

# skil level (1 = uneducated, 2 = educated, 3 = highly educated)
# farmer    : 1
# retailer  : 1
# driver    : 1
# academics : 3
# student   : 1
# clerks    : 2
# worker    : 1
# specialist: 3

# *done