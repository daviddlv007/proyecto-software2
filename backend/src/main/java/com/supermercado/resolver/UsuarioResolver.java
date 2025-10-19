package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import com.supermercado.model.Usuario;
import com.supermercado.repository.UsuarioRepository;

@Controller
public class UsuarioResolver {
    private final UsuarioRepository repository;

    public UsuarioResolver(UsuarioRepository repository) {
        this.repository = repository;
    }

    @QueryMapping
    public List<Usuario> allUsuarios() {
        return repository.findAll();
    }

    @MutationMapping
    public Usuario createUsuario(@Argument String nombre, @Argument String correo, @Argument String contrasena) {
        Usuario obj = new Usuario();
        obj.setNombre(nombre);
        obj.setCorreo(correo);
        obj.setContrasena(contrasena);
        return repository.save(obj);
    }

    @MutationMapping
    public Usuario updateUsuario(@Argument Long id, @Argument String nombre, @Argument String correo, @Argument String contrasena) {
        Usuario obj = repository.findById(id).orElseThrow();
        if (nombre != null) obj.setNombre(nombre);
        if (correo != null) obj.setCorreo(correo);
        if (contrasena != null) obj.setContrasena(contrasena);
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteUsuario(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
