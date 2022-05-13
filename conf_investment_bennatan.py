# Configuration data only. We use .py instead of json so as to allow using of constants instead of strings
from BrokerIBKR import BrokerIBKR
from MyConstants import PathConstants, GeneralConstants, TimeConstants
from MyConstants import ClassConstants
# from StrategyQuant import StrategyQuant
from StrategyBase import StrategyBase

# Paper Account - Account Number: DU4363640, username: yigael547, Password: Ariel2013

Conf = {
    PathConstants.RootFolder: "C:\\git\\InvestmentQuant",
    GeneralConstants.Strategy: ClassConstants.StrategyQuant,
    GeneralConstants.Classes: {
        ClassConstants.StrategyQuant: {
            # PathConstants.AggregatorFileName: "AggregatedInvestments.csv", - from other project
            StrategyBase.Accounts: ['DU4363640'],
            # for Or enter 0. for AdamRoni enter 1. for DanielYoni enter 2. for Michal enter 3.
            # for Avital enter 4. for Yigael enter 5. for tali enter 6. 9 for update from account only
            StrategyBase.OwnerOrdinal: 0,  # This is where you put the owner
            StrategyBase.NumberOfStocks: 20,  # This is where you put the owner
        },
        ClassConstants.StrategyBase: {StrategyBase.BrokerProvider: ClassConstants.BrokerIBKR},
        ClassConstants.BrokerIBKR: {
            BrokerIBKR.LocalAddress: "127.0.0.1",
            BrokerIBKR.Port: "7495",
            BrokerIBKR.ClientID: "13"
        },
    }
}
