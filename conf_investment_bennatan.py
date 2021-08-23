# Configuration data only. We use .py instead of json so as to allow using of constants instead of strings

from MyConstants import PathConstants as PC, GeneralConstants as GC, TimeConstants as TC
from MyConstants import ClassConstants as CC
from BrokerBase import BrokerBase as BB
from BrokerIBKR import BrokerIBKR as BI
from AggregatorPercentageParticipants import AggregatorPercentageParticipants as AP
from AggregatorBase import AggregatorBase as AB

Conf = {
    PC.RootFolder: "C:\\Users\\orben\\OneDrive\\DekelReceiptSendingFolder\\AggregatedInvestments",
    GC.Aggregator: CC.AggregatorPercentageParticipants,
    GC.Classes: {
        # CC.AggregatorPercentageParticipants: {
        #     AP.AggregatorFileName: "AggregatedInvestments.csv",
        #     AP.InitialState: {TC.Date: '2020-09-04 01:01:01', GC.Total: 1394539, 'Or': 1339808, 'AdamRoni': 20207,
        #                       'DanielYoni': 26813, 'Michal': 7711, GC.Comments: ['Start']},
        #     AB.Accounts: ['U1357738', 'U1378906', 'U3279997', 'U4502628', 'U4566811']
        #
        # },
        # CC.AggregatorPercentageParticipants: {
        #     AP.AggregatorFileName: "AggregatedInvestments.csv",
        #     AP.InitialState: {TC.Date: '2021-01-31 01:01:01', GC.Total: 1737261, 'Or': 1647930, 'AdamRoni': 41549,
        #                       'DanielYoni': 27782, 'Michal': 18164, 'Avital': 1833, 'Yigael': 1,
        #                       GC.Comments: ['Add Avital and Yigael']},
        #     AB.Accounts: ['U1357738', 'U1378906', 'U3279997', 'U4502628', 'U4566811']
        #
        # },
        CC.AggregatorPercentageParticipants: {
            AP.AggregatorFileName: "AggregatedInvestments.csv",
            AP.PercentagesFileName: "AggregatedInvestmentsPercentages.csv",
            AP.InitialState: {TC.Date: '2021-02-18 01:01:01', GC.Total: 1737261, 'Or': 1647930, 'AdamRoni': 41549,
                              'DanielYoni': 27782, 'Michal': 18164, 'Avital': 1833, 'Yigael': 1, 'tali': 0,
                              GC.Comments: ['Add Tali']},
            AB.Accounts: ['U3279997', 'U6112146'],
            #for Or enter 0. for AdamRoni enter 1. for DanielYoni enter 2. for Michal enter 3.
            # for Avital enter 4. for Yigael enter 5. for tali enter 6. 9 for update from account only
            AP.OwnerOrdinal: 0, # This is where you put the owner
            AP.Change: 37111 # Enter negative if owner reduces only.

        },
        CC.AggregatorBase: {AP.BrokerProvider: CC.BrokerIBKR},
        CC.BrokerIBKR: {
            BI.LocalAddress: "127.0.0.1",
            BI.Port: "7495",
            BI.ClientID: "13"
        },

    }
}
