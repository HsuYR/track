from track import Book
from datetime import date

book = Trackbook()

# initialize account_list
book.add_account('資產::流動資產::現金', 'asset')
book.add_account('資產::點數紅利::深藏咖啡點數', 'asset')
book.add_account('支出::飲食::飲料', 'expense')
book.add_account('支出::飲食::晚餐', 'expense')
book.add_account('資產::流動資產::悠遊卡', 'asset')

book.add_transaction(
    date(2017, 1, 20),
    [
    book.create_split(-60, '資產::流動資產::現金'),
    book.create_split(54, '支出::飲食::飲料', '深藏咖啡'),
    book.create_split(6, '資產::點數紅利::深藏咖啡點數', '深藏咖啡點數'),
    ],
    description = '熱摩卡無糖',
    tags = '',
    )

book.add_transaction(
    date.today(),
    [
    book.create_split(69, '支出::飲食::晚餐', '頂好 嘉義文蛤'),
    book.create_split(-69, '資產::流動資產::悠遊卡', '一仁悠遊卡'),
    ],
    description = '頂好 嘉義文蛤',
    tags = '過年 家裡開火',
)

for transaction in book.transactions:
    book.show_transaction(transaction)

for account in book.accounts:
    book.show_account(account)
