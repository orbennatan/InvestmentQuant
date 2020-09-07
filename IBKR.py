# This is a set of classes and method written to connect with IBKR
# It has nothing to do with our way of doing classes
# Our BrokerIBKR class uses the classes and methods here to do its job
# The main purpose of the classes here is to turn the initiate and call back structure of IB API to regular
# call which waits for the data.
# Gist example of IB wrapper ...
#
# Download API from http://interactivebrokers.github.io/#
#
# Install python API code /IBJts/source/pythonclient $ python3 setup.py install
#
# Note: The test cases, and the documentation refer to a python package called IBApi,
#    but the actual package is called ibapi. Go figure.
#
# Get the latest version of the gateway:
# https://www.interactivebrokers.com/en/?f=%2Fen%2Fcontrol%2Fsystemstandalone-ibGateway.php%3Fos%3Dunix
#    (for unix: windows and mac users please find your own version)
#
# Run the gateway
#
# user: edemo
# pwd: demo123
#
# Now I'll try and replicate the historical data example

from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract as IBContract
from ibapi.order import Order

from threading import Thread
import queue
import datetime
import pandas as pd
from ConfigurationCommon import Conf
from Classes import Dicts
from Classes import MyOrder
from Classes import SymbolHistory as SH
from Classes import SymbolMeta as SM
from Classes import Position
from Classes import AccountValues as AV
from Classes import NewsProvider as NP
from Classes import News

## these are just arbitrary numbers in leiu of a policy on this sort of thing
DEFAULT_HISTORIC_DATA_ID = 50
DEFAULT_GET_CONTRACT_ID = 43
DEFAULT_EXEC_TICKER = 78
DEFAULT_GET_POSITIONS = 57
DEFAULT_GET_STOPS = 64
DEFAULT_GET_ACCOUNT = 71
DEFAULT_GET_NEWS_PROVIDERS = 85
DEFAULT_GET_NEWS_HEADERS = 92
DEFAULT_GET_NEWS_ARTICLE = 98

## marker for when queue is finished
FINISHED = object()
STARTED = object()
TIME_OUT = object()

## This is the reqId IB API sends when a fill is received
FILL_CODE = -1
init_open_order_done = False

class AccountValues():
    ErrorTimeOut = 'error_timeout'
    OK = 'OK'
    Value = 'value'
    Key = 'key'
    Account = 'account'
    TotalCashBalance = 'TotalCashBalance'  # This must conform to the list of parameters in updateAccountValues)

class finishableQueue(object):

    def __init__(self, queue_to_finish):

        self._queue = queue_to_finish
        self.status = STARTED

    def get(self, timeout):
        """
        Returns a list of queue elements once timeout is finished, or a FINISHED flag is received in the queue
        :param timeout: how long to wait before giving up
        :return: list of queue elements
        """
        contents_of_queue = []
        finished = False

        while not finished:
            try:
                current_element = self._queue.get(timeout=timeout)
                if current_element is FINISHED:
                    finished = True
                    self.status = FINISHED
                else:
                    contents_of_queue.append(current_element)
                    ## keep going and try and get more data

            except queue.Empty:
                ## If we hit a time out it's most probable we're not getting a finished element any time soon
                ## give up and return what we have
                finished = True
                self.status = TIME_OUT

        return contents_of_queue

    def timed_out(self):
        return self.status is TIME_OUT


"""
Now into the main bit of the code; Wrapper and Client objects
"""


class TestWrapper(EWrapper):
    """
    The wrapper deals with the action coming back from the IB gateway or TWS instance
    We override methods in EWrapper that will get called when this action happens, like currentTime
    Extra methods are added as we need to store the results in this object
    """

    def __init__(self):
        self._my_contract_details = {}
        self._my_requested_execution = {}
        self._my_open_orders = {}
        self._my_historic_data_dict = {}
        self._my_positions_dict = {}
        self._my_account_dict = {}
        self._my_news_providers_dict = {}
        self._my_news_headers_dict = {}
        self._my_news_article_dict = {}

    # error handling code
    def init_error(self):
        error_queue = queue.Queue()
        self._my_errors = error_queue

    def get_error(self, timeout=5):
        if self.is_error():
            try:
                return self._my_errors.get(timeout=timeout)
            except queue.Empty:
                return None

        return None

    def is_error(self):
        an_error_if = not self._my_errors.empty()
        return an_error_if

    def error(self, id, errorCode, errorString):
        ## Overriden method
        errormsg = "IB error id %d errorcode %d string %s" % (id, errorCode, errorString)
        self._my_errors.put(errormsg)

    # get contract details code
    def init_contractdetails(self, reqId):
        contract_details_queue = self._my_contract_details[reqId] = queue.Queue()
        return contract_details_queue

    def contractDetails(self, reqId, contractDetails):
        ## overridden method

        if reqId not in self._my_contract_details.keys():
            self.init_contractdetails(reqId)

        self._my_contract_details[reqId].put(contractDetails)

    def contractDetailsEnd(self, reqId):
        ## overriden method
        if reqId not in self._my_contract_details.keys():
            self.init_contractdetails(reqId)

        self._my_contract_details[reqId].put(FINISHED)

    # News article
    def init_news_article(self, reqId):
        news_article_queue = self._my_news_article_dict[reqId] = queue.Queue()
        return news_article_queue

    def newsArticle(self, requestId, articleType, articleText):
        ## overridden method

        if requestId not in self._my_news_article_dict.keys():
            self.init_news_article(requestId)
        article_dict = {News.ArticleType: articleType, News.ArticleText: articleText}
        self._my_news_article_dict[requestId].put(article_dict)
        self._my_news_article_dict[requestId].put(FINISHED)

    # news headers
    def init_historical_news_headers(self, tickerid):
        historic_news_data_queue = self._my_news_headers_dict[tickerid] = queue.Queue()
        return historic_news_data_queue

    def historicalNews(self, requestId, time, providerCode, articleId, headline):
        ## Overriden method
        ## Note I'm choosing to ignore barCount, WAP and hasGaps but you could use them if you like
        historic_news_header_dict = self._my_news_headers_dict
        ## Add on to the current data
        if requestId not in historic_news_header_dict.keys():
            self.init_historical_news_headers(requestId)
        if ' ' in time:
            article_date_time_list = time.split(' ')
            if len(article_date_time_list) != 2:
                print(f'time format error in {articleId}, time = {time}')
                return
            article_date = article_date_time_list[0]
            article_time = article_date_time_list[1]
        else:
            print(f'time format error in {articleId}, time = {time}')
            return
        header_dict = {News.ArticleID: articleId, News.Headline: headline, News.Date: article_date,
                       News.Time: article_time, News.Provider: providerCode}
        historic_news_header_dict[requestId].put(header_dict)

    def historicalNewsEnd(self, requestId, hasMore):
        print(f'hasmore = {hasMore}')
        ## overriden method
        if requestId not in self._my_news_headers_dict.keys():
            self.init_historicprices(requestId)
        if hasMore:
            header_dict = {News.ArticleID: News.HasMore, News.Headline: News.HasMore}
        else:
            header_dict = {News.ArticleID: News.NoMore, News.Headline: News.NoMore}
        self._my_news_headers_dict[requestId].put(header_dict)
        self._my_news_headers_dict[requestId].put(FINISHED)

    # orders
    def init_open_orders(self):
        open_orders_queue = self._my_open_orders = queue.Queue()
        global init_open_order_done
        init_open_order_done = True
        return open_orders_queue

    def openOrder(self, orderId, contract, order, orderstate):
        """
        Tells us about any orders we are working now
        overriden method
        """
        ## Add on to the current data
        if init_open_order_done:
            order_details = {MyOrder.OrderID: orderId, MyOrder.Conctract: contract, MyOrder.OrderObject: order,
                             MyOrder.OrderState: orderstate}
            self._my_open_orders.put(order_details)

    def openOrderEnd(self):
        """
        Finished getting open orders
        Overriden method
        """
        if init_open_order_done:
            self._my_open_orders.put(FINISHED)

    ## order ids
    def init_nextvalidid(self):

        orderid_queue = self._my_orderid_data = queue.Queue()

        return orderid_queue

    def nextValidId(self, orderId):
        """
        Give the next valid order id
        Note this doesn't 'burn' the ID; if you call again without executing the next ID will be the same
        If you're executing through multiple clients you are probably better off having an explicit counter
        """
        if getattr(self, '_my_orderid_data', None) is None:
            ## getting an ID which we haven't asked for
            ## this happens, IB server just sends this along occassionally
            self.init_nextvalidid()

        self._my_orderid_data.put(orderId)

    ## Historic data code
    def init_historicprices(self, tickerid):
        historic_data_queue = self._my_historic_data_dict[tickerid] = queue.Queue()

        return historic_data_queue

    def historicalData(self, tickerid, bar):

        ## Overriden method
        ## Note I'm choosing to ignore barCount, WAP and hasGaps but you could use them if you like
        bardata = (bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume)

        historic_data_dict = self._my_historic_data_dict

        ## Add on to the current data
        if tickerid not in historic_data_dict.keys():
            self.init_historicprices(tickerid)
        # print(historic_data_dict)
        historic_data_dict[tickerid].put(bardata)

    def historicalDataEnd(self, tickerid, start: str, end: str):
        ## overriden method

        if tickerid not in self._my_historic_data_dict.keys():
            self.init_historicprices(tickerid)
        self._my_historic_data_dict[tickerid].put(FINISHED)

    ## news providers code
    def init_news_providers(self, tickerid):
        news_providers_data_queue = self._my_news_providers_dict[tickerid] = queue.Queue()

        return news_providers_data_queue

    def newsProviders(self, newsProviders):
        print("NewsProviders: ")
        for provider in newsProviders:
            print("NewsProvider.", provider)

        news_providers_dict = self._my_news_providers_dict

        ## Add on to the current data
        news_providers_dict[DEFAULT_GET_NEWS_PROVIDERS].put(newsProviders)
        news_providers_dict[DEFAULT_GET_NEWS_PROVIDERS].put(FINISHED)  # note that

    def init_account(self, tickerid):
        account_queue = self._my_account_dict[DEFAULT_GET_ACCOUNT] = queue.Queue()
        return account_queue

    def updateAccountValue(self, key, value, currency, accountName):
        super().updateAccountValue(key, value, currency, accountName)
        value = {AV.Account: accountName, AV.Value: value, AV.Key: key}
        account_values_dict = self._my_account_dict

        ## Add on to the current data
        if DEFAULT_GET_ACCOUNT not in account_values_dict.keys():
            self.init_account(DEFAULT_GET_ACCOUNT)

        account_values_dict[DEFAULT_GET_ACCOUNT].put(value)

    def accountDownloadEnd(self, account):
        if DEFAULT_GET_ACCOUNT not in self._my_account_dict.keys():
            self.init_account(DEFAULT_GET_POSITIONS)

        self._my_account_dict[DEFAULT_GET_ACCOUNT].put(FINISHED)

    def init_positions(self, tickerid):
        positions_queue = self._my_positions_dict[DEFAULT_GET_POSITIONS] = queue.Queue()
        return positions_queue

    def position(self, account: str, contract: IBContract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)

        ## Overriden method

        positions = {Position.Account: account, Position.Symbol: contract.symbol, Position.Amount: position,
                     Position.AvgCost: avgCost}

        positions_dict = self._my_positions_dict

        ## Add on to the current data
        if DEFAULT_GET_POSITIONS not in positions_dict.keys():
            self.init_positions(DEFAULT_GET_POSITIONS)

        positions_dict[DEFAULT_GET_POSITIONS].put(positions)

    def positionEnd(self):
        ## overriden method

        if DEFAULT_GET_POSITIONS not in self._my_positions_dict.keys():
            self.init_positions(DEFAULT_GET_POSITIONS)

        self._my_positions_dict[DEFAULT_GET_POSITIONS].put(FINISHED)


class TestClient(EClient):

    def print_error_queue(self):
        i = 0
        while self.wrapper.is_error():
            print(self.get_error())
            i += 1

    def get_error_queue(self):
        errors = []
        while self.wrapper.is_error():
            errors.append(self.get_error())
        return errors

    """
    The client method
    We don't override native methods, but instead call them from our own wrappers
    """

    def __init__(self, wrapper):
        ## Set up with a wrapper inside
        EClient.__init__(self, wrapper)

    def resolve_ib_contract(self, ibcontract, reqId=DEFAULT_GET_CONTRACT_ID):

        """
        From a partially formed contract, returns a fully fledged version
        :returns fully resolved IB contract
        """

        ## Make a place to store the data we're going to return
        contract_details_queue = finishableQueue(self.init_contractdetails(reqId))

        print("Getting full contract details for", ibcontract)

        self.reqContractDetails(reqId, ibcontract)

        ## Run until we get a valid contract(s) or get bored waiting
        MAX_WAIT_SECONDS = 60
        new_contract_details = contract_details_queue.get(timeout=MAX_WAIT_SECONDS)

        while self.wrapper.is_error():
            error = self.get_error()
            if not (("errorcode 2104" in error)
                    or ("errorcode 2106" in error)
                    or ("error code 2108")):
                print(error)
                return 0, error

        if contract_details_queue.timed_out():
            error = "Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour"
            print(error)
            return ibcontract, error

        if len(new_contract_details) == 0:
            error = "Failed to get additional contract details: returning unresolved contract"
            print(error)
            return ibcontract, error

        if len(new_contract_details) > 1:
            print("got multiple contracts using first one")

        new_contract_details = new_contract_details[0]

        resolved_ibcontract = new_contract_details.contract

        return resolved_ibcontract, "OK"

    def get_news_article(self, providerCode, articleId, reqId=DEFAULT_GET_NEWS_ARTICLE):
        news_article_queue = finishableQueue(self.init_news_article(reqId))
        self.reqNewsArticle(reqId, providerCode, articleId, None)
        MAX_WAIT_SECONDS = 20
        news_article_list_of_one = news_article_queue.get(timeout=MAX_WAIT_SECONDS)
        if news_article_queue.timed_out():
            error = "Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour"
            print(error)
            return "", News.TimeOut
        # Validate a bit more and normalize before we return
        # Check that we have text and we actually have something there.
        if len(news_article_list_of_one) == 0:
            return "", News.ArticleListZero
        news_article_dict = news_article_list_of_one[0]
        if News.ArticleText not in news_article_dict:
            return "", News.NoTextKey
        if len(news_article_dict[News.ArticleText]) == 0:
            return "", News.TextZeroLength
        return news_article_dict, News.OK

    def get_next_brokerorderid(self):
        """
        Get next broker order id
        :return: broker order id, int; or TIME_OUT if unavailable
        """

        ## Make a place to store the data we're going to return
        orderid_q = self.init_nextvalidid()

        self.reqIds(-1)  # -1 is irrelevant apparently (see IB API docs)

        ## Run until we get a valid contract(s) or get bored waiting
        MAX_WAIT_SECONDS = 20
        try:
            brokerorderid = orderid_q.get(timeout=MAX_WAIT_SECONDS)
        except queue.Empty:
            print("Wrapper timeout waiting for broker orderid")
            brokerorderid = TIME_OUT

        while self.wrapper.is_error():
            print(self.get_error(timeout=MAX_WAIT_SECONDS))

        return brokerorderid

    def place_new_IB_order(self, ibcontract, order, orderid=None):

        ## Note: It's possible if you have multiple traidng instances for orderids to be submitted out of sequence
        ##   in which case IB will break

        # Place the order
        self.placeOrder(
            orderid,  # orderId,
            ibcontract,  # contract,
            order  # order
        )

        return orderid

    def get_open_orders(self):
        """
        Returns a list of any open orders
        """

        ## store the orders somewhere
        open_orders_queue = finishableQueue(self.init_open_orders())

        ## You may prefer to use reqOpenOrders() which only retrieves orders for this client
        self.reqAllOpenOrders()

        ## Run until we get a terimination or get bored waiting

        MAX_WAIT_SECONDS = 20
        open_orders_list = open_orders_queue.get(timeout=MAX_WAIT_SECONDS)

        while self.wrapper.is_error():
            print(self.get_error())

        if open_orders_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished whilst getting orders")

        ## open orders queue will be a jumble of order details, turn into a tidy dict with no duplicates

        return open_orders_list, 'OK'

    def cancel_order(self, orderid):

        ## Has to be an order placed by this client. I don't check this here -
        ## If you have multiple IDs then you you need to check this yourself.

        self.cancelOrder(orderid)

        ## Wait until order is cancelled
        start_time = datetime.datetime.now()
        MAX_WAIT_TIME_SECONDS = 20

        finished = False

        while not finished:
            if orderid not in self.get_open_orders():
                ## finally cancelled
                finished = True

            if (datetime.datetime.now() - start_time).seconds > MAX_WAIT_TIME_SECONDS:
                print("Wrapper didn't come back with confirmation that order was cancelled!")
                finished = True

        ## return nothing

    def get_IB_historical_data_modified(self, ibcontract, durationStr="1 Y", barSizeSetting="1 day",
                                        tickerid=DEFAULT_HISTORIC_DATA_ID):

        """
        Returns historical prices for a contract, up to today
        ibcontract is a Contract
        :returns list of prices in 4 tuples: Open high low close volume
        """

        ## Make a place to store the data we're going to return
        historic_data_queue = finishableQueue(self.init_historicprices(tickerid))

        # Request some historical data. Native method in EClient
        self.reqHistoricalData(
            tickerid,  # tickerId,
            ibcontract,  # contract,
            datetime.datetime.today().strftime("%Y%m%d %H:%M:%S %Z"),  # endDateTime,
            durationStr,  # durationStr,
            barSizeSetting,  # barSizeSetting,
            "TRADES",  # whatToShow,
            1,  # useRTH,
            1,  # formatDate
            False,  # KeepUpToDate <<==== added for api 9.73.2
            []  ## chartoptions not used
        )

        ## Wait until we get a completed data, an error, or get bored waiting
        MAX_WAIT_SECONDS = 20
        print("Getting historical data from the server... could take %d seconds to complete " % MAX_WAIT_SECONDS)

        historic_data = historic_data_queue.get(timeout=MAX_WAIT_SECONDS)

        """
        while self.wrapper.is_error():
            print(self.get_error())
        """
        if historic_data_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")

        self.cancelHistoricalData(tickerid)

        return historic_data

    def get_historical_news_headers(self, conId, providerCodes, startDateTime='', endDateTime='', totalResults=300,
                                    requestId=DEFAULT_GET_NEWS_HEADERS):

        """
        Returns historical prices for a contract, up to today
        ibcontract is a Contract
        :returns list of prices in 4 tuples: Open high low close volume
        """
        ## Make a place to store the data we're going to return
        news_header_queue = finishableQueue(self.init_historical_news_headers(requestId))
        # Request some historical data. Native method in EClient
        self.reqHistoricalNews(requestId, conId, providerCodes, endDateTime, startDateTime, totalResults, None)
        ## Wait until we get a completed data, an error, or get bored waiting
        MAX_WAIT_SECONDS = 20
        print("Getting historical news headers. could take %d seconds to complete " % MAX_WAIT_SECONDS)
        historic_news_headers = news_header_queue.get(timeout=MAX_WAIT_SECONDS)
        if news_header_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")
            return News.ErrorNoNewsHeaders, News.ErrorNoNewsHeaders
        return historic_news_headers, News.OK

    def get_news_providers(self, tickerid=DEFAULT_GET_NEWS_PROVIDERS):

        """
        Returns historical prices for a contract, up to today
        ibcontract is a Contract
        :returns list of prices in 4 tuples: Open high low close volume
        """

        ## Make a place to store the data we're going to return
        news_providers_queue = finishableQueue(self.init_news_providers(tickerid))

        # Request some historical data. Native method in EClient
        self.reqNewsProviders()

        ## Wait until we get a completed data, an error, or get bored waiting
        MAX_WAIT_SECONDS = 20
        print(f"Getting news providers. could take {MAX_WAIT_SECONDS} seconds to complete ")

        news_providers = news_providers_queue.get(timeout=MAX_WAIT_SECONDS)

        if news_providers_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished ")
            return news_providers, NP.ErrorNoProviders

        return news_providers, NP.OK

    def get_positions(self, conf):
        ## Make a place to store the data we're going to return
        positions_queue = finishableQueue(self.init_positions(DEFAULT_GET_POSITIONS))

        self.reqPositions()
        ## Wait until we get a completed data, an error, or get bored waiting
        MAX_WAIT_SECONDS = 20
        print("Getting positions from the server... could take %d seconds to complete " % MAX_WAIT_SECONDS)

        positions_list_of_dicts = positions_queue.get(timeout=MAX_WAIT_SECONDS)
        if positions_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")
            return '', Position.ErrorTimeout
        self.cancelPositions()
        positions_df = pd.DataFrame(positions_list_of_dicts)
        positions_df.to_csv(conf[Conf.PositionsFilePath])
        return positions_df, Position.OK

    def get_account(self, account):
        ## Make a place to store the data we're going to return
        account_queue = finishableQueue(self.init_account(DEFAULT_GET_ACCOUNT))

        self.reqAccountUpdates(subscribe=True, acctCode=account)

        ## Wait until we get a completed data, an error, or get bored waiting
        MAX_WAIT_SECONDS = 20
        print("Getting positions from the server... could take %d seconds to complete " % MAX_WAIT_SECONDS)

        account_values = account_queue.get(timeout=MAX_WAIT_SECONDS)
        if account_queue.timed_out():
            print("Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")
            return '', AV.ErrorTimeOut
        self.reqAccountUpdates(subscribe=False, acctCode=account)  # To end the stream of messages
        return account_values, AV.OK


class TestApp(TestWrapper, TestClient):
    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        self.connect(ipaddress, portid, clientid)

        thread = Thread(target=self.run)
        thread.start()

        setattr(self, "_thread", thread)

        self.init_error()


def connect_broker(conf):
    app = TestApp(conf[Conf.BrokerLocalIPAddress], int(conf[Conf.BrokerPortForAccount]),
                  int(conf[Conf.BrokerClientIDForAccount]))
    return app


def connect_history_broker(conf):
    app = TestApp(conf[Conf.BrokerLocalIPAddress], int(conf[Conf.BrokerPortForHistoricalData]),
                  int(conf[Conf.BrokerClientForHistoricalData]))
    return app


def submit_trade(conf, connection, main_order_id, symbol_type, symbol, amount, stop_price, action, profit_take,
                 order_purpose, order_ref, lmt_or_market):
    app = connection  # For clarity purpose we call the parameter connection as it will be used with other brokers
    ibcontract = IBContract()
    ibcontract.secType = symbol_type
    ibcontract.symbol = symbol
    ibcontract.currency = "USD"
    ibcontract.exchange = "SMART"
    # ibcontract.PrimaryExchage = "ISLAND"
    resolved_ibcontract, error_code = app.resolve_ib_contract(ibcontract, reqId=conf[Conf.GlobalRequestID])
    conf[Conf.GlobalRequestID] += 1
    print(error_code)
    order_id_main = 0
    order_id_stop = 0
    order_id_profit_take = 0
    if error_code != "OK":
        return 0, 0, app.get_error_queue()
    if order_purpose == MyOrder.Main:  # This happens when we submit stop orders for existing position.
        order_main = Order()
        order_main.action = action
        order_main.account = conf[Conf.AccountNumber]
        order_main.orderRef = f'{MyOrder.Main}_{order_ref}'  # main order
        order_main.orderType = "MKT"
        order_main.totalQuantity = amount
        order_main.tif = 'DAY'
        if (stop_price > 0) or (profit_take > 0):
            order_main.transmit = False  # The order will be transmitted together with its child order, the stop loss
        else:  # This order closes a position or has no stop or profit take defined.
            order_main.transmit = True
        order_id_main = app.place_new_IB_order(resolved_ibcontract, order_main, orderid=main_order_id)
    #  Submit a stop order
    if stop_price > 0:
        order_stop = Order()
        order_stop.account = conf[Conf.AccountNumber]
        if main_order_id != 0:  # Some of the stop order request come without a parent ID to protect an existing position
            order_stop.parentId = main_order_id
        order_stop.action = Dicts.invert_action[action]
        order_stop.auxPrice = stop_price
        order_stop.orderRef = f'{MyOrder.StopLoss}_{order_ref}'
        order_stop.orderType = MyOrder.Stop
        order_stop.tif = 'GTC'  # If we don't put GTC the order is cancelled the next day.
        order_stop.totalQuantity = amount
        if profit_take > 0:
            order_stop.transmit = False
        else:
            order_stop.transmit = True  # The order will be transmitted together with its child order, the stop loss
        order_id_stop = app.place_new_IB_order(resolved_ibcontract, order_stop, orderid=main_order_id + 1)
    if profit_take > 0:
        order_profit_take = Order()
        order_profit_take.account = conf[Conf.AccountNumber]
        if main_order_id != 0:  # Some of the profit take order request come without a parent ID to protect an existing position
            order_profit_take.parentId = order_id_main
        profit_take_order_id = main_order_id + 2
        order_profit_take.action = Dicts.invert_action[action]
        order_profit_take.lmtPrice = profit_take
        order_profit_take.orderRef = f'{MyOrder.ProfitTake}_{order_ref}'
        order_profit_take.orderType = MyOrder.Limit
        order_profit_take.tif = 'GTC'  # If we don't put GTC the order is cancelled the next day.
        order_profit_take.totalQuantity = amount
        order_profit_take.transmit = True  # The order will be transmitted together with its child order, the stop loss
        order_id_profit_take = app.place_new_IB_order(resolved_ibcontract, order_profit_take,
                                                      orderid=profit_take_order_id)
    status_messages = app.get_error_queue()
    return order_id_main, order_id_stop, order_id_profit_take, status_messages


def submit_stop_cancel(order_id, connection):
    app = connection
    app.cancel_order(int(order_id))


def submit_profit_take_cancel(order_id, connection):
    app = connection
    app.cancel_order(int(order_id))


def get_daily_adjusted(conf, symbol, number_of_days):
    app = conf[Conf.BrokerConnectionHistData]
    ibcontract = IBContract()
    ibcontract.secType = "STK"
    ibcontract.symbol = symbol
    ibcontract.currency = "USD"
    ibcontract.exchange = "SMART"
    resolved_ibcontract, error = app.resolve_ib_contract(ibcontract, reqId=conf[Conf.GlobalRequestID])
    conf[Conf.GlobalRequestID] += 1
    if error != "OK":
        return 'error', 'error', SH.ErrorInvalidIBContract
    duration_str = '{days} D'.format(days=number_of_days)
    history_list_of_touples = app.get_IB_historical_data_modified(resolved_ibcontract, durationStr=duration_str,
                                                                  tickerid=conf[Conf.GlobalRequestID])
    conf[Conf.GlobalRequestID] += 1
    if len(history_list_of_touples) == 0:
        return 'error', 'error', SH.ErrorEmptyListOfTuples
    df_history = pd.DataFrame(
        columns=[SH.Date, SH.Open, SH.High, SH.Low, SH.AdjustedClose, SH.Volume, SH.Close, SH.Dividend,
                 SH.SplitCoefficient])
    for row in history_list_of_touples:
        date = row[0]
        date_hyphenated = '{}-{}-{}'.format(date[0:4], date[4:6], date[6:])
        dict_h = {SH.Date: date_hyphenated, SH.Open: row[1], SH.High: row[2], SH.Low: row[3],
                  SH.AdjustedClose: row[4], SH.Volume: row[5], SH.Close: SH.NotProvided, SH.Dividend: SH.NotProvided,
                  SH.SplitCoefficient: SH.NotProvided}
        df_history = df_history.append(dict_h, ignore_index=True)
    #  Create the symbol meta dict in order to be compatible with the alphavantage way of returning the data.
    symbol_meta = {SM.Information: SM.Ibkr1y1d, SM.Symbol: symbol, SM.LastRefreshed: SM.NotProvidedByIBKR,
                   SM.OutputSize: SM.NotProvidedByIBKR, SM.TimeZone: SM.NotProvidedByIBKR}
    return df_history, symbol_meta, SH.OK


def get_positions_from_all_accounts(conf, connection):
    positions, error = connection.get_positions(conf)
    return positions, error


def get_orders_from_all_accounts(conf, connection):
    orders, error = connection.get_open_orders()
    return orders, error


def get_account_values(conf, connection):
    account_values, error = connection.get_account(conf)
    account_dict = {}
    for value in account_values:
        account_dict[value[AV.Key]] = value[AV.Value]

    return account_dict, error


def get_news_providers_codes(connection):
    news_providers, error = connection.get_news_providers()
    codes = ''
    i = 0
    for news_provider in news_providers:
        for element in news_provider:
            if i == 0:
                codes = element.code
                i += 1
            else:
                codes = codes + '+' + element.code
    return codes


# def get_provider_from_article_ID(symbol, id):
#     seperator = '$'
#     if seperator in id:
#         elements = id.split(seperator, 1)
#         provider = elements[0]
#         return provider
#     else:
#         print(f'Seperator not found in id {id}')
#         quit(-1)


def get_hist_news_headers(conf, connection, symbol, providers_codes, today):
    end_date_time = f'{today} 00:00:00.0'
    start_date = '2000-01-01 00:00:00.0'
    ibcontract = IBContract()
    ibcontract.secType = 'STK'
    ibcontract.symbol = symbol
    ibcontract.currency = "USD"
    ibcontract.exchange = "SMART"
    resolved_ibcontract: IBContract  # This allows IDE to know what type it is and suggest methods or properties
    resolved_ibcontract, error_code = connection.resolve_ib_contract(ibcontract, reqId=conf[Conf.GlobalRequestID])
    conId = resolved_ibcontract.conId
    all_headers_for_symbol = pd.DataFrame()
    has_more = News.HasMore
    while has_more == News.HasMore:
        historical_news_headers, error_code = connection.get_historical_news_headers(conId, providers_codes,
                                                                                     startDateTime=start_date,
                                                                                     endDateTime=end_date_time)
        if error_code != News.OK:
            return all_headers_for_symbol, error_code
        if type(historical_news_headers) == str:
            print(f'historical_news_headers is {historical_news_headers} and is a string in {symbol}')
            return all_headers_for_symbol, error_code
        has_more = historical_news_headers[-1][News.ArticleID]
        del historical_news_headers[-1]
        df_headers = pd.DataFrame(historical_news_headers)
        # remove duplicate article ids.
        all_headers_for_symbol = pd.concat([all_headers_for_symbol, df_headers])
        if has_more == News.HasMore:
            end_time = all_headers_for_symbol.iloc[-1, :][News.Time]
            end_date = all_headers_for_symbol.iloc[-1, :][News.Date]
            end_date_time = f'{end_date} {end_time}'
            print(f'{symbol} has more')
    return all_headers_for_symbol, error_code


def get_providers(connection):
    providers_codes = get_news_providers_codes(connection)
    return providers_codes


