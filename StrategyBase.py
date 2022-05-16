from BaseClass import BaseClass
from BrokerBase import BrokerBase
from Logger import log

"""
A strategy class.
"""


class StrategyBase(BaseClass):
    BrokerProvider = 'BrokerProvider'
    Accounts = 'Accounts'
    Owners = 'Owners'
    OwnerOrdinal = 'OwnerOrdinal'
    NumberOfStocks = 'NumberOfStocks'  # Number of stocks this strategy handles
    CurrencyUnit = 'CurrencyUnit'  # $ Amount per trade
    AccountValues = 'AccountValues'

    def __init__(self, conf):
        super().__init__()  # We need this call in order to call the ABC __init__ method
        self.global_conf = conf
        self.class_conf = super().config_class(self, conf)
        self.broker: BrokerBase = super().instantiate_class(conf, self.class_conf[self.BrokerProvider])
        self.account_total = 0

        # Get account values
        class_conf = self.class_conf
        broker = self.broker
        account = class_conf[self.Accounts][class_conf[self.OwnerOrdinal]]
        class_conf[self.AccountValues] = broker.get_account_values(account)
        log.info(message={class_conf[self.AccountValues]})

    def initialise_strategy(self, account):

        pass

    def execute_strategy(self, account):

        pass

    def teardown_strategy(self, account):

        pass
