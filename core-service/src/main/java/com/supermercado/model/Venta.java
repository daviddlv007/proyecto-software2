package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import com.supermercado.model.Cliente;

@Data
@Entity
public class Venta {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne
    private Cliente cliente;
    private LocalDateTime fecha;
    private Double total;
}
