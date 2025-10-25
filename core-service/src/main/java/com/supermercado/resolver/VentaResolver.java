package com.supermercado.resolver;

import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.transaction.annotation.Transactional;

import com.supermercado.model.Venta;
import com.supermercado.model.DetalleVenta;
import com.supermercado.repository.VentaRepository;
import com.supermercado.repository.ClienteRepository;
import com.supermercado.repository.ProductoRepository;
import com.supermercado.input.VentaInput;
import com.supermercado.input.DetalleVentaInput;

import java.util.List;
import java.util.ArrayList;

@Controller
@Transactional
public class VentaResolver {
    
    private final VentaRepository ventaRepository;
    private final ClienteRepository clienteRepository;
    private final ProductoRepository productoRepository;
    
    public VentaResolver(VentaRepository ventaRepository, 
                        ClienteRepository clienteRepository,
                        ProductoRepository productoRepository) {
        this.ventaRepository = ventaRepository;
        this.clienteRepository = clienteRepository;
        this.productoRepository = productoRepository;
    }
    
    @QueryMapping
    @Transactional(readOnly = true)
    public List<Venta> ventas() {
        List<Venta> ventas = ventaRepository.findAll();
        
        // Inicializar relaciones lazy manualmente para evitar LazyInitializationException
        // Esto es seguro y no afecta la API GraphQL
        ventas.forEach(venta -> {
            if (venta.getCliente() != null) {
                venta.getCliente().getNombre(); // Forzar carga del cliente
            }
            venta.getDetalles().forEach(detalle -> {
                if (detalle.getProducto() != null) {
                    detalle.getProducto().getNombre(); // Forzar carga del producto
                    if (detalle.getProducto().getCategoria() != null) {
                        detalle.getProducto().getCategoria().getNombre(); // Forzar carga de categoría
                    }
                }
            });
        });
        
        return ventas;
    }
    
    @MutationMapping
    public Venta createVenta(@Argument VentaInput input) {
        // Crear venta
        Venta venta = new Venta();
        venta.setCliente(clienteRepository.findById(input.getClienteIdAsLong())
            .orElseThrow(() -> new RuntimeException("Cliente no encontrado")));
        venta.setFecha(input.getFechaAsLocalDateTime());
        
        // Agregar detalles
        for (DetalleVentaInput detalleInput : input.getDetalles()) {
            DetalleVenta detalle = new DetalleVenta();
            detalle.setProducto(productoRepository.findById(detalleInput.getProductoIdAsLong())
                .orElseThrow(() -> new RuntimeException("Producto no encontrado")));
            detalle.setCantidad(detalleInput.getCantidad());
            detalle.setPrecioUnitario(detalleInput.getPrecioUnitario());
            
            venta.addDetalle(detalle);
        }
        
        // Calcular total automáticamente
        venta.calcularTotal();
        
        return ventaRepository.save(venta);
    }
    
    @MutationMapping
    public Venta updateVenta(@Argument Long id, @Argument VentaInput input) {
        Venta venta = ventaRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Venta no encontrada"));
        
        // Actualizar datos básicos
        venta.setCliente(clienteRepository.findById(input.getClienteIdAsLong())
            .orElseThrow(() -> new RuntimeException("Cliente no encontrado")));
        venta.setFecha(input.getFechaAsLocalDateTime());
        
        // Limpiar detalles existentes de manera segura
        // Usar removeAll en lugar de clear para evitar problemas con JPA
        List<DetalleVenta> detallesActuales = new ArrayList<>(venta.getDetalles());
        detallesActuales.forEach(detalle -> {
            detalle.setVenta(null);
        });
        venta.getDetalles().clear();
        
        // Agregar nuevos detalles
        for (DetalleVentaInput detalleInput : input.getDetalles()) {
            DetalleVenta detalle = new DetalleVenta();
            detalle.setProducto(productoRepository.findById(detalleInput.getProductoIdAsLong())
                .orElseThrow(() -> new RuntimeException("Producto no encontrado")));
            detalle.setCantidad(detalleInput.getCantidad());
            detalle.setPrecioUnitario(detalleInput.getPrecioUnitario());
            
            venta.addDetalle(detalle);
        }
        
        // Recalcular total
        venta.calcularTotal();
        
        return ventaRepository.save(venta);
    }
    
    @MutationMapping
    public Boolean deleteVenta(@Argument Long id) {
        ventaRepository.deleteById(id);
        return true;
    }
}
