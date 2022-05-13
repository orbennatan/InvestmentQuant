import os
import sys
from importlib import import_module
from BaseClass import BaseClass
from MyConstants import PathConstants, GeneralConstants

configs = sys.argv
executable_path = sys.argv[0]
conf_module = sys.argv[1]  # a name of .py file without the .py extension just as you use it in import statement
conf = import_module(conf_module).Conf
executable_folder_path = os.path.dirname(executable_path)
conf_full_file_name = f'{conf_module}.py'
conf_path = os.path.join(executable_folder_path, conf_full_file_name)
conf[PathConstants.ConfFilePath] = conf_path

agg = BaseClass.instantiate_class(conf, conf[GeneralConstants.Strategy])
