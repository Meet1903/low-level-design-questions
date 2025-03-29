from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class ItemType(Enum):
    FLAVOR = "flavor"
    TOPPING = "topping"
    CONTAINER = "container"

class ContainerType(Enum):
    CONE = "cone"
    CUP = "cup"
    WAFFLE_CONE = "waffle_cone"
    BOWL = "bowl"

class OrderStatus(Enum):
    CREATED = "created"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    MOBILE_PAYMENT = "mobile_payment"
    GIFT_CARD = "gift_card"


class Item:
    def __init__(self, id, name, price, item_type, is_available):
        self.id = id
        self.name = name
        self.price = price
        self.type = item_type
        self.is_available = is_available

class IceCreamFlavor(Item):
    def __init__(self, id: str, name: str, price: float, is_dairy_free: bool, 
                 is_sugar_free: bool, quantity_in_stock: int):
        super().__init__(id, name, price, ItemType.FLAVOR, quantity_in_stock > 0)
        self.is_dairy_free = is_dairy_free
        self.is_sugar_free = is_sugar_free
        self.quantity_in_stock = quantity_in_stock

class Topping(Item):
    def __init__(self, id: str, name: str, price: float, is_vegan: bool, quantity_in_stock: int):
        super().__init__(id, name, price, ItemType.TOPPING, quantity_in_stock > 0)
        self.is_vegan = is_vegan
        self.quantity_in_stock = quantity_in_stock

class Container(Item):
    def __init__(self, id: str, name: str, price: float, container_type: ContainerType, quantity_in_stock: int):
        super().__init__(id, name, price, ItemType.CONTAINER, quantity_in_stock > 0)
        self.container_type = container_type
        self.quantity_in_stock = quantity_in_stock

class IceCreamScoop:
    def __init__(self, flavor: IceCreamFlavor):
        self.flavor = flavor
        self.toppings: List[Topping] = []
    
    def add_topping(self, topping: Topping):
        self.toppings.append(topping)
    
    def calculate_price(self) -> float:
        price = self.flavor.price
        for topping in self.toppings:
            price += topping.price
        return price
    
class IceCream:
    def __init__(self, id: str, container: Container):
        self.id = id
        self.container = container
        self.scoops: List[IceCreamScoop] = []
    
    def add_scoop(self, scoop: IceCreamScoop):
        self.scoops.append(scoop)
    
    def calculate_price(self) -> float:
        price = self.container.price
        for scoop in self.scoops:
            price += scoop.calculate_price()
        return price
    
class Customer:
    def __init__(self, id: str, name: str, phone: str, email: str):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.order_history: List[Order] = []

class Order:
    def __init__(self, id: str, customer: Customer):
        self.id = id
        self.customer = customer
        self.items: List[IceCream] = []
        self.order_time = datetime.now()
        self.status = OrderStatus.CREATED
        self.payment = None
    
    def add_item(self, ice_cream: IceCream):
        self.items.append(ice_cream)
    
    def calculate_total(self) -> float:
        total = 0
        for ice_cream in self.items:
            total += ice_cream.calculate_price()
        return total
    
    def update_status(self, status: OrderStatus):
        self.status = status

class Payment:
    def __init__(self, id: str, order: Order, amount: float, method: PaymentMethod):
        self.id = id
        self.order = order
        self.amount = amount
        self.method = method
        self.status = PaymentStatus.PENDING
        self.transaction_time = datetime.now()
    
    def process_payment(self):
        # Logic to process payment
        self.status = PaymentStatus.COMPLETED

class InventoryService:
    def __init__(self):
        self.flavors: Dict[str, IceCreamFlavor] = {}
        self.toppings: Dict[str, Topping] = {}
        self.containers: Dict[str, Container] = {}
    
    def add_flavor(self, flavor: IceCreamFlavor):
        self.flavors[flavor.id] = flavor
    
    def add_topping(self, topping: Topping):
        self.toppings[topping.id] = topping
    
    def add_container(self, container: Container):
        self.containers[container.id] = container
    
    def get_flavor(self, id: str) -> Optional[IceCreamFlavor]:
        return self.flavors.get(id)
    
    def get_topping(self, id: str) -> Optional[Topping]:
        return self.toppings.get(id)
    
    def get_container(self, id: str) -> Optional[Container]:
        return self.containers.get(id)
    
    def update_flavor_stock(self, id: str, quantity: int) -> bool:
        if id in self.flavors:
            flavor = self.flavors[id]
            new_quantity = flavor.quantity_in_stock + quantity
            if new_quantity >= 0:
                flavor.quantity_in_stock = new_quantity
                flavor.is_available = new_quantity > 0
                return True
        return False
    
    def update_topping_stock(self, id: str, quantity: int) -> bool:
        if id in self.toppings:
            topping = self.toppings[id]
            new_quantity = topping.quantity_in_stock + quantity
            if new_quantity >= 0:
                topping.quantity_in_stock = new_quantity
                topping.is_available = new_quantity > 0
                return True
        return False
    
    def update_container_stock(self, id: str, quantity: int) -> bool:
        if id in self.containers:
            container = self.containers[id]
            new_quantity = container.quantity_in_stock + quantity
            if new_quantity >= 0:
                container.quantity_in_stock = new_quantity
                container.is_available = new_quantity > 0
                return True
        return False
    
    def get_available_flavors(self) -> List[IceCreamFlavor]:
        return [flavor for flavor in self.flavors.values() if flavor.is_available]
    
    def get_available_toppings(self) -> List[Topping]:
        return [topping for topping in self.toppings.values() if topping.is_available]
    
    def get_available_containers(self) -> List[Container]:
        return [container for container in self.containers.values() if container.is_available]

class CustomerService:
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
    
    def add_customer(self, customer: Customer):
        self.customers[customer.id] = customer
    
    def get_customer(self, id: str) -> Optional[Customer]:
        return self.customers.get(id)
    
    def find_customer_by_phone(self, phone: str) -> Optional[Customer]:
        for customer in self.customers.values():
            if customer.phone == phone:
                return customer
        return None
    
    def update_customer(self, customer: Customer) -> bool:
        if customer.id in self.customers:
            self.customers[customer.id] = customer
            return True
        return False

class OrderService:
    def __init__(self, inventory_service: InventoryService):
        self.orders: Dict[str, Order] = {}
        self.inventory_service = inventory_service
    
    def create_order(self, customer: Customer) -> Order:
        order_id = f"ORD-{uuid.uuid4().hex[:8]}"
        order = Order(order_id, customer)
        self.orders[order_id] = order
        return order
    
    def add_item_to_order(self, order_id: str, ice_cream: IceCream) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status == OrderStatus.CREATED:
                # Check inventory before adding
                inventory_available = self._check_and_update_inventory(ice_cream, -1)
                if inventory_available:
                    order.add_item(ice_cream)
                    return True
        return False

    def _check_and_update_inventory(self, ice_cream: IceCream, multiplier: int) -> bool:
        # Check container availability
        container_id = ice_cream.container.id
        if not self.inventory_service.update_container_stock(container_id, multiplier):
            return False
        
        # Check each scoop and its toppings
        for scoop in ice_cream.scoops:
            flavor_id = scoop.flavor.id
            if not self.inventory_service.update_flavor_stock(flavor_id, multiplier):
                # Rollback container stock change
                self.inventory_service.update_container_stock(container_id, -multiplier)
                return False
            
            for topping in scoop.toppings:
                topping_id = topping.id
                if not self.inventory_service.update_topping_stock(topping_id, multiplier):
                    # Rollback container and flavor stock changes
                    self.inventory_service.update_container_stock(container_id, -multiplier)
                    self.inventory_service.update_flavor_stock(flavor_id, -multiplier)
                    return False
        
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            order.update_status(status)
            return True
        return False
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status != OrderStatus.DELIVERED:
                order.update_status(OrderStatus.CANCELLED)
                
                # Return items to inventory
                for ice_cream in order.items:
                    self._check_and_update_inventory(ice_cream, 1)
                
                # Handle payment refund if needed
                if order.payment and order.payment.status == PaymentStatus.COMPLETED:
                    order.payment.status = PaymentStatus.REFUNDED
                
                return True
        return False

class PaymentService:
    def __init__(self):
        self.payments: Dict[str, Payment] = {}
    
    def create_payment(self, order: Order, method: PaymentMethod) -> Payment:
        payment_id = f"PAY-{uuid.uuid4().hex[:8]}"
        amount = order.calculate_total()
        payment = Payment(payment_id, order, amount, method)
        self.payments[payment_id] = payment
        order.payment = payment
        return payment
    
    def process_payment(self, payment_id: str) -> bool:
        if payment_id in self.payments:
            payment = self.payments[payment_id]
            # Simulate payment processing
            payment.process_payment()
            return True
        return False
    
    def get_payment(self, payment_id: str) -> Optional[Payment]:
        return self.payments.get(payment_id)

class IceCreamShopFacade:
    def __init__(self):
        self.inventory_service = InventoryService()
        self.customer_service = CustomerService()
        self.order_service = OrderService(self.inventory_service)
        self.payment_service = PaymentService()
        
        # Initialize with some data
        self._initialize_inventory()
    
    def _initialize_inventory(self):
        # Add some flavors
        self.inventory_service.add_flavor(IceCreamFlavor("F1", "Vanilla", 2.5, False, False, 100))
        self.inventory_service.add_flavor(IceCreamFlavor("F2", "Chocolate", 2.5, False, False, 100))
        self.inventory_service.add_flavor(IceCreamFlavor("F3", "Strawberry", 2.75, False, False, 80))
        self.inventory_service.add_flavor(IceCreamFlavor("F4", "Mint Chocolate Chip", 3.0, False, False, 60))
        self.inventory_service.add_flavor(IceCreamFlavor("F5", "Dairy-Free Vanilla", 3.5, True, False, 40))
        
        # Add some toppings
        self.inventory_service.add_topping(Topping("T1", "Chocolate Chips", 0.75, False, 200))
        self.inventory_service.add_topping(Topping("T2", "Sprinkles", 0.5, True, 300))
        self.inventory_service.add_topping(Topping("T3", "Hot Fudge", 1.0, False, 150))
        self.inventory_service.add_topping(Topping("T4", "Whipped Cream", 0.5, False, 200))
        self.inventory_service.add_topping(Topping("T5", "Nuts", 0.75, True, 180))
        
        # Add some containers
        self.inventory_service.add_container(Container("C1", "Regular Cone", 1.0, ContainerType.CONE, 200))
        self.inventory_service.add_container(Container("C2", "Waffle Cone", 1.5, ContainerType.WAFFLE_CONE, 150))
        self.inventory_service.add_container(Container("C3", "Cup Small", 0.75, ContainerType.CUP, 250))
        self.inventory_service.add_container(Container("C4", "Cup Large", 1.25, ContainerType.CUP, 200))
        self.inventory_service.add_container(Container("C5", "Bowl", 1.0, ContainerType.BOWL, 100))
    
    # Customer related operations
    def register_customer(self, name: str, phone: str, email: str) -> Customer:
        customer_id = f"CUS-{uuid.uuid4().hex[:8]}"
        customer = Customer(customer_id, name, phone, email)
        self.customer_service.add_customer(customer)
        return customer
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        return self.customer_service.get_customer(customer_id)
    
    def find_customer_by_phone(self, phone: str) -> Optional[Customer]:
        return self.customer_service.find_customer_by_phone(phone)
    
    # Menu related operations
    def get_available_flavors(self) -> List[IceCreamFlavor]:
        return self.inventory_service.get_available_flavors()
    
    def get_available_toppings(self) -> List[Topping]:
        return self.inventory_service.get_available_toppings()
    
    def get_available_containers(self) -> List[Container]:
        return self.inventory_service.get_available_containers()
    
    # Order related operations
    def create_order(self, customer_id: str) -> Optional[Order]:
        customer = self.customer_service.get_customer(customer_id)
        if customer:
            return self.order_service.create_order(customer)
        return None
    
    def create_ice_cream(self, container_id: str) -> Optional[IceCream]:
        container = self.inventory_service.get_container(container_id)
        if container and container.is_available:
            ice_cream_id = f"ICE-{uuid.uuid4().hex[:8]}"
            return IceCream(ice_cream_id, container)
        return None
    
    def create_scoop(self, flavor_id: str) -> Optional[IceCreamScoop]:
        flavor = self.inventory_service.get_flavor(flavor_id)
        if flavor and flavor.is_available:
            return IceCreamScoop(flavor)
        return None
    
    def add_topping_to_scoop(self, scoop: IceCreamScoop, topping_id: str) -> bool:
        topping = self.inventory_service.get_topping(topping_id)
        if topping and topping.is_available:
            scoop.add_topping(topping)
            return True
        return False
    
    def add_scoop_to_ice_cream(self, ice_cream: IceCream, scoop: IceCreamScoop) -> bool:
        ice_cream.add_scoop(scoop)
        return True
    
    def add_ice_cream_to_order(self, order_id: str, ice_cream: IceCream) -> bool:
        return self.order_service.add_item_to_order(order_id, ice_cream)
    
    def place_order(self, order_id: str) -> bool:
        order = self.order_service.get_order(order_id)
        if order and order.status == OrderStatus.CREATED:
            self.order_service.update_order_status(order_id, OrderStatus.PREPARING)
            return True
        return False
    
    def complete_order(self, order_id: str) -> bool:
        order = self.order_service.get_order(order_id)
        if order and order.status == OrderStatus.PREPARING:
            self.order_service.update_order_status(order_id, OrderStatus.READY)
            return True
        return False
    
    def deliver_order(self, order_id: str) -> bool:
        order = self.order_service.get_order(order_id)
        if order and order.status == OrderStatus.READY:
            self.order_service.update_order_status(order_id, OrderStatus.DELIVERED)
            return True
        return False
    
    def cancel_order(self, order_id: str) -> bool:
        return self.order_service.cancel_order(order_id)
    
    # Payment related operations
    def create_payment(self, order_id: str, method: PaymentMethod) -> Optional[Payment]:
        order = self.order_service.get_order(order_id)
        if order:
            return self.payment_service.create_payment(order, method)
        return None
    
    def process_payment(self, payment_id: str) -> bool:
        return self.payment_service.process_payment(payment_id)
    
    # Inventory management operations
    def restock_flavor(self, flavor_id: str, quantity: int) -> bool:
        return self.inventory_service.update_flavor_stock(flavor_id, quantity)
    
    def restock_topping(self, topping_id: str, quantity: int) -> bool:
        return self.inventory_service.update_topping_stock(topping_id, quantity)
    
    def restock_container(self, container_id: str, quantity: int) -> bool:
        return self.inventory_service.update_container_stock(container_id, quantity)
    

if __name__=='main'():
    # Initialize the system
    shop = IceCreamShopFacade()
    
    # Register a customer
    customer = shop.register_customer("John Doe", "555-123-4567", "john@example.com")
    
    # Create a new order
    order = shop.create_order(customer.id)
    
    # Create an ice cream with a waffle cone
    ice_cream = shop.create_ice_cream("C2")  # Waffle cone
    
    # Add a scoop of vanilla
    vanilla_scoop = shop.create_scoop("F1")  # Vanilla
    
    # Add toppings to the scoop
    shop.add_topping_to_scoop(vanilla_scoop, "T2")  # Sprinkles
    shop.add_topping_to_scoop(vanilla_scoop, "T4")  # Whipped Cream
    
    # Add the scoop to the ice cream
    shop.add_scoop_to_ice_cream(ice_cream, vanilla_scoop)
    
    # Add a second scoop of chocolate
    chocolate_scoop = shop.create_scoop("F2")  # Chocolate
    shop.add_topping_to_scoop(chocolate_scoop, "T3")  # Hot Fudge
    shop.add_scoop_to_ice_cream(ice_cream, chocolate_scoop)
    
    # Add the ice cream to the order
    shop.add_ice_cream_to_order(order.id, ice_cream)
    
    # Create a second ice cream
    ice_cream2 = shop.create_ice_cream("C4")  # Cup Large
    mint_scoop = shop.create_scoop("F4")  # Mint Chocolate Chip
    shop.add_topping_to_scoop(mint_scoop, "T1")  # Chocolate Chips
    shop.add_scoop_to_ice_cream(ice_cream2, mint_scoop)
    shop.add_ice_cream_to_order(order.id, ice_cream2)
    
    # Create payment
    payment = shop.create_payment(order.id, PaymentMethod.CREDIT_CARD)
    
    # Process payment
    shop.process_payment(payment.id)
    
    # Place order
    shop.place_order(order.id)
    
    # Complete order preparation
    shop.complete_order(order.id)
    
    # Deliver order to customer
    shop.deliver_order(order.id)
    
    print("Order completed successfully!")
    print(f"Total amount: ${payment.amount:.2f}")