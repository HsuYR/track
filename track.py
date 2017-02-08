# Written in Python 3

from datetime import date

# root object Track

# transactions contains a list of Transaction.
transactions = []
accounts = []

def add_transaction(date, splits, description = '', tags = ''):
    transaction = Transaction(date, splits, description, tags)
    transactions.append(transaction)
    print('-'*20)
    print('Transaction added successfully.')
    transaction.show()
    print('-'*20)

def show_accounts():
    for account in accounts:
        print(account.name)
        print('Balance:', account.balance)

def show_transactions():
    for transaction in transactions:
        transaction.show()

# Each Transaction has a date, at least two Splits that balance,
# an optional description, and an optional string of tags.
class Transaction:
    def __init__(self, date, splits, description = '', tags = ''):
        self.date = date
        self._splits = splits
        self.description = description
        self.tags = tags

    def show(self):
        print('-'*5+'Transaction detail:')
        print('Date: ', self.date)
        print('Description: ', self.description)
        print('Tags: ', self.tags)
        for split in self.splits:
            if(split['amount'] < 0):
                print(-split['amount'], '從', split['account'],
                 ' p.s. '+split['description'] if split['description'] else '')
            else:
                print(split['amount'], '到', split['account'],
                 ' p.s. '+split['description'] if split['description'] else '')

    # Each Split
    # has the affected account, which cannot be a placeholder account,
    # the amount taking effect,
    # is either Dr. or Cr., represented by positive or negative amount respectively,
    # and an optional description.
    @property
    def splits(self):
        return self._splits

    @splits.setter
    def splits(self, splits):
        # Check the number of splits
        if len(splits) == 0:
            raise Exception('Transaction should at least have two splits.')
        # Check the total debit and total credit amount of the transaction balance
        if sum(split['amount'] for split in splits) != 0:
            raise Exception('Total debit and credit amount should balance.')
        self._splits = splits

def split(amount, account, description = ''):
    if amount == 0:
        raise Exception('Split amount cannot be zero.')
    # Check the account involved exists
    if account not in accounts:
        raise Exception('Account %s does not exists' % split['account'])
    return {'amount': amount, 'account': account, 'description': description}


# Accounts is a nested list of Account and its description
# Each Account is a dict and should belong to one of the basic types of accounts:
# Assets, Liabilities, Equity, Incomes, or Expenses.
# An Account could be a placeholder account which does not hold a balance.
accounts = [
'資產::流動資產::現金',
'資產::流動資產::存款',
'資產::流動資產::悠遊卡',
'資產::點數紅利::深藏咖啡點數',
'支出::飲食::飲料',
'支出::飲食::早餐',
'支出::飲食::午餐',
'支出::飲食::晚餐',
'支出::飲食::點心',
'收入::工作收入'
]

class Account:
    def __init__(self, parent, placeholder = False):
        self.parent = parent
        self.placeholder = placeholder
        self._balance = 0

    @property
    def balance(self):
        return self._balance


if __name__ == '__main__':
    add_transaction(
        date.today(),
        [
        split(-60, '資產::流動資產::現金'),
        split(54, '支出::飲食::飲料', '深藏咖啡'),
        split(6, '資產::點數紅利::深藏咖啡點數', '深藏咖啡點數')
        ],
        description = '熱摩卡無糖',
        tags = ''
    )
    add_transaction(
        date.today(),
        [
        split(69, '支出::飲食::晚餐', '頂好 嘉義文蛤'),
        split(-69, '資產::流動資產::悠遊卡', '一仁悠遊卡')
        ],
        description = '頂好 嘉義文蛤',
        tags = '過年 家裡開火'
    )
    show_transactions()
