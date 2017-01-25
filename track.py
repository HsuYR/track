# Written in Python 3

# Basic entry unit
# Each entry represents
# (1) Dr.(true)/Cr.(false) (2) certain account for (3) certain amount of currency

class Track:
    """Track holds a ledger containing all information.

    Ledger holds all accounts and their information.
    """
    def __init__(self, default = True):
        """Initialize Track with a ledger.

        Ledger is a list holding all accounts,
        in which each item contains account information, a dict.
        Optional initialization of ledger with default settings.
        """
        self.ledger = []
        # setup with default settings
        if default == True:
            self.add_account("Cash", True)
            self.add_account("Deposit", True, "Bank deposit")
            self.add_account("Salary", False, "Salary income")

    #
    # Account management
    #
    def add_account(self, name, isReal, description = None):
        """Add a new account to the ledger list.

        name is the account name.
        name should not be the same as any existing account name.
        name will be normalized with strip().

        isReal should be
        either True for real account, which includes assets and liabilities,
        or False for nominal account, which includes incomes and expenses.

        description is an optional account description string.
        """
        # strip name string
        name = name.strip()
        if name not in self.accounts('name'):
            self.ledger.append({'name': name,
                                'isReal': isReal,
                                'description': description,
                                'transactions': []
                                })
            print("Account \'%s\' created" % name)
        else:
            print("Account already exists!")

    def update_account(self, index, key, value):
        """Update account information."""
        self.ledger[index][key] = value
        print("\'%s\' on index %s updated as \'%s\'" % (key, index, value))

    def delete_account(self, index):
        """Delete a given account"""
        name = self.ledger[index]['name']
        del self.ledger[index]
        print("Account \'%s\' deleted at index %s." % (name, index))

    def accounts(self, key):
        """Generator for values of given key from all accounts."""
        for account in self.ledger:
            yield account[key]

    def print_account(self, index, account):
        print("Account", index)
        if account['isReal']:
            print(account['name'] + " is a real account.")
        else:
            print(account['name'] + " is a nominal account.")
        print("Description:", account['description'])

    def show_account(self, index = None):
        if index is not None:
            self.print_account(index, self.ledger[index])
        else:
            for i, account in enumerate(self.ledger):
                self.print_account(i, account)

    #
    # Transaction management
    #
    def add_transaction(self):
        pass

    #
    # Report management
    #

if __name__ == '__main__':
    track = Track()
    print()
    track.show_account()
    print()
    track.add_account('Food expenses', False)
    track.update_account(0, 'description', 'Cash in my wallet')
    track.delete_account(1)
    print()
    track.show_account()
    print()
    track.show_account(1)
