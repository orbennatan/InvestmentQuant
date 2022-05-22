# Configuration data only. We use .py instead of json so as to allow using of constants instead of strings
from BrokerIBKR import BrokerIBKR
from DatabaseAccess import DatabaseAccess
from MyConstants import PathConstants, GeneralConstants
from MyConstants import ClassConstants
# from StrategyQuant import StrategyQuant
from StrategyBase import StrategyBase

# Paper Account - Account Number: DU4363640, username: yigael547
# Rea Account - Account Number: U6947311, username: yigaelbennatan

Conf = {
    PathConstants.RootFolder: "C:\\git\\InvestmentQuant",
    GeneralConstants.Strategy: ClassConstants.StrategyQuant,
    GeneralConstants.RunMode: GeneralConstants.RunModeDebug,
    GeneralConstants.Classes: {
        ClassConstants.StrategyQuant: {
            # PathConstants.AggregatorFileName: "AggregatedInvestments.csv", - from other project
            StrategyBase.Accounts: ['DU4363640', 'U6947311'],
            # This is where you put the owner.
            # - 0 - Yigael Paper Account
            # - 1 - Yigael Live Account
            StrategyBase.OwnerOrdinal: 0,
            StrategyBase.NumberOfStocks: 20,
            StrategyBase.CurrencyUnit: 20000,
            StrategyBase.BrokerAccountValues: {}
        },
        ClassConstants.StrategyBase: {
            StrategyBase.BrokerProvider: ClassConstants.BrokerIBKR,
            StrategyBase.DatabaseProvider: ClassConstants.DatabaseAccess
        },
        ClassConstants.BrokerIBKR: {
            BrokerIBKR.LocalAddress: "127.0.0.1",
            BrokerIBKR.Port: "7495",
            BrokerIBKR.ClientID: "13"
        },
        ClassConstants.DatabaseAccess: {
            DatabaseAccess.DatabaseFilePath: "Database\\InvestmentQuant.accdb"
        },
    }
}
