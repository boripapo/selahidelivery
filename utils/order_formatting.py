def get_formatted_order(order):
    formatted_message = (
        f"<b>Заказ:</b> <code>{order["id"]}</code>\n"
        f"<b>Имя:</b> {order["name"]}\n"
        f"<b>Телефон:</b> <code>{order["phone"]}</code>\n"
        f"<b>Адрес:</b> {order["address"]}\n"
        f"<b>Способ оплаты:</b> {order["payment_method"]}\n\n"
        f"<i>{order["comment"]}</i>"
    )
    return formatted_message

def get_formatted_new_order(order):
    formatted_message = (
        f"<b>Новый заказ:</b> <code>{order["id"]}</code>\n"
        f"<b>Имя:</b> {order["name"]}\n"
        f"<b>Телефон:</b> <code>{order["phone"]}</code>\n"
        f"<b>Адрес:</b> {order["address"]}\n"
        f"<b>Способ оплаты:</b> {order["payment_method"]}\n\n"
        f"<i>{order["comment"]}</i>"
    )
    return formatted_message