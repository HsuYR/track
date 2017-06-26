# Written in Python 3

import shelve
from datetime import date
import uuid


class Trackbook:

    def __init__(self):
        with shelve.open('config_shelve') as config:
            if 'account_types' not in config:
                config['account_types'] = ['asset', 'liability', 'equity', 'income', 'expense']
            if 'accounts_filename' not in config:
                config['accounts_filename'] = 'accounts_shelve'
            if 'transactions_filename' not in config:
                config['transactions_filename'] = 'transactions_filename'
            self.account_types = config['account_types']
            self.accounts_filename = config['accounts_filename']
            self.transactions_filename = config['transactions_filename']

    #
    # Account
    #
    # Account name is the key for account detail dict
    #
    # Account type fall into one of the basic types:
    # asset, liability, equity, income, or expense.
    #
    # description is optional and hidden defaults to False
    def insert_account(self, name, detail):
        accounts = shelve.open(self.accounts_filename)
        if name in accounts:
            raise ValueError('Account name already exists')
        if detail['type'] not in self.account_types:
            raise ValueError('Invalid account type')
        if 'description' not in detail:
            detail['description'] = ''
        if 'hidden' not in detail:
            detail['hidden'] = False
        accounts[name] = detail
        accounts.close()

    def update_account(self, name, **kwargs):
        accounts = shelve.open(self.accounts_filename)
        for key in kwargs:
            if key == 'name':
                if kwargs[key] not in accounts:
                    self.rename_account(name, kwargs[key])
            elif key == 'type':
                if kwargs[key] in self.account_types:
                    a = accounts[name]
                    a[key] = kwargs[key]
                    accounts[name] = a
            else:
                a = accounts[name]
                a[key] = kwargs[key]
                accounts[name] = a
        accounts.close()

    def del_account(self, name, move_to_name = 'Imbalance'):
        accounts = shelve.open(self.accounts_filename)
        if len([self.get_splits(name)]):
            if move_to_name:
                if move_to_name not in accounts:
                    self.add_account(move_to_name, accounts[name]['type'])
                self.rename_account_in_splits(name, move_to_name)
            else:
                print('Deleting associated transactions.')
                transactions = shelve.open(self.transactions_filename)
                transactions = [transaction
                    for transaction in transactions:
                        if not self.involves_account(transaction, name)]
                print('Transacitons deleted.')
        del accounts[name]
        accounts.close()

    def rename_account(self, old_name, new_name):
        accounts = shelve.open(self.accounts_filename)
        if new_name not in accounts:
            accounts[new_name] = accounts[old_name]
            self.rename_account_in_splits(old_name, new_name)
            del accounts[old_name]
        else:
            raise ValueError('Account name already exists')
        accounts.close()

    def show_account(self, name, verbose = False):
        accounts = shelve.open(self.accounts_filename)
        print('-'*5 + 'Account Information' + '-'*6)
        print('Name:', name)
        print('Type:', accounts[name]['type'])
        print('Description:', accounts[name]['description'])
        print('Hidden:', accounts[name]['hidden'])
        print('Balance:', self.get_account_balance(name))
        print('-'*30)
        accounts.close()

    #
    # other account functions
    #
    def is_valid_account(self, name, detail):
        accounts = shelve.open(self.accounts_filename)
        if name in accounts:
            return False
        elif detail['type'] not in self.account_types:
            return False
        else:
            return True
        accounts.close()

    def get_account_balance(self, name):
        return sum(split['amount'] for split in self.get_splits(name))

    def get_splits(self, account_name = None):
        if account_name:
            for transaction in self.transactions:
                for split in transaction['splits']:
                    if split['account_name'] == account_name:
                        yield split
        else:
            for transaction in self.transactions:
                for split in transaction['splits']:
                    yield split

    def rename_account_in_splits(self, old_name, new_name):
        for split in get_splits(old_name):
            split['account_name'] = new_name

    def involves_account(self, transaction, account_name):
        for split in transaction['splits']:
            if split['account_name'] == account_name:
                return True
        return False


    #
    # Transaction
    #
    # Each transaction consists of a date,
    # at least two splits which balance,
    # an optional description,
    # and an optional string of tags.
    # tags are words separated by white space.
    def add_transaction(self, transaction):
        if 'date' not in transaction:
            transaction['date'] = date.today()
        if 'description' not in transaction:
            transaction['description'] = ''
        if 'tags' not in transaction:
            transaction['tags'] = ''
        if sum(split['amount'] for split in transaction['splits']) != 0:
            raise ValueError('Total debit and credit amount should balance')
        accounts = shelve.open(self.accounts_filename)
        for split in transaction['splits']:
            if split['account_name'] not in accounts:
                raise ValueError('Account name does not exists')
            if 'description' not in split:
                split['description'] = ''
        accounts.close()
        transactions = shelve.open(self.transactions_filename)
        transactions[str(uuid.uuid4())] = transaction
        transactions.close()

    def edit_transaction(self, index, key, value):
        transaction = self.transactions[index].copy()
        transaction[key] = value
        if self.is_valid_transaction(transaction):
            self.transactions[index] = transaction

    def delete_transaction(self, index):
        del self.transactions[index]

    def show_transaction(self, transaction):
        print('-'*5+'Transaction detail:'+'-'*6)
        print('Date: ', transaction['date'])
        print('Description: ', transaction['description'])
        print('Tags: ', transaction['tags'])
        for split in transaction['splits']:
            if(split['amount'] < 0):
                print(-split['amount'], 'from', split['account_name'],
                 ' p.s. '+split['description'] if split['description'] else '')
            else:
                print(split['amount'], 'to', split['account_name'],
                 ' p.s. '+split['description'] if split['description'] else '')
        print('-'*30)


    # Each split has
    # the affected account name,
    # the amount taking effect,
    # is either Dr. or Cr., represented by positive or negative amount respectively,
    # and an optional description.
    def create_split(self, amount, account_name, description = ''):
        return {
            'amount': amount,
            'account_name': account_name,
            'description': description,
            }
