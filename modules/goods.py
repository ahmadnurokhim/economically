import numpy as np
from modules.consts import *

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