"""A simple bookkeeping module"""
# Written in Python 3

import sqlite3
import os
import datetime

class Book:
    """A book for bookkeeping"""

    def __init__(self, database_name):
        """Open an existing book.

        Each instance has its own connection to the database. The connection
        will be shared and used among methods of the instance.
        """
        if os.path.exists(database_name):
            self.conn = sqlite3.connect(database_name)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute('PRAGMA foreign_keys = ON')
        else:
            raise FileNotFoundError


    @classmethod
    def new(cls, database_name):
        """Create a new book.

        Create a new blank book by initializing an empty database. Return an
        instance of the newly created book.
        """
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
                    [('ASSET',), ('LIABILITY',), ('EQUITY',), ('INCOME',), ('EXPENSE',)])
                c.execute('''CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY,
                    date DATE NOT NULL,
                    description TEXT
                    );''')
                c.execute('''CREATE TABLE IF NOT EXISTS splits(
                    id INTEGER PRIMARY KEY,
                    transaction_id INTEGER NOT NULL,
                    account_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                    );''')
        return cls(database_name)

    #
    # Account
    #
    # account detail is a dict with key:
    # name, type_id, [description, hidden]
    # in which description is optional and hidden defaults to False
    #
    # Account type falls into one of the basic types:
    # ASSET, LIABILITY, EQUITY, INCOME, or EXPENSE
    # with type_id 1, 2, 3, 4, 5 respectively.
    #
    def insert_account(self, account_detail):
        """Insert a new account with the provided account detail."""
        name = account_detail['name']
        type_id = account_detail['type_id']
        if 'description' not in account_detail:
            description = ''
        if 'hidden' not in account_detail:
            hidden = False
        with self.conn:
            c = self.conn.cursor()
            c.execute(
            'INSERT INTO accounts (name, type_id, description, hidden) VALUES (?,?,?,?);',
            (name, type_id, description, hidden)
             )

    def update_account(self, account_id, account_detail):
        """Update the account detail of the given account id."""
        with self.conn:
            c = self.conn.cursor()
            for key, value in account_detail.items():
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

    def account_detail_by_id(self, account_id):
        """Return the account detail of the given id.

        The returned account detail is a python dict.
        """
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT * FROM accounts WHERE id=?', (account_id,))
            cols = ['account_id', 'name', 'type_id', 'description', 'hidden']
            account = dict(zip(cols, c.fetchone()))
            return account

    def account_type_id(self, account_type):
        """Return the type id of the account type name."""
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT (id) FROM account_types WHERE type=?', (account_type,))
        return c.fetchone()['id']

    def account_id(self, name):
        conn = sqlite3.connect(self.database_name)
        with conn:
            c = conn.cursor()
            c.execute('SELECT (id) FROM accounts WHERE name=?', (name,))
            return c.fetchone()['id']

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
    # Each transaction is a dict consists of
    # a date, which would be default to today,
    # at least two splits which balance,
    # and an optional description
    def insert_transaction(self, transaction_detail):
        """Insert a new transaction."""
        with self.conn:
            c = self.conn.cursor()

            if 'date' not in transaction_detail:
                transaction_detail['date'] = datetime.date.today()
            if 'description' not in transaction_detail:
                transaction_detail['description'] = ''

            Book.check_split_sum(transaction_detail['splits'])
            c.execute('INSERT INTO transactions (date, description) VALUES (?, ?)',
            (transaction_detail['date'], transaction_detail['description'])
            )
            transaction_id = c.lastrowid
            self.write_splits(transaction_id, transaction_detail['splits'])

    def update_transaction(self, transaction_id, transaction_detail):
        """Update the transaction with the specified id.

        Update the transaction detail and overwrite the splits of the
        transaction.
        """
        with self.conn:
            c = self.conn.cursor()
            for key, value in transaction_detail.items():
                if key in ['date', 'description']:
                    c.execute('UPDATE transactions SET %s WHERE id=?' % key, (value, ))
                elif key == 'splits':
                    Book.check_split_sum(value)
                    self.write_splits(transaction_id, value)

    def delete_transaction(self, transaction_id):
        """Delete the specified transaction."""
        with self.conn:
            c = self.conn.cursor()
            c.execute('DELETE FROM splits WHERE transaction_id=?', (transaction_id,))
            c.execute('DELETE FROM transactions WHERE id=?', (transaction_id,))

    def transaction_detail_by_id(self, transaction_id):
        """Return the transaction detail with the specified id.

        The transaction detail returned is a python dict.
        """
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT * FROM transactions WHERE id=?', (transaction_id,))
            transaction_detail = {}
            row = c.fetchone()
            transaction_detail['date'] = row['date']
            transaction_detail['description'] = row['description']
            transaction_detail['splits'] = []
            c.execute('SELECT * FROM splits WHERE transaction_id=?', (transaction_id,))
            for row in c.fetchall():
                split = {
                    'account_id': row['account_id'],
                    'amount': row['amount'],
                    'description': row['description'],
                }
                transaction_detail['splits'].append(split)
        return transaction_detail


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

    @staticmethod
    def check_split_sum(splits):
        """Check whether the splits are balanced.

        The total amount of debit, represented as positive, and credit,
        represented as negative, for each transaction should be the same and
        therefore should sums up to zero.
        """
        if sum(split['amount'] for split in splits) != 0:
            raise ValueError('Total debit and credit amount should balance')

    def write_splits(self, transaction_id, splits):
        """Overwrite all existing splits related to the specified transaction."""
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT COUNT(*) FROM splits WHERE transaction_id=?', (transaction_id,))
            if c.fetchone()['COUNT(*)']:
                c.execute('DELETE FROM splits WHERE transaction_id=?', (transaction_id,))
            for split in splits:
                if 'description' not in split:
                    split['description'] = ''
                c.execute(
                'INSERT INTO splits (transaction_id, account_id, amount, description) VALUES (?, ?, ?, ?)',
                (transaction_id, split['account_id'], split['amount'], split['description'])
                )
