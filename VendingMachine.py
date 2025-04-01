from abc import ABC, abstractclassmethod
from enum import Enum
from typing import Dict, List
import uuid

class PaymentMethod(Enum):
    CASH = 1
    CARD = 2
    MOBILE_PAYMENT = 3

class VendingMachineStatus(Enum):
    IDLE = 1
    ITEM_SELECTED = 2
    PAYMENT_PENDING = 3
    DISPENSING = 4
    OUT_OF_SERVICE = 5

class Product:
    def __init__(self, name: str, price: float, quantity: int):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def is_available(self):
        return self.quantity > 0

    def decrease_quantity(self):
        if self.is_available():
            self.quantity -= 1

class PaymentProcessor(ABC):
    @abstractclassmethod
    def process_payment(self, amount: float) -> bool:
        pass

class CashPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        pass

class CreditCardPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        pass

class VendingMachine:
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.current_state = VendingMachineStatus.IDLE
        self.selected_priduct: Product = None
        self.payment_processor: PaymentProcessor = None
        self.current_balance = 0
    
    def add_product(self, product: Product):
        self.products[product.id] = product
    
    def select_product(self, product_id: str):
        if product_id not in self.products:
            raise ValueError("Product not found")

        product = self.products[product_id]

        if not product.is_available():
            raise ValueError('Product out of stock')
        
        self.selected_priduct = product
        self.current_state = VendingMachineStatus.ITEM_SELECTED
    
    def select_payment_method(self, method: PaymentMethod):
        if self.current_state != VendingMachineStatus.ITEM_SELECTED:
            raise ValueError("No product selected")

        if method == PaymentMethod.CASH:
            self.payment_processor = CashPaymentProcessor()
        elif method == PaymentMethod.CARD:
            self.payment_processor = CreditCardPaymentProcessor()
        else:
            raise ValueError("Unsupported payment method")

        self.current_state = VendingMachineStatus.PAYMENT_PENDING
    
    def insert_money(self, amount):
        if self.current_state != VendingMachineStatus.PAYMENT_PENDING:
            raise ValueError("Invalid state for inserting money")
        self.current_balance = amount
    
    def dispense_product(self):
        if self.current_state != VendingMachineStatus.PAYMENT_PENDING:
            raise ValueError("Invalid state for dispensing")

        if self.current_balance < self.selected_product.price:
            raise ValueError("Insufficient funds")

        if not self.payment_processor.process_payment(self.selected_product.price):
            raise ValueError("Payment failed")

        self.selected_product.decrease_quantity()
        self.current_state = VendingMachineStatus.DISPENSING

        change = self.current_balance - self.selected_product.price
        
        self.reset()
        
        return change
    
    def reset(self):
        self.current_state = VendingMachineStatus.IDLE
        self.selected_product = None
        self.payment_processor = None
        self.current_balance = 0.0

    def get_available_products(self) -> List[Product]:
        return [product for product in self.products.values() if product.is_available()]

if __name__ == '__main__':
    vm = VendingMachine()

    cola = Product("Cola", 1.50, 10)
    chips = Product("Chips", 1.00, 5)
    candy = Product("Candy", 0.75, 8)

    vm.add_product(cola)
    vm.add_product(chips)
    vm.add_product(candy)

    try:
        vm.select_product(cola.id)
        vm.select_payment_method(PaymentMethod.CASH)
        vm.insert_money(2.00)
        change = vm.dispense_product()
    except:
        print("Error")