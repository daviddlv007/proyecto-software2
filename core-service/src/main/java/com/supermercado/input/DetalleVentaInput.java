package com.supermercado.input;

import lombok.Data;

@Data
public class DetalleVentaInput {
    private String productoId;
    private Integer cantidad;
    private Double precioUnitario;
    
    public Long getProductoIdAsLong() {
        return productoId != null ? Long.parseLong(productoId) : null;
    }
}