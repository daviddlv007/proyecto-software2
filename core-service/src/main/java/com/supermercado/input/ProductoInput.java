package com.supermercado.input;

import lombok.Data;

@Data  
public class ProductoInput {
    private String nombre;
    private String descripcion;
    private String imagenUrl;
    private Double precio;
    private Integer stock;
    private String categoriaId;
    
    public Long getCategoriaIdAsLong() {
        return categoriaId != null ? Long.parseLong(categoriaId) : null;
    }
}