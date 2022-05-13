from BaseClass import BaseClass
from BrokerBase import BrokerBase

"""
A broker class attempting to encapsulate all brokers in a single API. We only know about IBKR when writing
this class so it is probably heavily biased toward IBKR.
"""


class AggregatorBase(BaseClass):
    BrokerProvider = 'BrokerProvider'
    Accounts = 'Accounts'
    Owners = 'Owners'

    def __init__(self, conf):
        super().__init__()  # We need this call in order to call the ABC __init__ method
        self.global_conf = conf
        self.class_conf = super().config_class(self, conf)
        self.broker: BrokerBase = super().instantiate_class(conf, self.class_conf[self.BrokerProvider])
        self.account_total = 0

    def create_pdf_from_csv(self):
        # read the csv from the one defined in class_conf into self.df. Print it out
        pass

    def update_total_from_accounts(self):
        self.get_total_from_all_accounts()
        # read totals from all accounts. Update the self.df including the amount each owner has.
        pass

    def input_owner_name(self)->str:
        # prompt user to enter the owner using a number. Print the names with the ordinal numbers and ask for a
        # single digit to be entered Tell the user 0 means we are done updating, and it is time to quit the program.
        pass

    def input_sum_to_update(self):
        # prompt for sum to be entered.
        pass

    def update_ownership_values(self, owner, amount):
        # Create new ownership values: Each class will do it in its way.
        pass

    def get_total_from_all_accounts(self):
        pass