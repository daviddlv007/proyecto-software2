package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.Usuario;

public interface UsuarioRepository extends JpaRepository<Usuario, Long> {}
