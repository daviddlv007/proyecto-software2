package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;
import com.supermercado.model.Venta;
import com.supermercado.model.Producto;

@Data
@Entity
public class DetalleVenta {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne
    private Venta venta;
    @ManyToOne
    private Producto producto;
    private Integer cantidad;
    private Double precioUnitario;
}
