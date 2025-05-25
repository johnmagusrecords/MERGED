from typing import TypedDict


class OrderItem(TypedDict):
    code: str
    name: str
    price: float
    quantity: int
    total: float
    description: str
    image: str


def create_order_item(
    code: str, name: str, price: float, quantity: int, description: str, image: str
) -> OrderItem:
    """
    Create an OrderItem object from the given parameters.

    Args:
        code (str): The item code.
        name (str): The item name.
        price (float): The item price.
        quantity (int): The item quantity.
        description (str): The item description.
        image (str): The item image URL.

    Returns:
        OrderItem: The created OrderItem object.
    """
    return {
        "code": code,
        "name": name,
        "price": price,
        "quantity": quantity,
        "total": price * quantity,
        "description": description,
        "image": image,
    }
