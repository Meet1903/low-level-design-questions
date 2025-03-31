class User:
    def __init__(self, userID, name, email):
        self.userID = userID
        self.name = name
        self.email = email
        self.cart = Cart(self)
        self.orders = []
    
    def add_to_cart(self, product, quantity):
        self.cart.add_product(product, quantity)

    def remove_from_cart(self, product, quantity):
        self.cart.remove_product(product, quantity)

    def place_order(self):
        # Create an order using the products currently in the cart
        order = Order(self.cart.products.copy())
        self.orders.append(order)
        self.cart.empty_cart()  # clear the cart after placing the order
        return order

    def view_orders(self):
        return self.orders


class Product:
    def __init__(self, productID, name, price, stock):
        self.productID = productID
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product({self.productID}, {self.name}, {self.price}, stock={self.stock})"


class Cart:
    def __init__(self, user):
        self.user = user
        self.products = {}  # key: Product, value: quantity

    def add_product(self, product, quantity):
        if quantity > product.stock:
            print(f"Cannot add {quantity}. Only {product.stock} left in stock.")
        else:
            self.products[product] = self.products.get(product, 0) + quantity
            product.stock -= quantity
        
    def remove_product(self, product, quantity):
        if product not in self.products:
            print("Product not in cart.")
        elif quantity > self.products[product]:
            print(f"Cannot remove {quantity}. You only have {self.products[product]} in your cart.")
        else:
            self.products[product] -= quantity
            if self.products[product] == 0:
                del self.products[product]
            product.stock += quantity
        
    def view_cart(self):
        return self.products
    
    def empty_cart(self):
        # When emptying the cart, we should return the products to stock.
        for product, quantity in self.products.items():
            product.stock += quantity
        self.products.clear()


class Order:
    order_count = 0

    def __init__(self, products):
        Order.order_count += 1
        self.order_id = Order.order_count
        # products is a dictionary with Product objects and their quantity at the time of order
        self.products = products  
        self.status = 'Placed'
        self.payment = None  # payment will be linked later

    def add_payment(self, payment):
        self.payment = payment

    def __repr__(self):
        return f"Order(id={self.order_id}, status={self.status}, products={self.products})"


class Payment:
    def __init__(self, order, amount, payment_type):
        self.order = order
        self.amount = amount
        self.payment_type = payment_type
        self.status = 'Pending'

    def process_payment(self):
        # Here you might add external payment gateway integrations
        # For now, we simply mark the payment as completed.
        self.status = 'Completed'
        # You can update the order status here as well.
        self.order.status = 'Paid'
        
    def __repr__(self):
        return f"Payment(order_id={self.order.order_id}, amount={self.amount}, type={self.payment_type}, status={self.status})"


# Example usage:
if __name__ == "__main__":
    # Create some products
    product1 = Product(1, "Laptop", 1200, 10)
    product2 = Product(2, "Headphones", 150, 20)

    # Create a user
    user = User(100, "Alice", "alice@example.com")

    # Add products to the cart
    user.add_to_cart(product1, 1)
    user.add_to_cart(product2, 2)

    print("Cart contents:", user.cart.view_cart())

    # Place an order
    order = user.place_order()
    print("Order placed:", order)

    # Create a payment for the order
    total_amount = sum(product.price * quantity for product, quantity in order.products.items())
    payment = Payment(order, total_amount, "Credit Card")
    payment.process_payment()
    order.add_payment(payment)

    print("Order after payment:", order)
    print("Payment details:", payment)
