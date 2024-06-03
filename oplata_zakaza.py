import stripe

# Установите ваш секретный ключ Stripe
stripe.api_key = 'your_secret_key'

def process_payment(user_id, order_id, card_number, exp_month, exp_year, cvc, amount):
    """
    Функция для обработки оплаты заказа банковской картой.

    Параметры:
    user_id: ID пользователя
    order_id: ID заказа
    card_number: Номер банковской карты
    exp_month: Месяц окончания срока действия карты (MM)
    exp_year: Год окончания срока действия карты (YYYY)
    cvc: CVC код карты
    amount: Сумма к оплате в копейках (например, 1000 копеек = 10 рублей)
    """
    try:
        # Создаем токен карты
        token = stripe.Token.create(
            card={
                "number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
        )

        # Создаем платеж
        charge = stripe.Charge.create(
            amount=amount,  # Сумма в копейках
            currency="rub",
            description=f"Order {order_id} payment by user {user_id}",
            source=token.id,
        )

        # Возвращаем информацию о платеже
        return {"status": "success", "charge_id": charge.id, "amount": charge.amount}
    except stripe.error.CardError as e:
        # Обработка ошибок карты
        return {"status": "error", "message": str(e)}
    except Exception as e:
        # Обработка других ошибок
        return {"status": "error", "message": "An error occurred. Please try again later."}

# Пример использования функции
user_id = 1
order_id = 12345
card_number = '4242424242424242'
exp_month = 12
exp_year = 2024
cvc = '123'
amount = 1000  # 1000 копеек = 10 рублей

result = process_payment(user_id, order_id, card_number, exp_month, exp_year, cvc, amount)
print(result)

'''Импорт библиотеки Stripe: Импортируется библиотека Stripe для работы с API.
Настройка секретного ключа: Устанавливается секретный ключ API, который вы получите при регистрации на сайте Stripe.
Функция process_payment:
Параметры: Функция принимает идентификаторы пользователя и заказа, данные карты (номер, месяц и год окончания срока действия, CVC код) и сумму оплаты в копейках.
Создание токена карты: Создается токен карты с использованием переданных данных.
Создание платежа: Создается платеж с использованием токена карты.
Возврат результата: Возвращается результат оплаты. В случае успеха возвращается идентификатор платежа и сумма. В случае ошибки возвращается сообщение об ошибке.
Пример использования: Приведен пример использования функции с тестовыми данными.
Эту функцию можно интегрировать в систему заказа еды, чтобы обрабатывать оплату заказов банковскими картами. Не забудьте заменить тестовые данные и API ключ на реальные данные вашей системы.'''





