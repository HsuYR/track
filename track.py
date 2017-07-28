''' Track
    A Simple Bookkeeping Module

'''
# Written in Python 3

import sqlite3
import os
from datetime import datetime

class Book:
    'A book for bookkeeping'

    def __init__(self, database_name):
        'Open existing database'
        if os.path.exists(database_name):
            self.conn = sqlite3.connect(database_name)


    @classmethod
    def new(cls, database_name):
        'Create new database'
        if os.path.exists(database_name):
            raise FileExistsError
        else:
            conn = sqlite3.connect(database_name)
            with conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    type_id INTEGER NOT NULL,
                    description TEXT,
                    hidden INTEGER NOT NULL,
                    FOREIGN KEY (type_id) REFERENCES account_types(id)
                    );''')
                c.execute('''CREATE TABLE IF NOT EXISTS account_types(
                    id INTEGER PRIMARY KEY,
                    type TEXT UNIQUE NOT NULL
                    );''')
                c.executemany('''INSERT INTO account_types (type) VALUES (?);''',
                    [('asset',), ('liability',), ('equity',), ('income',), ('expense',)])
                c.execute('''CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY,
                    date DATE NOT NULL,
                    description TEXT
                    );''')
                c.execute('''CREATE TABLE IF NOT EXISTS splits(
                    transaction_id INTEGER NOT NULL,
                    account_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                    );''')
        return Book(database_name)

    #
    # Account
    #
    # Account type falls into one of the basic types:
    # assets, liability, equity, income, or expense.
    #
    # description is optional and hidden defaults to False
    def add_account(self, name, type_id, description = '', hidden = False):
        with self.conn:
            c = self.conn.cursor()
            c.execute(
            'INSERT INTO accounts (name, type_id, description, hidden) VALUES (?,?,?,?);',
            (name, type_id, description, hidden)
             )

    def update_account(self, account_id, **kwargs):
        with self.conn:
            c = self.conn.cursor()
            for key, value in kwargs.items():
                if key in ['name', 'type_id', 'description', 'hidden']:
                    c.execute('UPDATE accounts SET %s=? WHERE id=?;' % key, (value, account_id))

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
                    #for transaction in transactions:
                    #    if not self.involves_account(transaction, name)]
                print('Transacitons deleted.')
        del accounts[name]
        accounts.close()

    def account(self, account_id):
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT * FROM accounts WHERE id=?', (account_id,))
            cols = ['account_id', 'name', 'type_id', 'description', 'hidden']
            account = dict(zip(cols, c.fetchone()))
            return account

    def account_type_id(self, account_type):
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT (id) FROM account_types WHERE type=?', (account_type,))
        return c.fetchone()[0]

    def account_id(self, name):
        conn = sqlite3.connect(self.database_name)
        with conn:
            c = conn.cursor()
            c.execute('SELECT (id) FROM accounts WHERE name=?', (name,))
            return c.fetchone()[0]

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
