from BrokerBase import BrokerBase
from IBKR import TestApp, AccountValues as AV


class BrokerIBKR(BrokerBase):
    Port = 'Port'
    LocalAddress = 'LocalAddress'
    ClientID = 'ClientID'
    Value = 'value'
    Key = 'key'
    NetLiquidation = 'NetLiquidation'
    # We don't want to create a dependency between clients of BrokerIBKR and the IBKR module hence the dict translation
    error_dict = {AV.ErrorTimeOut: BrokerBase.TimeOutError, AV.OK: BrokerBase.OK}

    def __init__(self, conf):
        super().__init__(conf)  # We need this call in order to call the ABC __init__ method
        self.connection = TestApp(self.class_conf[self.LocalAddress], int(self.class_conf[self.Port]),
                                  int(self.class_conf[self.ClientID]))
        pass

    def get_account_values(self, account):
        account_values, error = self.connection.get_account(account)
        account_dict = {}
        for value in account_values:
            account_dict[value[self.Key]] = value[self.Value]
        return account_dict[self.NetLiquidation], self.error_dict[error]
