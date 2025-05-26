package com.boripapa.selahidelivery.entity;

public enum OrderStatus {
    NEW, //Новый, необработанный админом
    REJECTED, //Отклонён админом
    ASSIGNED, //Назначен курьеру
    CANCELED, //Отклонён курьером, возвращается админу
    IN_DELIVERY, //Доставляется
    DELIVERED, //Успешно доставлен
    CLOSED //Закрыт, присваивается всем заказам по закрытию смены либо по завершению работы программы
}
