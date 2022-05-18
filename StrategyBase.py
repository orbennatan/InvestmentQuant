from BaseClass import BaseClass
from BrokerBase import BrokerBase
from IBKR import AccountValues
from Logger import log
from BrokerState import BrokerState
from BrokerInstrument import BrokerInstrument

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
    BrokerAccountValues = 'BrokerAccountValues'

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
        class_conf[self.BrokerAccountValues], error = broker.get_account_values(account)
        if error != AccountValues.OK:
            log.error(message=error)
            raise Exception(error)
        log.info(message={class_conf[self.BrokerAccountValues]})
        self.brokerState = BrokerState()
        self.brokerState.AvailableFunds = float(class_conf[self.BrokerAccountValues])
        log.info(message=f'AvailableFunds {self.brokerState.AvailableFunds}')
        self.brokerState.instrumentDict = broker.get_positions(conf)
        log.info(message=f'Positions {self.brokerState.instrumentDict}')


    def initialise_strategy(self, account):

        pass

    def execute_strategy(self, account):

        pass

    def teardown_strategy(self, account):

        pass
