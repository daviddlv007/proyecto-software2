package com.supermercado.graphql;

import com.supermercado.auth.AuthService;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Controller
public class AuthResolver {

    private final AuthService authService;

    public AuthResolver(AuthService authService) {
        this.authService = authService;
    }

    @MutationMapping
    public AuthService.AuthResponse register(@Argument Map<String, String> input) {
        String nombre = input.get("nombre");
        String correo = input.get("correo");
        String contrasena = input.get("contrasena");
        
        return authService.register(nombre, correo, contrasena);
    }

    @MutationMapping
    public AuthService.AuthResponse login(@Argument Map<String, String> input) {
        String correo = input.get("correo");
        String contrasena = input.get("contrasena");
        
        return authService.login(correo, contrasena);
    }
}