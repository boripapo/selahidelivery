package com.boripapa.selahidelivery.controller;

import com.boripapa.selahidelivery.dto.OrderRequest;
import com.boripapa.selahidelivery.entity.Order;
import com.boripapa.selahidelivery.service.OrderService;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/order")
public class OrderController {
    private final OrderService orderService;
    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ResponseEntity<String> placeOrder(@Validated @RequestBody OrderRequest req) {
        Order saved = orderService.createOrder(req);
        return ResponseEntity.ok("Заказ №" + saved.getId() + " оформлен");
    }
}
