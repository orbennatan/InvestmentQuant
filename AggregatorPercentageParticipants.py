from AggregatorBase import AggregatorBase
from BrokerBase import BrokerBase
from MyConstants import PathConstants as PC, TimeConstants as TC, GeneralConstants as GC
from os.path import join, exists
import pandas as pd
from pandas import DataFrame
from pandas import DataFrame


class AggregatorPercentageParticipants(AggregatorBase):
    AggregatorFileName = 'AggregatorFileName'
    InitialState = 'InitialState'
    NonOwnersKeys = [TC.Date, GC.Comments, GC.Total]

    def __init__(self, conf):
        super().__init__(conf)  # We need this call in order to call the ABC __init__ method
        self.df = None
        self.account_total = 0
        self.owners = []
        self.owners_percentages = {}
        self.filepath = join(self.global_conf[PC.RootFolder], self.class_conf[self.AggregatorFileName])
        self.init_df_from_file_or_conf()
        self.update_total_from_accounts()
        self.create_owners_list()
        self.update_df_with_new_net_liquidation_value()
        owner_ordinal, change = self.obtain_owner_name_and_deposit_or_withdrawal_amount()
        if owner_ordinal != 9:
            self.update_df_with_owner_deposit_or_withdrawal(owner_ordinal=owner_ordinal, change=change)

    def init_df_from_file_or_conf(self):
        if exists(self.filepath):
            self.df = pd.read_csv(self.filepath)
        else:
            self.df = DataFrame.from_dict(data=self.class_conf[self.InitialState])
        self.df.reset_index(drop=True, inplace=True)

    def create_owners_list(self):
        keys = self.class_conf[self.InitialState]
        for key in keys:
            if key not in self.NonOwnersKeys:
                self.owners.append(key)

    def get_total_from_all_accounts(self):
        accounts = self.class_conf[self.Accounts]
        self.account_total = 0
        for account in accounts:
            net_liquidation, error = self.broker.get_account_values(account)
            if error == BrokerBase.OK:
                self.account_total += float(net_liquidation)
            else:
                print('Error')

    def update_df_with_new_net_liquidation_value(self):
        # Sort the csv by date decsending to make sure the first row is the latest
        self.df.sort_values([TC.Date], ascending=False, inplace=True)
        # Line 0 now contains the values associated with each owner now, before the update from the account
        # Create a dict of percentage of the account associated with each owner
        # First, claculate the total
        total_all_oweners = 0
        for owner in self.owners:
            total_all_oweners += int(self.df.iloc[0][owner])
        # Now the relative value
        for owner in self.owners:
            self.owners_percentages[owner] = int(self.df.iloc[0][owner]) / total_all_oweners
        # Add this row with today's date and the comment
        new_row = {TC.Date: self.today_datetime_string(), GC.Comments: 'Upload from account', GC.Total: self.account_total}
        for owner in self.owners:
            new_row[owner] = int(self.account_total * self.owners_percentages[owner])
        new_row[GC.Comments] = 'Upload from account'

        self.df = self.df.append(new_row, ignore_index=True)
        self.df.sort_values([TC.Date], ascending=False, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.df.to_csv(self.filepath, index=False)

    def update_df_with_owner_deposit_or_withdrawal(self, owner_ordinal, change):
        # This method should be called only after a call to update the numbers from the total net liequidation of
        # the account
        # 'Or' is a special owner.
        # When Or is the owner making the change, it means the money was already transferred in/out of the account
        # In this case take current net liquidation value. Based on percentage of ownership calculate amount of each owner
        # If Or added money to the account: Subtract the money from the net liquidation. Using the amounts from the last line
        # Calculate the amount for each owner.
        # Add the new amount to Or. Write the line into the csv. The totals should be now equal the net liquidation
        depositing_owner = self.owners[owner_ordinal]
        new_row = {TC.Date: self.today_datetime_string(), GC.Comments: f'{self.owners[owner_ordinal]} {change}',
                   GC.Total: self.account_total}
        if depositing_owner == 'Or':
            total = self.account_total - change
            for owner in self.owners:
                amount = int(self.owners_percentages[owner] * total)
                if owner == 'Or':
                    amount += change
                new_row[owner] = amount
        else: # If the owner is not 'Or' it is actually a loan or takes from or returns to the owner.
            total = self.account_total
            for owner in self.owners:
                amount = int(self.owners_percentages[owner] * total)
                if owner == 'Or':
                    amount -= change
                elif owner == depositing_owner:
                    amount += change
                new_row[owner] = amount
        self.df = self.df.append(new_row, ignore_index=True)
        self.df.sort_values([TC.Date], ascending=False, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.df.to_csv(self.filepath, index=False)

    def obtain_owner_name_and_deposit_or_withdrawal_amount(self):
        # create prompt string
        owner_ordinal = 0
        prompt = ''
        for owner in self.owners:
            prompt = prompt + f'for {owner} enter {owner_ordinal}. '
            owner_ordinal += 1
        prompt += '9 for update from account only'
        owner_ordinal = int(input(prompt))
        if owner_ordinal != 9:
            prompt = 'enter a positive number for deposit, negative for withdraw. Just dollars. No cents allowed'
            change = int(input(prompt))
        else:
            change = 0
        return owner_ordinal, change
