package com.boripapa.selahidelivery.service;

import com.boripapa.selahidelivery.dto.OrderRequest;
import com.boripapa.selahidelivery.entity.Order;
import com.boripapa.selahidelivery.entity.OrderItem;
import com.boripapa.selahidelivery.entity.PaymentMethod;
import com.boripapa.selahidelivery.repository.OrderRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.stream.Collectors;

@Service
public class OrderService {
    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @Transactional
    public Order createOrder(OrderRequest req) {
        Order order = new Order();
        order.setName(req.getName());
        order.setPhone(req.getPhone());
        order.setAddress(req.getAddress());
        order.setComment(req.getComment());
        order.setPaymentMethod(PaymentMethod.valueOf(req.getPaymentMethod()));

        var items = req.getItems().stream().map(i -> {
            OrderItem item = new OrderItem();
            item.setProductId(i.getId());
            item.setName(i.getName());
            item.setPrice(i.getPrice().doubleValue() != 0 ?
                    java.math.BigDecimal.valueOf(i.getPrice()) : java.math.BigDecimal.ZERO);
            item.setQuantity(i.getQuantity());
            item.setOrder(order);
            return item;
        }).collect(Collectors.toList());

        order.setItems(items);
        return orderRepository.save(order);
    }
}
