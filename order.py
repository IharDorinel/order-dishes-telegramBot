
# Класс для представления блюда меню
class MenuItem:
    def __init__(self, dish_name, price):
        self.dish_name = dish_name
        self.price = price

# Класс для управления заказом
class OrderPositions:
    def __init__(self):
        self.items = {}

# Добавление блюда в заказ
    def add_item(self, item: MenuItem, quantity: int):
        if item.name in self.items:
            self.items[item.name]['quantity'] += quantity
        else:
            self.items[item.name] = {'item': item, 'quantity': quantity}

# Удаление блюда из заказа
    def remove_item(self, item_name: str):
        if item_name in self.items:
            del self.items[item_name]

# Вывод сформированного заказа
    def get_order_summary(self):
        summary = ""
        total_cost = 0
        for item_name, details in self.items.items():
            item = details['item']
            quantity = details['quantity']
            cost = item.price * quantity
            summary += f"{item_name}: {quantity} x {item.price} = {cost}\n"
            total_cost += cost
        summary += f"\nTotal: {total_cost}"
        return summary