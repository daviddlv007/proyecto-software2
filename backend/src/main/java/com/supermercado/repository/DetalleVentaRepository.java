package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.DetalleVenta;

public interface DetalleVentaRepository extends JpaRepository<DetalleVenta, Long> {}
