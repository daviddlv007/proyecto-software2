package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.Cliente;

public interface ClienteRepository extends JpaRepository<Cliente, Long> {}
