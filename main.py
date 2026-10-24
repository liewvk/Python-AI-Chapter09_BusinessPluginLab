# main.py

import asyncio
import sys

from openai import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError
)

from business_plugins import parse_amount

from kernel_service import BusinessKernelService

from settings import MODEL_NAME


def show_menu():

    print("\n======================================")
    print("         BUSINESS PLUGIN LAB")
    print("======================================")

    print("1. List registered plugin functions")
    print("2. List sample products")
    print("3. Retrieve product information")
    print("4. Calculate purchase total")
    print("5. Apply a discount")
    print("6. Check sample order status")
    print("7. Generate a quotation")
    print("8. Explain the latest result with AI")
    print("0. Exit")


def read_text(label):

    value = input(label).strip()

    if not value:

        raise ValueError(
            "Input cannot be empty."
        )

    if len(value) > 100:

        raise ValueError(
            "Input is too long."
        )

    return value


def read_quantity():

    text = read_text(
        "Enter quantity: "
    )

    try:

        quantity = int(text)

    except ValueError:

        raise ValueError(
            "Quantity must be a whole number."
        )

    if quantity < 1 or quantity > 1000:

        raise ValueError(
            "Quantity must be between 1 and 1000."
        )

    return quantity


async def main():

    service = BusinessKernelService()

    print("======================================")
    print("   SEMANTIC KERNEL BUSINESS PLUGINS")
    print("   Visual Studio 2026")
    print("======================================")

    print("Model:", MODEL_NAME)

    print(
        "Python interpreter:",
        sys.executable
    )

    try:

        while True:

            show_menu()

            try:

                choice = input(
                    "\nSelect an option: "
                ).strip()

                if choice == "0":

                    print("Goodbye!")
                    break

                elif choice == "1":

                    result = (
                        service.list_registered_functions()
                    )

                    print(result)

                elif choice == "2":

                    result = await service.invoke(
                        "Catalog",
                        "list_products"
                    )

                    print("\nAvailable Products:")
                    print(result)

                elif choice == "3":

                    name = read_text(
                        "Enter product name: "
                    )

                    result = await service.invoke(
                        "Catalog",
                        "get_product",
                        product_name=name
                    )

                    print("\nProduct Information:")
                    print(result)

                elif choice == "4":

                    price = read_text(
                        "Enter unit price: "
                    )

                    quantity = read_quantity()

                    result = await service.invoke(
                        "Calculator",
                        "calculate_total",
                        unit_price=price,
                        quantity=quantity
                    )

                    print("\nCalculation:")
                    print(result)

                elif choice == "5":

                    subtotal = read_text(
                        "Enter subtotal: "
                    )

                    percent = read_text(
                        "Enter discount percentage: "
                    )

                    result = await service.invoke(
                        "Business",
                        "apply_discount",
                        subtotal=subtotal,
                        discount_percent=percent
                    )

                    print("\nDiscount Calculation:")
                    print(result)

                elif choice == "6":

                    order_id = read_text(
                        "Enter sample order ID: "
                    )

                    result = await service.invoke(
                        "Business",
                        "get_order_status",
                        order_id=order_id
                    )

                    print("\nOrder Information:")
                    print(result)

                elif choice == "7":

                    name = read_text(
                        "Enter product name: "
                    )

                    quantity = read_quantity()

                    percent = read_text(
                        "Enter discount percentage: "
                    )

                    result = await service.create_quotation(
                        name,
                        quantity,
                        percent
                    )

                    print("\n" + result)

                elif choice == "8":

                    print(
                        "\nRequesting a Qwen 3.5 explanation..."
                    )

                    answer = (
                        await service.explain_last_result()
                    )

                    print("\nAI Explanation:")
                    print(answer)

                else:

                    print(
                        "Invalid menu option."
                    )

            except (EOFError, KeyboardInterrupt):

                print("\nGoodbye!")
                break

            except ValueError as exc:

                print(
                    "\nInput or calculation error:",
                    exc
                )

            except APIConnectionError:

                print(
                    "\nCannot connect to Ollama."
                )

                print(
                    "Check the local server."
                )

            except APITimeoutError:

                print(
                    "\nThe AI request timed out."
                )

            except APIStatusError as exc:

                print(
                    "\nAI API error:",
                    exc.status_code
                )

            except Exception as exc:

                print(
                    "\nOperation failed:",
                    exc
                )

    finally:

        await service.close()


if __name__ == "__main__":

    asyncio.run(main())

