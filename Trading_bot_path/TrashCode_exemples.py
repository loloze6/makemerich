# pnl_net_total = result[0].analyzers.trade.get_analysis().pnl.net.total
# print("Total PnL: {}".format(pnl_net_total))

# data_btc=fetchData(token='BTC/USDT',barDuration='15m',start='2018-01-01T00:00:00Z', duration = 700)
# dataBT_btc=data_btc['BT_DataFeed']

# data_eth=fetchData(token='ETH/USDT',barDuration='15m',start='2018-01-01T00:00:00Z', duration = 700)
# dataBT_eth=data_eth['BT_DataFeed']
from abc import ABC, abstractmethod

class hr:
    class PayrollSystem:
        def calculate_payroll(self, employees):
            print('Calculating Payroll')
            print('===================')
            for employee in employees:
                print(f'Payroll for: {employee.id} - {employee.name}')
                print(f'- Check amount: {employee.calculate_payroll()}')
                print('')
                
    class Employee(ABC):
        def __init__(self, id, name):
            self.id = id
            self.name = name

        @abstractmethod
        def calculate_payroll(self):
            pass     
            
    class SalaryEmployee(Employee):
        def __init__(self, id, name, weekly_salary):
            super().__init__(id, name)
            self.weekly_salary = weekly_salary

        def calculate_payroll(self):
            return self.weekly_salary
        
    class HourlyEmployee(Employee):
        def __init__(self, id, name, hours_worked, hour_rate):
            super().__init__(id, name)
            self.hours_worked = hours_worked
            self.hour_rate = hour_rate

        def calculate_payroll(self):
            return self.hours_worked * self.hour_rate
        
    class CommissionEmployee(SalaryEmployee):
        def __init__(self, id, name, weekly_salary, commission):
            super().__init__(id, name, weekly_salary)
            self.commission = commission

        def calculate_payroll(self):
            fixed = super().calculate_payroll()
            return fixed + self.commission
    class DisgruntledEmployee:
        def __init__(self, id, name):
            self.id = id
            self.name = name

        def calculate_payroll(self):
            return 1000000
employee = hr.Employee(1, 'Invalid')
payroll_system.calculate_payroll([employee])
salary_employee = hr.SalaryEmployee(1, 'John Smith', 1500)
hourly_employee = hr.HourlyEmployee(2, 'Jane Doe', 40, 15)
commission_employee = hr.CommissionEmployee(3, 'Kevin Bacon', 1000, 250)
payroll_system = hr.PayrollSystem()
payroll_system.calculate_payroll([
    salary_employee,
    hourly_employee,
    commission_employee
])
dir(salary_employee)

def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

def say_whee():
    print("Whee!")

say_whee = my_decorator(say_whee)
