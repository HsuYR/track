from track import Trackbook
from datetime import date


book = Trackbook()

while True:
    cmd = input('Your order sir? ')
    if cmd == 'quit':
        print('My pleasure!')
        break
    elif cmd == 'add account':
        name = input('Account name sir? ')
        if name in book.accounts:
            print('Sorry sir, the name has been taken.')
            break
        _type = input('Account type sir? ')
        if _type not in book.account_types:
            print('Sorry sir, we don\'t have this kind of account.')
            break
        description = input('Account description sir?\n')
        hidden = input('Account hidden sir?')
        if hidden == 'yes':
            hidden = True
        else:
            hidden = False
        book.add_account(name, _type, description, hidden)
        print('The following account has been added:')
        book.show_account(name)
    elif cmd == 'add transaction':
        pass
    else:
        print('Pardon me sir, I don\'t understand.')
