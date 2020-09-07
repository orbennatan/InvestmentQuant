from BaseClass import BaseClass

"""
Clases inheriting from this class calculate the quality of the trade in many different manners. 
They take a series and period size as input and return a series back. The operation is based on the oportinitues
offered by pandas functions like pct_change or rolling.apply save the need for loops on dataframes and serieses 
Important: The returned value must have the input returned as the first 
"""


class HelloWorld(BaseClass):
    Printer = 'Printer'
    StringToPrint = 'StringToPrint'

    def __init__(self, conf):
        super().__init__()  # We need this call in order to call the ABC __init__ method
        self.global_conf = conf
        self.class_conf = super().config_class(self, conf)

    def hello_world(self):
        print(self.class_conf[self.StringToPrint])
