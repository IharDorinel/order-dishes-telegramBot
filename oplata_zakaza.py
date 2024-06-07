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

# Пример использования функции с тестовыми данными
user_id = "example_user_id"
order_id = "example_order_id"
card_number = "4242424242424242"  # Тестовый номер карты Stripe
exp_month = 12
exp_year = 2024
cvc = "123"
amount = 1000  # 1000 копеек = 10 рублей

result = process_payment(user_id, order_id, card_number, exp_month, exp_year, cvc, amount)
print(result)