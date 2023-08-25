from modules.consts import *
import modules.goods as m_goods 
import modules.general_vars as general_vars

class Job:
    def __init__(self, title: str, required_skill: float, org_id: str, produced: dict, consumed: dict) -> None:
        self.title = title
        self.income = 0
        self.required_skill = required_skill
        self.produced = produced
        self.consumed = consumed
        self.update_income()
        self.org_id = org_id

    def do_the_job(self):
        global global_gdp
        for goods_name, value in self.produced.items():
            m_goods.goods_all[goods_name].supply += value
        for goods_name, value in self.consumed.items():
            m_goods.goods_all[goods_name].demand += value
            general_vars.gdp_current_month += m_goods.goods_all[goods_name].price * value
        self.update_income()

    def update_income(self):
        return

class Farmer(Job):
    def __init__(self) -> None:
        """Farm measured in 1 ha. 1 ha produced 5400 kg of food per semester, which worked by 6 people.
        So, monthly, it produces 150 kg per person"""
        super().__init__("farner", 1.0, '', {'food': FARMER_OUTPUT_FOOD}, {'transport': 0.5})
    
    def update_income(self):
        self.income = m_goods.goods_all['food'].price * FARMER_OUTPUT_FOOD
    
class Retailer(Job):
    def __init__(self) -> None:
        super().__init__("retailer", 1.0, '', {'goods_c': RETAILER_OUTPUT_GOODS}, {}) # goods_c stands for goods for consumer

    def update_income(self):
        self.income = m_goods.goods_all['goods_c'].price * RETAILER_OUTPUT_GOODS

class Driver(Job):
    def __init__(self) -> None:
        super().__init__("driver", 1.0, '', {'transport': DRIVER_OUTPUT_TRANSPORT}, {})

    def update_income(self):
        self.income = m_goods.goods_all['transport'].price * DRIVER_OUTPUT_TRANSPORT

class Academics(Job):
    def __init__(self, org_id):
        super().__init__("academics", 3.0, org_id, produced={}, consumed={})
        self.income = INCOME_ACADEMICS

class Student(Job):
    def __init__(self, org_id):
        super().__init__("student", 1.0, org_id, produced={}, consumed={})
        self.income = INCOME_STUDENT
        self.enroll_date = general_vars.world_date
        self.graduate_date = self.enroll_date + 48
    
    def is_graduated(self):
        if general_vars.world_date >= self.graduate_date:
            return True

class Clerk(Job):
    def __init__(self, org_id) -> None:
        super().__init__("clerk", 2.0, org_id, produced={}, consumed={})
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
            'farmer': m_goods.goods_all['food'].price * FARMER_OUTPUT_FOOD,
            'retailer': m_goods.goods_all['goods_c'].price * RETAILER_OUTPUT_GOODS,
            'driver': m_goods.goods_all['transport'].price * DRIVER_OUTPUT_TRANSPORT,
            'student': INCOME_STUDENT
        }
level_2_jobs = {'clerk': INCOME_CLERK}
level_3_jobs = {'academics': INCOME_ACADEMICS}

available_jobs = [Farmer(), Retailer(), Driver()]  # Available job types
jobs_incomes = []


def update_monthly():
    global level_1_jobs
    level_1_jobs.update({
            'farmer': m_goods.goods_all['food'].price * FARMER_OUTPUT_FOOD,
            'retailer': m_goods.goods_all['goods_c'].price * RETAILER_OUTPUT_GOODS,
            'driver': m_goods.goods_all['transport'].price * DRIVER_OUTPUT_TRANSPORT,
        })
