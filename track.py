# Written in Python 3

from datetime import date


# transactions is a list of all transaction recorded
transactions = []

# accounts is a list of all accounts registered
accounts = []


# Each transaction consists of a date,
# at least two splits which balance,
# an optional description,
# and an optional string of tags.
# tags are words separated by white space.
def create_transaction(date, splits, description = '', tags = ''):
    return {
        'date': date,
        'splits': splits,
        'description': description,
        'tags': tags,
        }

def is_valid_transaction(transaction):
    #
    # Splits checking
    #
    # Transaction should at least have two splits.
    splits = transaction['splits']
    if len(splits) == 0:
        return False
    # Total debit and credit amount should balance.
    if sum(split['amount'] for split in splits) != 0:
        return False
    for split in splits:
        # Split amount cannot be zero.
        if split['amount'] == 0:
            return False
        # Check the account involved exists
        if split['account_name'] not in list_account_property('account_name'):
            return False
    return True

# Each split has
# the affected account name,
# the amount taking effect,
# is either Dr. or Cr., represented by positive or negative amount respectively,
# and an optional description.
def create_split(amount, account_name, description = ''):
    return {
        'amount': amount,
        'account_name': account_name,
        'description': description,
        }

def add_transaction(transaction):
    if is_valid_transaction(transaction):
        transactions.append(transaction)
    else:
        print('Invalid transaction!')

def edit_transaction(transaction, index):
    if is_valid_transaction(transaction):
        transactions[index] = transaction
    else:
        print('Invalid transaction! Failied')

def delete_transaction(index):
    transactions.pop(index)

def print_transaction(transaction):
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

def print_transactions():
    for transaction in transactions:
        print_transaction(transaction)

# Each account is a dict and should belong to one of the basic types of accounts:
# asset, liability, equity, income, or expense.
def create_account(account_name, account_type, account_code = None, description = ''):
    return {
        'account_name': account_name,
        'account_type': account_type,
        'account_code': account_code,
        'description': description,
        }

account_types = ['asset', 'liability', 'equity', 'income', 'expense']

def is_valid_account(account):
    if account['account_name'] in list_account_property('account_name'):
        return False
    elif account['account_code'] and account['account_code'] in list_account_property('account_code'):
        return False
    elif account['account_type'] not in account_types:
        return False
    else:
        return True

def list_account_property(key):
    return [account[key] for account in accounts]

def calculate_account_balance(account):
    return sum(split['amount']
        for transaction in transactions \
            for split in transaction['splits'] \
                if split['account_name'] == account['account_name'])

def print_account_detail(account):
    print('-'*5 + 'Account Information' + '-'*6)
    print('Name:', account['account_name'], 'Code:', account['account_code'])
    print('Type:', account['account_type'])
    print('Description:', account['description'])
    print('Balance:', calculate_account_balance(account))
    print('-'*30)

def print_accounts_detail():
    for account in accounts:
        print_account_detail(account)

if __name__ == '__main__':
    # initialize accounts
    accounts.append(create_account('資產::流動資產::現金', 'asset'))
    accounts.append(create_account('資產::點數紅利::深藏咖啡點數', 'asset'))
    accounts.append(create_account('支出::飲食::飲料', 'expense'))


    t1 = create_transaction(
        date.today(),
        [
        create_split(-60, '資產::流動資產::現金'),
        create_split(54, '支出::飲食::飲料', '深藏咖啡'),
        create_split(6, '資產::點數紅利::深藏咖啡點數', '深藏咖啡點數'),
        ],
        description = '熱摩卡無糖',
        tags = '',
    )
    add_transaction(t1)
    print(is_valid_transaction(t1))
    t2 = create_transaction(
        date.today(),
        [
        create_split(69, '支出::飲食::晚餐', '頂好 嘉義文蛤'),
        create_split(-69, '資產::流動資產::悠遊卡', '一仁悠遊卡'),
        ],
        description = '頂好 嘉義文蛤',
        tags = '過年 家裡開火',
    )
    add_transaction(t2)
    print(is_valid_transaction(t2))
    print_transactions()
    print_accounts_detail()
