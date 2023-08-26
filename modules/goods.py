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
        # print(self.supply, self.demand)
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

goods_all = {
    'food': Goods('food', 1),
    'goods_c': Goods('goods_c', 2),
    'transport': Goods('transport', 0.12),
    'energy': Goods('energy', ENERGY_PRICE)
}
goods_log = []     # Store data about goods each month

def update_monthly():
    global goods_log
    global goods_all
    goods_price_ratio_this_month = {key: 0 for key in goods_all.keys()}
    for key, goods in goods_all.items(): # for all goods, store the price ratio and then reset the demand & supply
        goods.update_price() # update the price
        goods_price_ratio_this_month[key] = goods.price / goods.original_price # update the price ratio
    goods_log.append(goods_price_ratio_this_month)

def reset_goods_supply_demand():
    for goods in goods_all.values():
        goods.reset_value()