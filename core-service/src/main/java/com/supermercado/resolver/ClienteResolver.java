package com.supermercado.resolver;

import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;

import com.supermercado.model.Cliente;
import com.supermercado.repository.ClienteRepository;
import com.supermercado.input.ClienteInput;

import java.util.List;

@Controller
public class ClienteResolver {
    
    private final ClienteRepository repository;
    
    public ClienteResolver(ClienteRepository repository) {
        this.repository = repository;
    }
    
    @QueryMapping
    public List<Cliente> clientes() {
        return repository.findAll();
    }
    
    @MutationMapping
    public Cliente createCliente(@Argument ClienteInput input) {
        Cliente cliente = new Cliente();
        cliente.setNombre(input.getNombre());
        cliente.setCorreo(input.getCorreo());
        cliente.setTelefono(input.getTelefono());
        return repository.save(cliente);
    }

    @MutationMapping
    public Cliente updateCliente(@Argument Long id, @Argument ClienteInput input) {
        Cliente cliente = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Cliente no encontrado"));
        cliente.setNombre(input.getNombre());
        cliente.setCorreo(input.getCorreo());
        cliente.setTelefono(input.getTelefono());
        return repository.save(cliente);
    }

    @MutationMapping
    public Boolean deleteCliente(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
