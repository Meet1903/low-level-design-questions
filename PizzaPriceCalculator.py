from enum import Enum
from typing import List

class Size(Enum):
    SMALL = ('Small', 5.00)
    MEDIUM = ('Medium', 7.00)
    LARGE = ('Large', 10.00)

    def __init__(self, description: str, base_price: float):
        self.description = description
        self.base_price = base_price

class Topping:
    def __init__(self, name: str, cost: float):
        self.name = name
        self.cost = cost

    def __str__(self):
        return f"{self.name} (${self.cost:.2f})"

class Crust(Enum):
    CHEESY = ('Cheesy', 2.00)
    THIN = ('Thin', 1.50)
    THICK = ('Thick', 2.50)

    def __init__(self, description: str, crust_price: float):
        self.description = description
        self.crust_price = crust_price

class Pizza:
    def __init__(self, size: Size, crust: Crust):
        self.size = size
        self.crust = crust
        self.toppings: List[Topping] = []

    def add_topping(self, topping: Topping):
        """Add a topping to the pizza."""
        self.toppings.append(topping)

    def calculate_price(self) -> float:
        """
        Calculate the total price of the pizza.
        Total = Base Price (size) + Crust Price + Sum of Topping Costs.
        """
        total_price = self.size.base_price + self.crust.crust_price
        total_price += sum(topping.cost for topping in self.toppings)
        return total_price

    def __str__(self):
        toppings_str = ', '.join(str(t) for t in self.toppings) if self.toppings else 'No Toppings'
        return (f"{self.size.description} Pizza with {self.crust.description} crust, "
                f"Toppings: {toppings_str} - Price: ${self.calculate_price():.2f}")

class PizzaOrder:
    def __init__(self):
        self.pizzas: List[Pizza] = []

    def add_pizza(self, pizza: Pizza):
        """Add a pizza to the order."""
        self.pizzas.append(pizza)

    def calculate_total(self) -> float:
        """Calculate the total price for the entire order."""
        return sum(pizza.calculate_price() for pizza in self.pizzas)

    def __str__(self):
        pizzas_str = "\n".join(str(pizza) for pizza in self.pizzas)
        total = self.calculate_total()
        return f"Pizza Order:\n{pizzas_str}\nTotal: ${total:.2f}"


# Example usage:
if __name__ == "__main__":
    # Create some toppings
    pepperoni = Topping("Pepperoni", 1.50)
    mushrooms = Topping("Mushrooms", 1.00)
    olives = Topping("Olives", 1.00)

    # Create a large pizza with a thick crust and add toppings
    pizza1 = Pizza(Size.LARGE, Crust.THICK)
    pizza1.add_topping(pepperoni)
    pizza1.add_topping(mushrooms)

    # Create a medium pizza with a thin crust and add a topping
    pizza2 = Pizza(Size.MEDIUM, Crust.THIN)
    pizza2.add_topping(olives)

    # Create an order and add the pizzas
    order = PizzaOrder()
    order.add_pizza(pizza1)
    order.add_pizza(pizza2)

    # Output the order details
    print(order)