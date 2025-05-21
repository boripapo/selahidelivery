package com.boripapa.selahidelivery.dto;

import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class OrderRequest {
    @NotBlank
    @Size(max = 30)
    private String name;

    @Pattern(regexp = "\\+375\\d{9}")
    private String phone;

    @NotBlank
    private String address;

    private String comment;

    @NotNull
    private String paymentMethod;

    @NotEmpty
    private List<ItemDto> items;

    @Getter
    @Setter
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ItemDto {
        @NotNull private Long id;
        @NotBlank private String name;
        @NotNull private Double price;
        @NotNull @Min(1) private Integer quantity;
    }
}