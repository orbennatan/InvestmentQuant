from BaseClass import BaseClass

"""
A strategy class.
"""


class StrategyBase(BaseClass):

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
