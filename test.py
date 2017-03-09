import track

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
