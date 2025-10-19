package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.Producto;

public interface ProductoRepository extends JpaRepository<Producto, Long> {}
