package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;
import lombok.ToString;
import java.time.LocalDateTime;
import java.util.List;
import java.util.ArrayList;

@Data
@ToString(exclude = {"detalles"})  // Excluir detalles del toString para evitar recursión
@Entity
@Table(name = "ventas")
public class Venta {
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cliente_id", nullable = false)
    private Cliente cliente;
    
    @Column(nullable = false)
    private LocalDateTime fecha;
    
    @Column(nullable = false)
    private Double total;
    
    @OneToMany(mappedBy = "venta", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.EAGER)
    private List<DetalleVenta> detalles = new ArrayList<>();

    // Campos para Payments
    @Column(name = "payment_provider", length = 20)
    private String paymentProvider;

    @Column(name = "payment_status", length = 20)
    private String paymentStatus;

    @Column(name = "checkout_session_id", length = 100)
    private String checkoutSessionId;

    @Column(name = "payment_intent_id", length = 100)
    private String paymentIntentId;

    @Column(name = "qr_checkout_url", length = 5000)
    private String qrCheckoutUrl;

    @Column(name = "currency", length = 10)
    private String currency = "USD";

    // Campos para Delivery
    @Column(name = "delivery_status", length = 20)
    private String deliveryStatus;

    @Column(name = "delivery_address", length = 500)
    private String deliveryAddress;

    @Column(name = "delivery_lat")
    private Double deliveryLat;

    @Column(name = "delivery_lng")
    private Double deliveryLng;

    @Column(name = "delivery_distance_km")
    private Double deliveryDistanceKm;

    @Column(name = "delivery_fee")
    private Double deliveryFee;

    @Column(name = "delivery_eta_minutes")
    private Integer deliveryEtaMinutes;

    @Column(name = "delivery_rider_id", length = 50)
    private String deliveryRiderId;


    // Método de conveniencia para calcular total automáticamente
    public void calcularTotal() {
        this.total = detalles.stream()
            .mapToDouble(detalle -> detalle.getCantidad() * detalle.getPrecioUnitario())
            .sum();
    }
    
    // Método para agregar detalle manteniendo la relación bidireccional
    public void addDetalle(DetalleVenta detalle) {
        detalles.add(detalle);
        detalle.setVenta(this);
    }
}
