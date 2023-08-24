import numpy as np

GOODS_MAX_PRICE_MULTIPLIER = 2
GOODS_MIN_PRICE_MULTIPLIER = 0.25

FARMER_OUTPUT_FOOD = 150.0
RETAILER_OUTPUT_GOODS = 130.0
DRIVER_OUTPUT_TRANSPORT = 1500.0
ACADEMICS_FIXED_INCOME = 400

AGENT_MIN_CONSUMPTION_FACTOR = 0.4
AGENT_MAX_CONSUMPTION_FACTOR = 3.0

AGENT_LOW_WEALTH_THRESHOLD = 500 # IN USD
AGENT_HIGH_WEALTH_THRESHOLD = 2000 # IN USD
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
    'transport': Goods('trnsprt', 0.12)
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

    def update_income(self):
        pass

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
        super().__init__("Academics", required_skill=3.0, produced={}, consumed={})
        self.update_income()
    
    def update_income(self):
        self.income = 400.0

class Student(Job):
    def __init__(self):
        super().__init__("Student", required_skill=1.0, produced={}, consumed={})
        self.update_income()
    
    def update_income(self):
        self.income = -50.0

job_mapping = {
    'farmer': Farmer,
    'retailer': Retailer,
    'driver': Driver,
    'academics': Academics,
    'student': Student
}


"""==========================================================================="""


class Agent:
    
    def __init__(self, initial_wealth=200.0, skill_level=1.0, consumption={'food': 7.0, 'goods_c': 30.0, 'transport': 240.0}, job=None) -> None:
        """All consumption measured monthly. food in kg, goods_c in unit, and transport in km"""
        global AGENT_ID
        self.id = AGENT_ID
        self.wealth: float = max(0, np.random.normal(initial_wealth, initial_wealth/20))    # USD
        # self.skill_level: float = np.random.normal(skill_level, skill_level/5)
        self.skill_level = skill_level
        self.consumption: dict = {key: np.random.normal(value, value/20) for key, value in consumption.items()}
        self.consumption_factor = 1.0
        # self.production_factor = {'current': 1.0, 'min': 0.4, 'max': 2.0}   # TBD
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
        for goods_name, value in self.consumption.items():
            actual_consumption = value * self.consumption_factor
            self._update_global_demand(goods_name, actual_consumption)
            money = all_goods[goods_name].price * value
            self._update_wealth(money)
            global_gdp += money
        
    def update_consumption_factor(self):
        if self.wealth < AGENT_LOW_WEALTH_THRESHOLD:
            self.consumption_factor = max(self.consumption_factor - 0.05, AGENT_MIN_CONSUMPTION_FACTOR)
        elif self.wealth >= AGENT_LOW_WEALTH_THRESHOLD and self.wealth < AGENT_HIGH_WEALTH_THRESHOLD:
            if self.consumption_factor < 1.0:
                self.consumption_factor = min(self.consumption_factor + 0.05, 1)
            elif self.consumption_factor > 1.0:
                self.consumption_factor = max(self.consumption_factor - 0.05, 1)
        elif self.wealth >= AGENT_HIGH_WEALTH_THRESHOLD:
            self.consumption_factor = min(self.consumption_factor + 0.05, AGENT_MAX_CONSUMPTION_FACTOR)

    def work(self):
        self._perform_job()
        self._earn_income() 
            
    def consider_change_job(self):
        if isinstance(self.job, Academics):
            return
        
        opportunity = {
            'farmer': all_goods['food'].price * FARMER_OUTPUT_FOOD,
            'retailer': all_goods['goods_c'].price * RETAILER_OUTPUT_GOODS,
            'driver': all_goods['transport'].price * DRIVER_OUTPUT_TRANSPORT,
            'self': self.job.income
        }
        if self.skill_level >= 3:
            opportunity.update({'academics': ACADEMICS_FIXED_INCOME})

        opportunity = max(opportunity, key=opportunity.get) # will output a job name/id
        
        if opportunity == 'academics':
            available_org_ids = []
            for org_id, org in global_orgs.items():
                if org.get_vacancy()[opportunity] > 0:
                    available_org_ids.append(org_id)
            if len(available_org_ids) > 0:
                choosen_org_id = np.random.choice(available_org_ids)
                self.job = global_orgs[choosen_org_id].apply(self.id, opportunity)
                return
            else:
                opportunity = 'self'
        if opportunity != 'self':
            self.job = job_mapping[opportunity]()

    def _update_global_demand(self, goods_name: str, value: float):
        all_goods[goods_name].demand += value

    def _update_wealth(self, money: float):
        self.wealth -= money

    def _perform_job(self):
        self.job.do_the_job()

    def _earn_income(self):
        self.wealth += self.job.income

    def __str__(self) -> str:
        return f"Wealth: {self.wealth:.2f}"


"""==========================================================================="""


class Organization:
    def __init__(self, name: str, employees_needed: dict):
        self.name: str = name
        self.employees_needed: dict = employees_needed
        self.employee_ids = {}
        self.need_employees = True

    def get_vacancy(self):
        # Calculate the difference between needed employees and the number of employees for each job
        vacancy = {key: self.employees_needed[key] - len(self.employee_ids.get(key, [])) for key in self.employees_needed.keys()}
        print(self.employee_ids)
        return vacancy

    def apply(self, employee_id: int, job: str):
        """This method will be called from agent's consider_change_job. In return, the agent will receive the job instace"""
        if job not in self.employee_ids.keys():
            self.employee_ids[job] = []
        self.employee_ids[job].append(employee_id)
        return job_mapping[job]()
    
    def resign(self, employee_id: int, job: str):
        """This method will be called from agent's consider_change_job"""
        self.employee_ids[job].remove(employee_id)
        
class School(Organization):
    def __init__(self):
        super().__init__("School", employees_needed={"academics":2, "student": 40})
        self.employees_ids = {key: [] for key in self.employees_needed.keys()}
    
global_orgs = {'school_1': School()}