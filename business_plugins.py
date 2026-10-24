# business_plugins.py

from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP
)

from semantic_kernel.functions import kernel_function


CENT = Decimal("0.01")


def parse_amount(value, label):
    """Convert and validate a nonnegative decimal amount."""

    try:

        number = Decimal(str(value).strip())

    except (InvalidOperation, ValueError):

        raise ValueError(
            f"{label} must be a valid number."
        )

    if not number.is_finite():

        raise ValueError(
            f"{label} must be finite."
        )

    if number < 0 or number > Decimal("1000000"):

        raise ValueError(
            f"{label} must be between 0 and 1000000."
        )

    return number


def money(value):
    """Format a decimal value as Malaysian ringgit."""

    rounded = value.quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )

    return f"RM{rounded:,.2f}"


class CalculatorPlugin:

    @kernel_function(
        name="calculate_total",
        description=(
            "Calculates a purchase total from "
            "unit price and quantity."
        )
    )
    def calculate_total(
        self,
        unit_price: str,
        quantity: int
    ) -> str:

        price = parse_amount(
            unit_price,
            "Unit price"
        )

        if type(quantity) is not int:

            raise ValueError(
                "Quantity must be an integer."
            )

        if quantity < 1 or quantity > 1000:

            raise ValueError(
                "Quantity must be between 1 and 1000."
            )

        total = price * quantity

        return (
            f"Unit price: {money(price)}\n"
            f"Quantity: {quantity}\n"
            f"Total: {money(total)}"
        )
class ProductCatalogPlugin:

    def __init__(self):

        self.products = {

            "laptop": {
                "name": "Laptop",
                "price": "3500.00",
                "stock": 15
            },

            "monitor": {
                "name": "Monitor",
                "price": "850.00",
                "stock": 30
            },

            "keyboard": {
                "name": "Keyboard",
                "price": "120.00",
                "stock": 8
            }
        }

    def get_record(self, product_name):
        """Return a copy of a matching product record."""

        key = product_name.strip().lower()

        product = self.products.get(key)

        if product is None:
            return None

        return product.copy()

    @kernel_function(
        name="list_products",
        description="Lists products and their prices."
    )
    def list_products(self) -> str:

        lines = []

        for product in self.products.values():

            price = money(
                Decimal(product["price"])
            )

            lines.append(
                f"{product['name']}: {price}, "
                f"stock {product['stock']}"
            )

        return "\n".join(lines)

    @kernel_function(
        name="get_product",
        description=(
            "Retrieves the price and stock quantity "
            "of a named product."
        )
    )
    def get_product(
        self,
        product_name: str
    ) -> str:

        product = self.get_record(
            product_name
        )

        if product is None:

            return (
                "Product not found. "
                "Available products: "
                "Laptop, Monitor, Keyboard."
            )

        return (
            f"Product: {product['name']}\n"
            f"Price: {money(Decimal(product['price']))}\n"
            f"Stock: {product['stock']} units"
        )
class BusinessOperationsPlugin:

    def __init__(self):

        self.orders = {
            "ORD-1001": "Processing",
            "ORD-1002": "Ready for collection",
            "ORD-1003": "Completed"
        }

    @kernel_function(
        name="apply_discount",
        description=(
            "Applies a percentage discount "
            "to a purchase subtotal."
        )
    )
    def apply_discount(
        self,
        subtotal: str,
        discount_percent: str
    ) -> str:

        amount = parse_amount(
            subtotal,
            "Subtotal"
        )

        percent = parse_amount(
            discount_percent,
            "Discount percentage"
        )

        if percent > 100:

            raise ValueError(
                "Discount percentage cannot exceed 100."
            )

        discount = (
            amount * percent / Decimal("100")
        ).quantize(
            CENT,
            rounding=ROUND_HALF_UP
        )

        final_total = amount - discount

        return (
            f"Subtotal: {money(amount)}\n"
            f"Discount: {percent}%\n"
            f"Discount amount: {money(discount)}\n"
            f"Final total: {money(final_total)}"
        )

    @kernel_function(
        name="get_order_status",
        description=(
            "Retrieves the status of a sample order."
        )
    )
    def get_order_status(
        self,
        order_id: str
    ) -> str:

        key = order_id.strip().upper()

        status = self.orders.get(key)

        if status is None:

            return (
                "Sample order not found. "
                "Available IDs: ORD-1001, "
                "ORD-1002, ORD-1003."
            )

        return (
            f"Sample Order: {key}\n"
            f"Status: {status}"
        )

