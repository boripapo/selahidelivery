package com.boripapa.selahidelivery.entity;

public enum OrderStatus {
    NEW, //Новый, необработанный админом
    REJECTED, //Отклонён админом
    ASSIGNED, //Назначен курьеру
    CANCELED, //Отклонён курьером, возвращается админу
    DELIVERED, //Доставлен
    CLOSED //Закрыт (финальный)
}
