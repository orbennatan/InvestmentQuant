# This file contain constants for several categories. Each category is defined as a class
class ClassConstants:
    StrategyBase = 'StrategyBase'
    StrategyQuant = 'StrategyQuant'
    HelloWorld = 'HelloWorld'
    BrokerBase = 'BrokerBase'
    BrokerIBKR = 'BrokerIBKR'
    DatabaseBase = 'DatabaseBase'
    DatabaseAccess = 'DatabaseAccess'
    BaseClass = 'BaseClass'
    Classes = 'classes'
    ConfSecond = 'conf_second'
    Folder_ = 'folder_'
    File_ = 'file_'
    Conf_ = 'conf_'
    Name = 'Name'


class AttributeConstants:
    pass


class PathConstants:
    RootFolder = 'root_folder'
    ConfFilePath = 'conf_file_path'
    FileList = 'file_list'
    ErrorFileNotFound = 'error_file_not_found'
    Folders = 'folders'
    Files = 'files'


class GeneralConstants:
    Classes = 'classes'
    Hyperparameter = 'hyperparameter'
    Strategy = 'Strategy'
    Comments = 'Comments'
    Total = 'Total'
    RunMode = 'RunMode'
    RunModeDebug = 'RunModeDebug'


class ErrorConstants:
    OK = 'OK'
    AttributeNotSupported = 'attribute_not_supported'


class TimeConstants:
    StartDate = 'start_date'
    EndDate = 'end_date'
    Date = 'date'
    DateFormatHyphens = '%Y-%m-%d'


class DatabaseConstants:
    StateTable = 'State'
    StateRowIdInd = 0
    StateRowCacheInd = 1
    StateRowNumStocksInd = 2
    StateRowDateInd = 3
    StateRowStateJsonInd = 4
