package com.supermercado.model;
import jakarta.persistence.*;
import lombok.Data;

@Data
@Entity
public class Categoria {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String nombre;
    private String descripcion;
}
