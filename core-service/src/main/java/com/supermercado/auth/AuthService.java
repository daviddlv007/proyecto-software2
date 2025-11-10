package com.supermercado.auth;

import com.supermercado.model.Usuario;
import com.supermercado.repository.UsuarioRepository;
import com.supermercado.security.JwtTokenProvider;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UsuarioRepository usuarioRepo;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtProvider;

    public AuthService(UsuarioRepository usuarioRepo, 
                      PasswordEncoder passwordEncoder,
                      JwtTokenProvider jwtProvider) {
        this.usuarioRepo = usuarioRepo;
        this.passwordEncoder = passwordEncoder;
        this.jwtProvider = jwtProvider;
    }

    @Transactional
    public AuthResponse register(String nombre, String correo, String contrasena) {
        if (usuarioRepo.findByCorreo(correo).isPresent()) {
            throw new IllegalArgumentException("El usuario ya existe");
        }

        Usuario usuario = new Usuario();
        usuario.setNombre(nombre);
        usuario.setCorreo(correo);
        usuario.setContrasena(passwordEncoder.encode(contrasena));
        
        usuarioRepo.save(usuario);

        String token = jwtProvider.generateToken(correo, "USER");
        
        return new AuthResponse(token, usuario.getId(), nombre, correo);
    }

    public AuthResponse login(String correo, String contrasena) {
        Usuario usuario = usuarioRepo.findByCorreo(correo)
            .orElseThrow(() -> new IllegalArgumentException("Credenciales inválidas"));

        if (!passwordEncoder.matches(contrasena, usuario.getContrasena())) {
            throw new IllegalArgumentException("Credenciales inválidas");
        }

        String token = jwtProvider.generateToken(correo, "USER");
        
        return new AuthResponse(token, usuario.getId(), usuario.getNombre(), correo);
    }

    public record AuthResponse(String token, Long userId, String nombre, String correo) {}
}