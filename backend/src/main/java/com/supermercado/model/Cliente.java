package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
public class Cliente {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nombre;
    private String correo;
    private String telefono;
}
