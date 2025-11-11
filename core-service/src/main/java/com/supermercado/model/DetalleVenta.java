package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;
import lombok.ToString;

@Data
@ToString(exclude = {"venta"})  // Excluir venta del toString para evitar recursión
@Entity
@Table(name = "detalle_ventas")
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
    
    @Column(nullable = false)
    private Double subtotal;
    
    // Calcular el subtotal automáticamente
    public void calcularSubtotal() {
        this.subtotal = cantidad != null && precioUnitario != null ? 
            cantidad * precioUnitario : 0.0;
    }
    
    // Getter para compatibilidad (mantener el método existente)
    public Double getSubtotal() {
        return subtotal;
    }
}
