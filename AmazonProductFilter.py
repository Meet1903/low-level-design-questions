from abc import ABC, abstractmethod
from typing import List

class Product:
    def __init__(self, product_id: int, name: str, category: str, price: float, brand: str, rating: float):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.brand = brand
        self.rating = rating

    def __repr__(self) -> str:
        return (f"Product(id={self.product_id}, name='{self.name}', category='{self.category}', "
                f"price={self.price}, brand='{self.brand}', rating={self.rating})")

# Abstract Base Class for Filter Criteria
class FilterCriteria(ABC):
    @abstractmethod
    def filter(self, products: List[Product]) -> List[Product]:
        """Return a filtered list of products."""
        pass

# Concrete Filter Criteria: CategoryFilter
class CategoryFilter(FilterCriteria):
    def __init__(self, category: str):
        self.category = category

    def filter(self, products: List[Product]) -> List[Product]:
        return [product for product in products if product.category.lower() == self.category.lower()]

# Concrete Filter Criteria: PriceFilter
class PriceFilter(FilterCriteria):
    def __init__(self, min_price: float, max_price: float):
        self.min_price = min_price
        self.max_price = max_price

    def filter(self, products: List[Product]) -> List[Product]:
        return [product for product in products if self.min_price <= product.price <= self.max_price]

# Concrete Filter Criteria: BrandFilter
class BrandFilter(FilterCriteria):
    def __init__(self, brand: str):
        self.brand = brand

    def filter(self, products: List[Product]) -> List[Product]:
        return [product for product in products if product.brand.lower() == self.brand.lower()]

# Concrete Filter Criteria: RatingFilter
class RatingFilter(FilterCriteria):
    def __init__(self, min_rating: float):
        self.min_rating = min_rating

    def filter(self, products: List[Product]) -> List[Product]:
        return [product for product in products if product.rating >= self.min_rating]

# ProductFilter Class that applies multiple filter criteria
class ProductFilter:
    def __init__(self):
        self.criteria_list: List[FilterCriteria] = []

    def add_criteria(self, criteria: FilterCriteria) -> None:
        """Add a new filter criterion."""
        self.criteria_list.append(criteria)

    def filter(self, products: List[Product]) -> List[Product]:
        """
        Apply all added criteria sequentially.
        Each criterion is applied to the product list, reducing it further.
        """
        filtered_products = products
        for criteria in self.criteria_list:
            filtered_products = criteria.filter(filtered_products)
        return filtered_products

# Example usage:
if __name__ == "__main__":
    # Sample list of products
    products = [
        Product(1, "Wireless Mouse", "Electronics", 25.99, "Logitech", 4.5),
        Product(2, "Gaming Keyboard", "Electronics", 79.99, "Razer", 4.7),
        Product(3, "Water Bottle", "Home", 15.99, "Nalgene", 4.2),
        Product(4, "Bluetooth Speaker", "Electronics", 45.50, "JBL", 4.4),
        Product(5, "Coffee Maker", "Home", 99.99, "Keurig", 4.0),
        Product(6, "Mechanical Keyboard", "Electronics", 89.99, "Logitech", 4.8)
    ]

    # Instantiate a ProductFilter and add criteria
    product_filter = ProductFilter()
    product_filter.add_criteria(CategoryFilter("Electronics"))
    product_filter.add_criteria(PriceFilter(30.00, 100.00))
    product_filter.add_criteria(RatingFilter(4.5))
    # Uncomment the following line to also filter by brand "Logitech"
    # product_filter.add_criteria(BrandFilter("Logitech"))

    # Get filtered products
    filtered_products = product_filter.filter(products)
    print("Filtered Products:")
    for product in filtered_products:
        print(product)
