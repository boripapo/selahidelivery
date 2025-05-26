from datetime import datetime


def get_formatted_order(order, items):
    created_at = order["created_at"]
    assert isinstance(created_at, datetime)

    lines = []
    total_price = 0
    for item in items:
        total_price += item["price"] * item["quantity"]
        lines.append(f"▫️ {item["name"]} x {item["quantity"]} - <b>{item["price"] * item["quantity"]} р.</b>")
    items_str = "\n".join(lines)

    formatted_message = (
        f"<i>{created_at.strftime("%Y-%m-%d %H:%M")}</i>\n\n"
        f"<b>{"Новый " if order["status"] == "NEW" else ""}заказ:</b> <code>{order["id"]}</code>\n"
        f"<b>Имя:</b> {order["name"]}\n"
        f"<b>Телефон:</b> <code>{order["phone"]}</code>\n"
        f"<b>Адрес:</b> {order["address"]}\n\n"
        f"{items_str}\n\n"
        f"<u>Общая сумма:</u> <b>{total_price} р.</b> - {"наличными" if order["payment_method"] == "CASH" else "картой" if order["payment_method"] == "CARD" else ""}\n\n"
        f"<i>{order["comment"]}</i>"
    )
    return formatted_message