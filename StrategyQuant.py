import logging

from Logger import log
from MyConstants import DatabaseConstants
from StrategyBase import StrategyBase

"""
A strategy class.
"""


class StrategyQuant(StrategyBase):

    """ Init Logic
    Load the latest configurations from .py file - StrategyBase
    Get current state from TWS
    Get the latest state from Database
    If Same date - compare states and report error on differences
        Cache And Stock Value differences are Expected.
        Stock amount values differences are Unexpected
    Else - Save latest state
    """
    def __init__(self, conf):
        super().__init__(conf)  # We need this call in order to call the ABC __init__ method
        self.get_account_values_from_broker(conf)
        database_broker_state = self.database.get_last_row(DatabaseConstants.StateTable)
        log.info(f'{database_broker_state}')
        StrategyQuant.validate_database_broker_state(broker_state=database_broker_state)

    def initialise_strategy(self, account):

        pass

    def execute_strategy(self, account):

        pass

    def teardown_strategy(self, account):

        pass

    @staticmethod
    def validate_database_broker_state(broker_state):
