from datetime import datetime


def get_formatted_order(order, items):
    created_at = order["created_at"]
    assert isinstance(created_at, datetime)

    lines = []
    for item in items:
        lines.append(f"{item["name"]} x {item["quantity"]} - <b>{item["price"] * item["quantity"]}</b>")
    items_str = "\n".join(lines)

    formatted_message = (
        f"<i>{created_at.strftime("%Y-%m-%d %H:%M")}</i>\n\n"
        f"<b>Заказ:</b> <code>{order["id"]}</code>\n"
        f"<b>Имя:</b> {order["name"]}\n"
        f"<b>Телефон:</b> <code>{order["phone"]}</code>\n"
        f"<b>Адрес:</b> {order["address"]}\n"
        f"<b>Способ оплаты:</b> {order["payment_method"]}\n\n"
        f"{items_str}\n"
        f"<i>{order["comment"]}</i>"
    )
    return formatted_message

def get_formatted_new_order(order, items):
    created_at = order["created_at"]
    assert isinstance(created_at, datetime)

    lines = []
    for item in items:
        lines.append(f"{item["name"]} x {item["quantity"]} - <b>{item["price"] * item["quantity"]}</b>")
    items_str = "\n".join(lines)

    formatted_message = (
        f"<i>{created_at.strftime("%Y-%m-%d %H:%M")}</i>\n\n"
        f"<b>Новый заказ:</b> <code>{order["id"]}</code>\n"
        f"<b>Имя:</b> {order["name"]}\n"
        f"<b>Телефон:</b> <code>{order["phone"]}</code>\n"
        f"<b>Адрес:</b> {order["address"]}\n"
        f"<b>Способ оплаты:</b> {order["payment_method"]}\n\n"
        f"{items_str}\n"
        f"<i>{order["comment"]}</i>"
    )
    return formatted_message