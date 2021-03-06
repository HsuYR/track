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
    # account_detail is a dict with the following key:
    # name -- the name string of the account,
    # type_id -- the id of the account type,
    # description -- optional text description of the account,
    # hidden -- boolean value representing whether account will be hidden.
    #
    # Account type falls into one of the basic types:
    # ASSET -- with type_id 1,
    # LIABILITY -- with type_id 2,
    # EQUITY -- with type_id 3,
    # INCOME -- with type_id 4, or
    # EXPENSE -- with type_id 5.
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

    def delete_account(self, account_id, move_to_id = 0):
        """Delete the specified account.

        Delete the account with specified account id. If there are not existing
        transactions related to the account, delete the account directly. If
        there are transactions related to the account, one can specify another
        account that substitute the to-be-deleted account using move_to_id
        argument. If move_to_id is set to 0 (also as default value), all
        transactions related to the account will be deleted."""
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT COUNT(*) FROM splits WHERE account_id=?', (account_id,))
            if c.fetchone()['COUNT(*)']:
                if move_to_id:
                    c.execute('SELECT * FROM splits')
                    c.execute('UPDATE splits SET account_id=? WHERE account_id=?',
                    (move_to_id, account_id))
                else:
                    c.execute('SELECT transaction_id FROM splits WHERE account_id=?',
                    (account_id,))
                    for row in c.fetchall():
                        self.delete_transaction(row['transaction_id'])
            for row in c.fetchall():
                print(row['transaction_id'], row[2], row[3], row[4])
            c.execute('DELETE FROM accounts WHERE id=?', (account_id,))

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

    def account_ids(self):
        """Generator function of account ids"""
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT id FROM accounts')
            for row in c.fetchall():
                yield row['id']

    def account_ids_list(self):
        """Return a list of account id"""
        return [i for i in self.account_ids()]

    def account_balance(self, account_id):
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT SUM(amount) FROM splits WHERE account_id=?', (account_id,))
        return c.fetchone()['SUM(amount)']

    #
    # Transaction
    #
    # Each transaction is a dict consists of
    # date -- a date, which would be default to today,
    # splits -- list of at least two splits which balance, and
    # description -- an optional description.
    #
    # Each split has
    # account_id -- the affected account id,
    # amount -- the amount taking effect,
    #     which is either Dr. or Cr.,
    #     represented by positive or negative amount respectively, and
    # description -- an optional description.
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
                    c.execute('UPDATE transactions SET %s=? WHERE id=?' % key,
                    (value, transaction_id))
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

    def transaction_ids(self):
        """Generator function of transaction ids"""
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT id FROM transactions')
            for row in c.fetchall():
                yield row['id']

    def transaction_ids_list(self):
        """Return a list of transaction id"""
        return [i for i in self.transaction_ids()]

    def transaction_ids_between_date(self, start_date, end_date):
        """Generator function yielding transaction ids between dates

        Both start_date and end_date are inclusive. Both start_date and
        end_date are strings and follow the format "YYYY-MM-DD".
        """
        with self.conn:
            c = self.conn.cursor()
            c.execute('SELECT id FROM transactions WHERE date BETWEEN ? AND ?',
            (start_date, end_date))
            for row in c.fetchall():
                yield row['id']

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
