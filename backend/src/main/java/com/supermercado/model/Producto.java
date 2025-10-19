package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;
import com.supermercado.model.Categoria;

@Data
@Entity
public class Producto {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nombre;
    private String descripcion;
    private String imagenUrl;
    private Double precio;
    private Integer stock;
    @ManyToOne
    private Categoria categoria;
}
