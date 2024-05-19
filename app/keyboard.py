from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать кредит', callback_data='main1')],
        [InlineKeyboardButton(text='Рассчитать выплаты по вкладу', callback_data='main2')],
        # [InlineKeyboardButton(text='Игра "52 недели богатства"', callback_data='main3')]
    ]
)

credit_type_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Аннуитетный', callback_data='credit_type1')],
        [InlineKeyboardButton(text='Дифференцированный', callback_data='credit_type2')]
    ]
)

deposit_type_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='С капитализацией', callback_data='deposit_type1')],
        [InlineKeyboardButton(text='Без капитализации', callback_data='deposit_type2')]
    ]
)

end_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться в главное меню', callback_data='end1')]
    ]
)
