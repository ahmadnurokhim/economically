import entity
import random, time
import numpy as np
import pandas as pd
from numerize.numerize import numerize

SIMULATION_PERIOD = 300 # Month
NUMBER_OF_AGENTS = 200

gdp_timeline = []
agents = []
agents_len = len(agents)
agents_wealth = []
available_jobs = [entity.Farmer(), entity.Retailer(), entity.Driver()]
goods_data = []

def initialize():
    global agents
    global agents_len
    for x in range(NUMBER_OF_AGENTS):
        agent = entity.Agent(job=random.choice(available_jobs))
        agents.append(agent)
    agents_len = len(agents)

def main():
    global agents
    global agents_len
    for _ in range(SIMULATION_PERIOD):
        goods_this_month = {}
        print("===================================")
        # Handle the GDP
        gdp_timeline.append(entity.global_gdp)
        print(f"${numerize(entity.global_gdp)}")
        entity.global_gdp = 0

        # Handling Goods
        for key, goods in entity.all_goods.items():
            goods.update_price()
            entity.update_price_ratio(key, goods)
            goods_this_month[key] = goods.price/goods.original_price
            print(goods)
            goods.reset_value()

        # Handling Agents
        agent_wealth = []
        for i, agent in enumerate(agents):
            agent.update()        
            agent_wealth.append(agent.wealth)
            if i < 3:
                print(f"{i+1}. {agent}")
            
            if isinstance(agent.job, entity.Farmer):
                if 'farmer' not in goods_this_month.keys():
                    goods_this_month['farmer'] = 0
                goods_this_month['farmer'] += 1   
            elif isinstance(agent.job, entity.Retailer):
                if 'retailer' not in goods_this_month.keys():
                    goods_this_month['retailer'] = 0
                goods_this_month['retailer'] += 1
            elif isinstance(agent.job, entity.Driver):
                if 'driver' not in goods_this_month.keys():
                    goods_this_month['driver'] = 0
                goods_this_month['driver'] += 1

        agents_wealth.append(agent_wealth)
        goods_data.append(goods_this_month)

        # Handle Population Growth
        agents_len *= 1.00105 # this should be 1.00105 as monthly population growth
        needed_agent = round(agents_len-len(agents))
        if needed_agent >= 1:
            for x in range(needed_agent):
                agent = entity.Agent(job=random.choice(available_jobs))
                agents.append(agent)


        time.sleep(0.01)


if __name__ == "__main__":
    initialize()
    main()
    # for _ in gdp_timeline[50:]:
        # print(_)
    pd.DataFrame(goods_data).to_excel('goods.xlsx')