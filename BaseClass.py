import datetime
import json
from importlib import import_module
import numpy

from Logger import log
from MyConstants import ClassConstants
from MyConstants import TimeConstants, PathConstants


class BaseClass:

    @staticmethod
    def instantiate_class(conf, class_name):
        # All our classes accept the conf file as a paramter for construction
        # Assume that like in Java, each class is in its own module with the same name
        try:
            module = import_module(class_name)  # Here we assume one class in each module with the same name
            class_object = getattr(module, class_name)
            class_instance = class_object(conf)
        except Exception as ex:
            log.error(f'{ex}')
            raise ex
        return class_instance

    @staticmethod
    def config_class(self, conf) -> dict:
        self.root_folder = conf[PathConstants.RootFolder]
        # class_name = type(self).__name__
        current_class_object = type(self)
        # Create class_conf dict based on all keys found in parent class with child class overriding parents
        parents = current_class_object.mro()
        class_conf = {}
        for class_object in reversed(parents):  # From higher to lower in the hierarchy
            class_name = class_object.__name__
            if class_name not in conf[ClassConstants.Classes].keys():
                continue
            temp_conf = conf[ClassConstants.Classes][class_name]
            for key, value in temp_conf.items():
                class_conf[key] = value  # Lower in the hierarchy overrides keys that were defined in parent classes
        self.class_conf = class_conf
        return class_conf

        # for key, value in class_conf:
        #     if key.startswith(ClassConstants.Folder_):  # Create a folder path and create the folder if it doesn't exist
        #         folder_name = f'{class_name}_{value.replace(ClassConstants.Folder_, "")}'
        #         folder_path = join(root_folder, folder_name)
        #         makedirs(folder_path, exist_ok=True)
        #
        #         class_conf[value] = folder_path
        #     elif value.startswith(ClassConstants.File_):  # Create a file path.
        #         # file_name = f'{class_name}_{key.replace(CNST.File_,"")}'
        #         setattr(type(self), value, conf[ClassConstants.Classes][class_name][value])
        #
        #         file_path = join(root_folder, conf[ClassConstants.Classes][class_name][value])
        #         setattr(type(self), value, file_path)

    @staticmethod
    def read_json(path: str) -> dict:
        with open(path, 'r') as fp:
            my_dict = json.load(fp)
        return my_dict

    @staticmethod
    def today_string():
        return datetime.date.today().strftime(TimeConstants.DateFormatHyphens)

    @staticmethod
    def today_datetime_string():
        return datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    @staticmethod
    def second_ago_string():
        time_now = datetime.datetime.now()
        second_ago = datetime.datetime.now() - datetime.timedelta(seconds=1)
        #print(f'now = {time_now}, second_ago = {second_ago}')
        return second_ago.strftime("%Y-%m-%d, %H:%M:%S")

    @staticmethod
    def get_range_for_last_business_day() -> (str, str):
        date_today = datetime.date.today()
        date_last_week = date_today - datetime.timedelta(days=4)
        date_format = "%Y-%m-%d"
        today_string = date_today.strftime(date_format)
        to_date_object = datetime.datetime.strptime(today_string, TimeConstants.DateFormatHyphens)
        yesterday = to_date_object - datetime.timedelta(days=1)
        yesterday_string = yesterday.strftime(TimeConstants.DateFormatHyphens)
        last_week_string = date_last_week.strftime(date_format)
        return (last_week_string, yesterday_string)

    def print_ds(self, ds):
        for inputs, labels in ds.take(3):
            print(inputs.numpy(), "=>", labels.numpy())

    def normalize_0_to_1(self, array):
        x = ((array - numpy.min(array)) / (numpy.linalg.norm(array - numpy.min(array)))) * 1000
        return x.astype(int)
