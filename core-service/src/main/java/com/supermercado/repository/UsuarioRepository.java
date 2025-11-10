package com.supermercado.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.supermercado.model.Usuario;
import java.util.Optional;

public interface UsuarioRepository extends JpaRepository<Usuario, Long> {
    Optional<Usuario> findByCorreo(String correo);
}