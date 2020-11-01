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
        CC.AggregatorPercentageParticipants: {
            AP.AggregatorFileName: "AggregatedInvestments.csv",
            AP.InitialState: {TC.Date: '2020-09-04 01:01:01', GC.Total: 1394539, 'Or': 1339808, 'AdamRoni': 20207,
                              'DanielYoni': 26813, 'Michal': 7711, GC.Comments: ['Start']},
            AB.Accounts: ['U1357738', 'U1378906', 'U3279997', 'U4502628', 'U4566811']

        },
        CC.AggregatorBase: {AP.BrokerProvider: CC.BrokerIBKR},
        CC.BrokerIBKR: {
            BI.LocalAddress: "127.0.0.1",
            BI.Port: "7495",
            BI.ClientID: "12"
        },

    }
}
