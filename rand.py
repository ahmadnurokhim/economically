import random

class Entity:
    def __init__(self, skill):
        self.skill = skill
        self.wealth = 0

class Bakery(Entity):
    def __init__(self, num_bakers):
        super().__init__(1.0)  # Minimum baker skill: 1.0
        self.num_bakers = num_bakers
        self.cost_per_kg = 20
        self.production_per_baker = 1000

class Company(Entity):
    def __init__(self, num_clerks):
        super().__init__(2.0)  # Minimum employee skill: 2.0
        self.num_clerks = num_clerks
        self.salary_low_skill = 2500
        self.salary_high_skill = 6000
        self.production_per_clerk = 1000

class School(Entity):
    def __init__(self, num_academics):
        super().__init__(3.0)  # Minimum employee skill: 3.0
        self.num_academics = num_academics
        self.student_fee = 50
        self.years_to_graduate = 3
        self.students = []

class Person(Entity):
    def __init__(self, skill):
        super().__init__(skill)

# Simulation setup
num_bakeries = 2
num_companies = 1
num_schools = 1

bakeries = [Bakery(random.randint(1, 5)) for _ in range(num_bakeries)]
companies = [Company(random.randint(20, 50)) for _ in range(num_companies)]
schools = [School(random.randint(5, 15)) for _ in range(num_schools)]

people = [Person(random.uniform(1, 4)) for _ in range(100)]

# Simulation loop (12 time steps for 1 year)
for timestep in range(12):
    print(f"Month {timestep + 1}:")

    # Bakery production
    for bakery in bakeries:
        total_production = bakery.num_bakers * bakery.production_per_baker
        production_cost = total_production * bakery.cost_per_kg
        bakery.wealth -= production_cost

    # Company production
    for company in companies:
        total_production = company.num_clerks * company.production_per_clerk
        salary = company.salary_high_skill if company.skill >= 3.0 else company.salary_low_skill
        production_cost = total_production * salary
        company.wealth -= production_cost

    # School operations
    for school in schools:
        for student in school.students:
            student.skill += 1
            school.wealth += school.student_fee

    # Individuals' activities
    for person in people:
        person.wealth += random.randint(100, 1000)  # Random income

# Print final results
for i, person in enumerate(people):
    print(f"Person {i + 1}: Skill {person.skill:.2f}, Wealth {person.wealth:.2f}")
