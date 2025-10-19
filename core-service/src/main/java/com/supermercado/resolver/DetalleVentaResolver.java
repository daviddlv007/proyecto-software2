package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import com.supermercado.model.DetalleVenta;
import com.supermercado.repository.DetalleVentaRepository;
import com.supermercado.repository.VentaRepository;
import com.supermercado.repository.ProductoRepository;

@Controller
public class DetalleVentaResolver {
    private final DetalleVentaRepository repository;
    private final VentaRepository ventaRepository;
    private final ProductoRepository productoRepository;

    public DetalleVentaResolver(DetalleVentaRepository repository, VentaRepository ventaRepository, ProductoRepository productoRepository) {
        this.repository = repository;
        this.ventaRepository = ventaRepository;
        this.productoRepository = productoRepository;
    }

    @QueryMapping
    public List<DetalleVenta> allDetalleVentas() {
        return repository.findAll();
    }

    @MutationMapping
    public DetalleVenta createDetalleVenta(@Argument Long ventaId, @Argument Long productoId, @Argument Integer cantidad, @Argument Double precioUnitario) {
        DetalleVenta obj = new DetalleVenta();
        obj.setVenta(ventaRepository.findById(ventaId).orElseThrow());
        obj.setProducto(productoRepository.findById(productoId).orElseThrow());
        obj.setCantidad(cantidad);
        obj.setPrecioUnitario(precioUnitario);
        return repository.save(obj);
    }

    @MutationMapping
    public DetalleVenta updateDetalleVenta(@Argument Long id, @Argument Long ventaId, @Argument Long productoId, @Argument Integer cantidad, @Argument Double precioUnitario) {
        DetalleVenta obj = repository.findById(id).orElseThrow();
        if (ventaId != null) obj.setVenta(ventaRepository.findById(ventaId).orElseThrow());
        if (productoId != null) obj.setProducto(productoRepository.findById(productoId).orElseThrow());
        if (cantidad != null) obj.setCantidad(cantidad);
        if (precioUnitario != null) obj.setPrecioUnitario(precioUnitario);
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteDetalleVenta(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
