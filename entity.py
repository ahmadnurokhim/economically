import numpy as np

GOODS_MAX_PRICE_MULTIPLIER = 1.75
GOODS_MIN_PRICE_MULTIPLIER = 0.25

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
            multiplier = 100
        
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
    'transport': Goods('trnsprt', 0.025)
}
all_goods_price_ratio = {}

def update_price_ratio(key, goods: Goods):
    all_goods_price_ratio[key] = goods.price / goods.original_price

"""==========================================================================="""


class Job:
    def __init__(self, title: str, income: float, required_skill: float, produced: dict, consumed: dict) -> None:
        self.title = title
        self.income = income
        self.required_skill = required_skill
        self.produced = produced
        self.consumed = consumed

    def do_the_job(self):
        global global_gdp
        for goods_name, value in self.produced.items():
            all_goods[goods_name].supply += value
        for goods_name, value in self.consumed.items():
            all_goods[goods_name].demand += value
            global_gdp += all_goods[goods_name].price * value

class Farmer(Job):
    def __init__(self) -> None:
        """Farm measured in 1 ha. 1 ha produced 6000 kg of food per semester, which worked by 6 people.
        So, monthly it produces 17 kg per person"""
        super().__init__("Farner", all_goods['food'].price * 17.0, 1.0, {'food': 17.0}, {'transport': 0.5})
    
class Retailer(Job):
    def __init__(self) -> None:
        super().__init__("Retailer", all_goods['goods_c'].price * 50.0, 1.0, {'goods_c': 50.0}, {}) # goods_c stands for goods for consumer

class Driver(Job):
    def __init__(self) -> None:
        """A driver is assumed can drive 3000 km monthly"""
        super().__init__("Driver", all_goods['transport'].price * 3000, 1.0, {'transport': 3000.0}, {})


job_mapping = {
    'food': Farmer,
    'goods_c': Retailer,
    'transport': Driver}

"""==========================================================================="""

def randomize_consumption(consumption: dict):
    consumption = {key: value for key, value in consumption.items()}

class Agent:
    
    def __init__(self, initial_wealth=200.0, skill_level=1.0, consumption={'food': 7.0, 'goods_c': 30.0, 'transport': 240.0}, job=None) -> None:
        """All consumption measured monthly. food in kg, goods_c in unit, and transport in km"""
        self.wealth: float = max(0, np.random.normal(initial_wealth, initial_wealth/20))    # USD
        self.skill_level: float = np.random.normal(skill_level, skill_level/20)
        self.consumption: dict = {key: np.random.normal(value, value/20) for key, value in consumption.items()}
        # self.consumption_factor = {'current': 1.0, 'min': 0.4, 'max': 2.0}  # TBD
        # self.production_factor = {'current': 1.0, 'min': 0.4, 'max': 2.0}   # TBD
        self.job: Job = job
    
    def update(self):
        self.consume()
        self.work()
        self.consider_change_job()
           
    def consume(self):
        global global_gdp
        for goods_name, value in self.consumption.items():
            self._update_global_demand(goods_name, value)
            money = all_goods[goods_name].price * value
            self._update_wealth(money)
            global_gdp += money
        
    def work(self):
        self._perform_job()
        self._earn_income() 

    def consider_change_job(self):
        for key, ratio in all_goods_price_ratio.items():
            if ratio > 1:
                if np.random.random() < (((ratio - 1) / 2) ** 4):
                    self.job = job_mapping[key]()
            else:
                if np.random.random() < (((1 - ratio) / 2) ** 4):
                    jobs = job_mapping.copy()
                    jobs.pop(key)
                    self.job = job_mapping[np.random.choice(list(jobs.keys()))]()
                    

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

# class Organization:
#     def __init__(self, title, goods_consumed, goods_produced, workers_needed) -> None:
#         self.title = title
#         self.goods_consumed = goods_consumed
#         self.goods_produced = goods_produced
#         self.workers_needed = workers_needed