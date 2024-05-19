from aiogram import Router, html, F
from aiogram.filters import CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.keyboard import main_kb, credit_type_kb, deposit_type_kb, end_kb

router = Router()


class CreditInfo(StatesGroup):
    setting_total = State()
    setting_period = State()
    setting_rate = State()


class DepositInfo(StatesGroup):
    setting_total = State()
    setting_period = State()
    setting_rate = State()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f'Привет, {html.bold(message.from_user.full_name)}!\n\n'
                         f'Данный бот поможет вам лучше управлять своими финансами.\n\n'
                         f'Выберите, что вы хотите сделать:', reply_markup=main_kb)


@router.message(CreditInfo.setting_total)
async def set_credit_total_handler(message: Message, state: FSMContext):
    await state.update_data(credit_total=float(''.join(message.text.strip().split())))
    await message.answer('Введите срок кредита в мес. (число вида XX):')
    await state.set_state(CreditInfo.setting_period)


@router.message(CreditInfo.setting_period)
async def set_credit_period_handler(message: Message, state: FSMContext):
    await state.update_data(credit_period=int(message.text.strip()))
    await message.answer('Введите процентную ставку (число вида XX.XX):')
    await state.set_state(CreditInfo.setting_rate)


@router.message(CreditInfo.setting_rate)
async def set_credit_rate_handler(message: Message, state: FSMContext):
    await state.update_data(credit_rate=float(message.text.strip()))

    user_credit_data = await state.get_data()
    user_credit_type = user_credit_data['credit_type']
    user_credit_total = user_credit_data['credit_total']
    user_credit_period = user_credit_data['credit_period']
    user_credit_rate = user_credit_data['credit_rate']
    user_credit_rate_dec = user_credit_rate / 100 / 12

    if user_credit_type == 1:
        user_credit_type_string = 'Аннуитетный'
        monthly_payment = (user_credit_total *
                           (user_credit_rate_dec + (user_credit_rate_dec /
                                                    (pow((1 + user_credit_rate_dec), user_credit_period) - 1))))
        overpayment = monthly_payment * user_credit_period - user_credit_total

        msg = (f'Ежемесячный платеж составит: {html.bold(f'{round(monthly_payment, 2)} ₽')}.\n'
               f'Переплата по процентам составит: {html.bold(f'{round(overpayment, 2)} ₽')}.')
    else:
        user_credit_type_string = 'Дифференцированный'
        overpayment = 0
        debt_part = user_credit_total / user_credit_period
        remaining = user_credit_total
        msg = 'График платежей по каждому месяцу:\n'

        for i in range(user_credit_period):
            accrued_interest = remaining * user_credit_rate_dec
            total_payment = debt_part + accrued_interest
            remaining -= debt_part
            overpayment += accrued_interest
            msg += f'{html.bold(f'{i + 1})')} {round(total_payment, 2)} {html.bold('₽')}.\n'

        msg += f'\nПереплата по процентам составит: {html.bold(f'{round(overpayment, 2)} ₽')}.'

    await message.answer(f'Данные о вашем кредите:\n'
                         f'Сумма кредита: {html.bold(f'{user_credit_total} ₽')}\n'
                         f'Тип кредита: {html.bold(f'{user_credit_type_string}')}\n'
                         f'Срок кредита: {html.bold(f'{user_credit_period} мес')}.\n'
                         f'Процентная ставка: {html.bold(f'{user_credit_rate} %')}\n\n'
                         f'{msg}',
                         reply_markup=end_kb)
    await state.clear()


@router.message(DepositInfo.setting_total)
async def set_deposit_total_handler(message: Message, state: FSMContext):
    await state.update_data(deposit_total=float(''.join(message.text.strip().split())))
    await message.answer('Введите годовую процентную ставку (число вида XX.XX):')
    await state.set_state(DepositInfo.setting_rate)


@router.message(DepositInfo.setting_rate)
async def set_deposit_period_handler(message: Message, state: FSMContext):
    await state.update_data(deposit_rate=float(message.text.strip()))
    await message.answer('Введите срок вклада в годах (число):')
    await state.set_state(DepositInfo.setting_period)


@router.message(DepositInfo.setting_period)
async def set_deposit_total_handler(message: Message, state: FSMContext):
    await state.update_data(deposit_period=int(message.text.strip()))

    user_deposit_data = await state.get_data()
    user_deposit_type = user_deposit_data['deposit_type']
    user_deposit_total = user_deposit_data['deposit_total']
    user_deposit_period = user_deposit_data['deposit_period']
    user_deposit_rate = user_deposit_data['deposit_rate']

    current_total = user_deposit_total

    if user_deposit_type == 1:
        user_deposit_type_string = 'С капитализацией'
        previous_payment = 0

        for i in range(user_deposit_period * 12):
            previous_payment = ((current_total + previous_payment) * (user_deposit_rate / 100) /
                                (user_deposit_period * 12))
            current_total += previous_payment

        total_income = current_total - user_deposit_total
        effective_rate = total_income * 100 / user_deposit_total

        msg = (f'К концу срока баланс Вашего банковского счета составит: {html.bold(f'{round(current_total, 2)} ₽')}\n'
               f'Итоговый доход составит: {html.bold(f'{round(total_income, 2)} ₽')}\n'
               f'Эффективная ставка составит: {html.bold(f'{round(effective_rate, 2)} %')}\n')
    else:
        user_deposit_type_string = 'Без капитализации'
        income = 0

        for i in range(user_deposit_period):
            income += user_deposit_total * (user_deposit_rate / 100)
            current_total += income

        msg = (f'К концу срока на Вашем банковском счету станет: {html.bold(f'{round(current_total, 2)} ₽')}\n'
               f'Итоговый доход составит: {html.bold(f'{round(income, 2)} ₽')}\n')

    await message.answer(f'Информация по Вашему вкладу:\n'
                         f'Сумма вклада: {html.bold(f'{user_deposit_total} ₽')}\n'
                         f'Тип вклада: {html.bold(f'{user_deposit_type_string}')}\n'
                         f'Срок вклада: {html.bold(f'{user_deposit_period} г')}.\n'
                         f'Процентная ставка (годовая): {html.bold(f'{user_deposit_rate} %')}\n\n'
                         f'{msg}',
                         reply_markup=end_kb)
    await state.clear()


@router.callback_query(F.data == 'main1')
async def button1_handler(query: CallbackQuery):
    await query.message.answer('Выберите вид платежа:', reply_markup=credit_type_kb)


@router.callback_query(F.data == 'main2')
async def button2_handler(query: CallbackQuery):
    await query.message.answer('Выберите тип вклада:', reply_markup=deposit_type_kb)


@router.callback_query(F.data.in_(['credit_type1', 'credit_type2']))
async def set_credit_type_handler(query: CallbackQuery, state: FSMContext):
    credit_type = 1
    if query.data == 'credit_type2':
        credit_type = 2

    await state.update_data(credit_type=credit_type)
    await query.message.answer('Введите сумму кредита в ₽ (число вида XXXX.XX):')
    await state.set_state(CreditInfo.setting_total)


@router.callback_query(F.data.in_(['deposit_type1', 'deposit_type2']))
async def set_deposit_type_handler(query: CallbackQuery, state: FSMContext):
    deposit_type = 1
    if query.data == 'deposit_type2':
        deposit_type = 2

    await state.update_data(deposit_type=deposit_type)
    await query.message.answer('Введите сумму вклада в ₽ (число вида XXXX.XX):')
    await state.set_state(DepositInfo.setting_total)


@router.callback_query(F.data == 'end1')
async def button_4_handler(query: CallbackQuery):
    await query.message.answer(f'{html.bold('Главное меню')}\n\n'
                               f'Выберите, что вы хотите сделать:', reply_markup=main_kb)
