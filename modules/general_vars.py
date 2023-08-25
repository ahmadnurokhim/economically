gdp_current_month = 0
gdp_timeline = []   # Store GDP over time
world_date = 0


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