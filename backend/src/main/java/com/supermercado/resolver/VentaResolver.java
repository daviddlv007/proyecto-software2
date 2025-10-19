package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import java.time.LocalDateTime;
import com.supermercado.model.Venta;
import com.supermercado.repository.VentaRepository;
import com.supermercado.repository.ClienteRepository;

@Controller
public class VentaResolver {
    private final VentaRepository repository;
    private final ClienteRepository clienteRepository;

    public VentaResolver(VentaRepository repository, ClienteRepository clienteRepository) {
        this.repository = repository;
        this.clienteRepository = clienteRepository;
    }

    @QueryMapping
    public List<Venta> allVentas() {
        return repository.findAll();
    }

    @MutationMapping
    public Venta createVenta(@Argument Long clienteId, @Argument LocalDateTime fecha, @Argument Double total) {
        Venta obj = new Venta();
        obj.setCliente(clienteRepository.findById(clienteId).orElseThrow());
        obj.setFecha(fecha);
        obj.setTotal(total);
        return repository.save(obj);
    }

    @MutationMapping
    public Venta updateVenta(@Argument Long id, @Argument Long clienteId, @Argument LocalDateTime fecha, @Argument Double total) {
        Venta obj = repository.findById(id).orElseThrow();
        if (clienteId != null) obj.setCliente(clienteRepository.findById(clienteId).orElseThrow());
        if (fecha != null) obj.setFecha(fecha);
        if (total != null) obj.setTotal(total);
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteVenta(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
