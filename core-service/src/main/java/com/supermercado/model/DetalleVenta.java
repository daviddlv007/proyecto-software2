package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
public class DetalleVenta {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "venta_id", nullable = false)
    private Venta venta;
    
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "producto_id", nullable = false)
    private Producto producto;
    
    @Column(nullable = false)
    private Integer cantidad;
    
    @Column(nullable = false)
    private Double precioUnitario;
    
    // Campo calculado para el subtotal
    public Double getSubtotal() {
        return cantidad != null && precioUnitario != null ? 
            cantidad * precioUnitario : 0.0;
    }
}
