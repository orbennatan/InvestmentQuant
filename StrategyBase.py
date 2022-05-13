from BaseClass import BaseClass
from BrokerBase import BrokerBase

"""
A strategy class.
"""


class StrategyBase(BaseClass):
    BrokerProvider = 'BrokerProvider'
    Accounts = 'Accounts'
    Owners = 'Owners'
    OwnerOrdinal = 'OwnerOrdinal'
    NumberOfStocks = 'NumberOfStocks'  # Number of stocks this strategy handles

    def __init__(self, conf):
        super().__init__()  # We need this call in order to call the ABC __init__ method
        self.global_conf = conf
        self.class_conf = super().config_class(self, conf)
        self.broker: BrokerBase = super().instantiate_class(conf, self.class_conf[self.BrokerProvider])
        self.account_total = 0

    def initialise_strategy(self, account):

        pass

    def execute_strategy(self, account):

        pass

    def teardown_strategy(self, account):

        pass
