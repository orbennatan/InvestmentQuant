from StrategyBase import StrategyBase

"""
A strategy class.
"""


class StrategyQuant(StrategyBase):

    """ Init Logic
    Load latest configurations from .py file
    Get current state from TWS
    Get latest state from Database
    If Same date - compare states and report error on differences
        Cache And Stock Value differences are Expected.
        Stock amount values differences are Unexpected
    Else - Save latest state
    """
    def __init__(self, conf):
        super().__init__()  # We need this call in order to call the ABC __init__ method
        self.global_conf = conf
        self.class_conf = super().config_class(self, conf)

    def initialise_strategy(self, account):

        pass

    def execute_strategy(self, account):

        pass

    def teardown_strategy(self, account):

        pass
