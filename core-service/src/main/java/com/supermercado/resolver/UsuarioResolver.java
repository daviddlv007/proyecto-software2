package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import com.supermercado.model.Usuario;
import com.supermercado.repository.UsuarioRepository;
import com.supermercado.input.UsuarioInput;

@Controller
public class UsuarioResolver {
    private final UsuarioRepository repository;

    public UsuarioResolver(UsuarioRepository repository) {
        this.repository = repository;
    }

    @QueryMapping
    public List<Usuario> usuarios() {
        return repository.findAll();
    }

    @MutationMapping
    public Usuario createUsuario(@Argument UsuarioInput input) {
        Usuario obj = new Usuario();
        obj.setNombre(input.getNombre());
        obj.setCorreo(input.getCorreo());
        obj.setContrasena(input.getContrasena());
        return repository.save(obj);
    }

    @MutationMapping
    public Usuario updateUsuario(@Argument Long id, @Argument UsuarioInput input) {
        Usuario obj = repository.findById(id).orElseThrow();
        if (input.getNombre() != null) obj.setNombre(input.getNombre());
        if (input.getCorreo() != null) obj.setCorreo(input.getCorreo());
        if (input.getContrasena() != null) obj.setContrasena(input.getContrasena());
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteUsuario(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
