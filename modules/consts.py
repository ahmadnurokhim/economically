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

TAX_UNTAXED_INCOME = 300 # IN USD
TAX_LOW_THRESHOLD =  280 # IDR 50M annually
TAX_MED_THRESHOLD = 1400 # IDR 250M annually
TAX_HIG_THRESHOLD = 2800 # IDR 500M annually
TAX_LOW_RATE = 0.05 # If below low threshold
TAX_MED_RATE = 0.15 # If below med threshold
TAX_HIG_RATE = 0.25 # If below hig threshold
TAX_ULT_RATE = 0.30 # If above hig threshold
