from BaseClass import BaseClass

"""
A broker class attempting to encapsulate all brokers in a single API. We only know about IBKR when writing
this class so it is probably heavily biased towared IBKR.
"""


class BrokerBase(BaseClass):
    Account = 'Account'
    Accounts = 'Accounts'
    TimeOutError = 'TimeOutError'
    OK = 'OK'


    def __init__(self, conf):
        super().__init__()  # We need this call in order to call the ABC __init__ method
        self.global_conf = conf
        self.class_conf = super().config_class(self, conf)

    def get_account_values(self, account):

        pass
