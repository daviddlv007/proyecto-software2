package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import com.supermercado.model.Cliente;
import com.supermercado.repository.ClienteRepository;

@Controller
public class ClienteResolver {
    private final ClienteRepository repository;

    public ClienteResolver(ClienteRepository repository) {
        this.repository = repository;
    }

    @QueryMapping
    public List<Cliente> allClientes() {
        return repository.findAll();
    }

    @MutationMapping
    public Cliente createCliente(@Argument String nombre, @Argument String correo, @Argument String telefono) {
        Cliente obj = new Cliente();
        obj.setNombre(nombre);
        obj.setCorreo(correo);
        obj.setTelefono(telefono);
        return repository.save(obj);
    }

    @MutationMapping
    public Cliente updateCliente(@Argument Long id, @Argument String nombre, @Argument String correo, @Argument String telefono) {
        Cliente obj = repository.findById(id).orElseThrow();
        if (nombre != null) obj.setNombre(nombre);
        if (correo != null) obj.setCorreo(correo);
        if (telefono != null) obj.setTelefono(telefono);
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteCliente(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
