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
    Next Version - For now database only for writing
        Get the latest state from Database
        If Same date - compare states and report error on differences
            Cache And Stock Value differences are Expected.
            Stock amount values differences are Unexpected
    Save latest state
    """
    def __init__(self, conf):
        super().__init__(conf)  # We need this call in order to call the ABC __init__ method
        self.get_account_values_from_broker(conf)

    def initialise_strategy(self, account):

        pass

    def execute_strategy(self, account):

        pass

    def teardown_strategy(self, account):

        pass
