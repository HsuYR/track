# Written in Python 3

class Trackbook:

    def __init__(self):
        self.accounts = {}
        self.transactions = []
        self.account_types = ['asset', 'liability', 'equity', 'income', 'expense']

    #
    # Account
    #
    # Account name is the key for account detail dict
    #
    # Account type fall into one of the basic types:
    # asset, liability, equity, income, or expense.
    #
    # description is optional and hidden defaults to False
    def add_account(self, name, detail):
        if name in self.accounts:
            raise ValueError('Account name already exists')
        if detail['type'] not in account_types:
            raise ValueError('Invalid account type')
        if 'description' not in detail:
            detail['description'] = ''
        if 'hidden' not in detail:
            detail['hidden'] = False
        self.accounts[name] = detail


    def edit_account(self, name, key, value):
        if key == 'name':
            new_name = value
            if new_name not in self.account:
                self.accounts[new_name] = self.accounts[name]
                self.rename_account_in_splits(name, new_name)
                del self.accounts[name]
        elif key == 'type':
            if value in self.account_types:
                self.accounts[name]['type'] = value
        else:
            self.accounts[name][key] = value

    def delete_account(self, name, move_to_name = 'Imbalance'):
        if len([self.get_splits(name)]):
            if move_to_name:
                if move_to_name not in self.accounts:
                    self.add_account(move_to_name, self.accounts[name]['type'])
                self.rename_account_in_splits(name, move_to_name)
            else:
                print('Deleting associated transactions.')
                self.transactions = [transaction
                    for transaction in self.transactions
                        if not self.involves_account(transaction, name)]
                print('Transacitons deleted.')
        del self.accounts[name]

    def show_account(self, name, verbose = False):
        print('-'*5 + 'Account Information' + '-'*6)
        print('Name:', name)
        print('Type:', self.accounts[name]['type'])
        print('Description:', self.accounts[name]['description'])
        print('Hidden:', self.accounts[name]['hidden'])
        print('Balance:', self.get_account_balance(name))
        print('-'*30)

    #
    # other account functions
    #
    def is_valid_account(self, name, detail):
        if name in self.accounts:
            return False
        elif detail['type'] not in self.account_types:
            return False
        else:
            return True

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
    def add_transaction(self, date, splits, description = '', tags = ''):
        transaction = {
            'date': date,
            'splits': splits,
            'description': description,
            'tags': tags,
            }
        if self.is_valid_transaction(transaction):
            self.transactions.append(transaction)

    def edit_transaction(self, index, key, value):
        transaction = self.transactions[index].copy()
        transaction[key] = value
        if self.is_valid_transaction(transaction):
            self.transactions[index] = transaction

    def delete_transaction(self, index):
        del self.transactions[index]

    def is_valid_transaction(self, transaction):
        #
        # Splits checking
        #
        # Total debit and credit amount should balance.
        if sum(split['amount'] for split in transaction['splits']) != 0:
            return False
        for split in transaction['splits']:
            if split['account_name'] not in self.accounts:
                return False
        return True

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
