# Written in Python 3

from datetime import date


# transaction_list is a list of all transaction recorded
transaction_list = []

# account_list is a list of all account registered
account_list = []


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
        if split['account_name'] not in get_account_name_list():
            return False
    return True

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

def involves_account(transaction, account_name):
    for split in transaction['splits']:
        if split['account_name'] == account_name:
            return True
    else:
        return False

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

def get_all_splits():
    for transaction in transaction_list:
        for split in transaction['splits']:
            yield split

def get_splits_by_account_name(account_name):
    for split in get_all_splits():
        if split['account_name'] == account_name:
            yield split

def replace_account_name_in_splits(old_name, new_name):
    for split in get_splits_by_account_name(old_name):
        split['account_name'] = new_name

# transaction_list operations
def add_transaction(transaction):
    if is_valid_transaction(transaction):
        transaction_list.append(transaction)
        transaction_list.sort(
            key = lambda transaction: transaction['date'],
            reverse = True,
        )
    else:
        print('Invalid transaction!')

def edit_transaction(transaction, index):
    if is_valid_transaction(transaction):
        transaction_list[index] = transaction
    else:
        print('Invalid transaction! Failied')

def delete_transaction(index):
    transaction_list.pop(index)

def print_transaction_list():
    for transaction in transaction_list:
        print_transaction(transaction)

# Each account is a dict and should belong to one of the basic types of account_list:
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
    if account['account_name'] in get_account_name_list():
        return False
    elif account['account_code'] and account['account_code'] in get_account_code_list():
        return False
    elif account['account_type'] not in account_types:
        return False
    else:
        return True

def calculate_account_balance(account):
    return sum(split['amount']
        for transaction in transaction_list \
            for split in transaction['splits'] \
                if split['account_name'] == account['account_name'])

def print_account_detail(account):
    print('-'*5 + 'Account Information' + '-'*6)
    print('Name:', account['account_name'], 'Code:', account['account_code'])
    print('Type:', account['account_type'])
    print('Description:', account['description'])
    print('Balance:', calculate_account_balance(account))
    print('-'*30)


# account_list operations
def get_account_name_list():
    for account in account_list:
        yield account['account_name']

def get_account_code_list():
    for account in account_list:
        yield account['account_code']

def add_account(account):
    if is_valid_account(account):
        account_list.append(account)
        account_list.sort(
            key = lambda account: account['account_name']
        )
    else:
        print('Invalid Account!')

def edit_account(account_name, new_account):
    if is_valid_account(new_account):
        if new_account['account_name'] != account_name:
            replace_account_name_in_splits(account_name, new_account['name'])
        account_list[index] = new_account
        account_list.sort(
            key = lambda new_account: new_account['account_name']
        )
    else:
        print('Invalid Account!')

def delete_account(account_name, move_to_account_name = 'Imbalance'):
    deleting_account_name = account_name
    if move_to_account_name == 'Imbalance' and 'Imbalance' not in get_account_name_list():
        add_account(create_account('Imbalance', 'equity'))
    if move_to_account_name in get_account_name_list():
        replace_account_name_in_splits(account_name, move_to_account_name)
        account_list.pop([get_account_name_list].index(account_name))
    # delete related transaction when move_to_account_name is None
    elif move_to_account_name is None:
        new_transaction_list = []
        for transaction in transaction_list:
            if not involves_account(transaction, deleting_account_name):
                new_transaction_list.append(transaction)
        transaction_list = new_transaction_list
        account_list.pop([get_account_name_list].index(account_name))
    else:
        print('Invalid new account name!')

def print_account_list_detail():
    for account in account_list:
        print_account_detail(account)

if __name__ == '__main__':
    # initialize account_list
    add_account(create_account('資產::流動資產::現金', 'asset'))
    add_account(create_account('資產::點數紅利::深藏咖啡點數', 'asset'))
    add_account(create_account('支出::飲食::飲料', 'expense'))
    add_account(create_account('支出::飲食::晚餐', 'expense'))
    add_account(create_account('資產::流動資產::悠遊卡', 'asset'))


    t1 = create_transaction(
        date(2017, 1, 20),
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
    print_transaction_list()
    print_account_list_detail()
