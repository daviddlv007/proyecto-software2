package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.Categoria;

public interface CategoriaRepository extends JpaRepository<Categoria, Long> {}
