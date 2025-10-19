package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.Venta;

public interface VentaRepository extends JpaRepository<Venta, Long> {}
