package com.boripapa.selahidelivery.repository;

import com.boripapa.selahidelivery.entity.OrderItem;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {
}
