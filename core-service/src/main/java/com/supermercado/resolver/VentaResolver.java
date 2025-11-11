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
        System.out.println("DEBUG: createVenta iniciado con input: " + input);
        try {
            // Crear venta
            Venta venta = new Venta();
            System.out.println("DEBUG: Venta creada: " + venta);
            
            venta.setCliente(clienteRepository.findById(input.getClienteIdAsLong())
                .orElseThrow(() -> new RuntimeException("Cliente no encontrado")));
            System.out.println("DEBUG: Cliente asignado: " + venta.getCliente());
            
            venta.setFecha(input.getFechaAsLocalDateTime());
            System.out.println("DEBUG: Fecha asignada: " + venta.getFecha());
            
            // Agregar detalles y descontar stock
            for (DetalleVentaInput detalleInput : input.getDetalles()) {
                System.out.println("DEBUG: Procesando detalle: " + detalleInput);
                
                var producto = productoRepository.findById(detalleInput.getProductoIdAsLong())
                    .orElseThrow(() -> new RuntimeException("Producto no encontrado"));
                System.out.println("DEBUG: Producto encontrado: " + producto);
                
                // VALIDACIÓN: Verificar stock disponible
                if (producto.getStock() == null) {
                    throw new RuntimeException("Producto '" + producto.getNombre() + "' no tiene stock configurado");
                }
                
                if (producto.getStock() < detalleInput.getCantidad()) {
                    throw new RuntimeException("Stock insuficiente para producto '" + producto.getNombre() + 
                        "'. Disponible: " + producto.getStock() + ", Solicitado: " + detalleInput.getCantidad());
                }
                
                // REGLA DE NEGOCIO: Descontar stock
                producto.setStock(producto.getStock() - detalleInput.getCantidad());
                productoRepository.save(producto);
                System.out.println("DEBUG: Stock actualizado para producto " + producto.getNombre() + ": " + producto.getStock());
                
                // Crear detalle de venta
                DetalleVenta detalle = new DetalleVenta();
                detalle.setProducto(producto);
                detalle.setCantidad(detalleInput.getCantidad());
                detalle.setPrecioUnitario(detalleInput.getPrecioUnitario());
                detalle.calcularSubtotal(); // Calcular subtotal
                
                venta.addDetalle(detalle);
                System.out.println("DEBUG: Detalle agregado: " + detalle);
            }
            
            // Calcular total automáticamente
            venta.calcularTotal();
            System.out.println("DEBUG: Total calculado: " + venta.getTotal());
            
            Venta ventaGuardada = ventaRepository.save(venta);
            System.out.println("DEBUG: Venta guardada exitosamente: " + ventaGuardada);
            
            return ventaGuardada;
        } catch (Exception e) {
            System.err.println("ERROR en createVenta: " + e.getMessage());
            e.printStackTrace();
            throw e;
        }
    }
    
    @MutationMapping
    public Venta updateVenta(@Argument Long id, @Argument VentaInput input) {
        Venta venta = ventaRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Venta no encontrada"));
        
        // REGLA DE NEGOCIO: Devolver stock de los detalles anteriores
        List<DetalleVenta> detallesAnteriores = new ArrayList<>(venta.getDetalles());
        for (DetalleVenta detalleAnterior : detallesAnteriores) {
            var producto = detalleAnterior.getProducto();
            producto.setStock(producto.getStock() + detalleAnterior.getCantidad());
            productoRepository.save(producto);
        }
        
        // Actualizar datos básicos
        venta.setCliente(clienteRepository.findById(input.getClienteIdAsLong())
            .orElseThrow(() -> new RuntimeException("Cliente no encontrado")));
        venta.setFecha(input.getFechaAsLocalDateTime());
        
        // Limpiar detalles existentes de manera segura
        detallesAnteriores.forEach(detalle -> {
            detalle.setVenta(null);
        });
        venta.getDetalles().clear();
        
        // Agregar nuevos detalles y descontar stock
        for (DetalleVentaInput detalleInput : input.getDetalles()) {
            var producto = productoRepository.findById(detalleInput.getProductoIdAsLong())
                .orElseThrow(() -> new RuntimeException("Producto no encontrado"));
            
            // VALIDACIÓN: Verificar stock disponible
            if (producto.getStock() == null) {
                // Rollback: devolver stock de los productos ya procesados
                for (DetalleVenta detalleAnterior : detallesAnteriores) {
                    var prod = detalleAnterior.getProducto();
                    prod.setStock(prod.getStock() - detalleAnterior.getCantidad());
                    productoRepository.save(prod);
                }
                throw new RuntimeException("Producto '" + producto.getNombre() + "' no tiene stock configurado");
            }
            
            if (producto.getStock() < detalleInput.getCantidad()) {
                // Rollback: devolver stock de los productos ya procesados
                for (DetalleVenta detalleAnterior : detallesAnteriores) {
                    var prod = detalleAnterior.getProducto();
                    prod.setStock(prod.getStock() - detalleAnterior.getCantidad());
                    productoRepository.save(prod);
                }
                throw new RuntimeException("Stock insuficiente para producto '" + producto.getNombre() + 
                    "'. Disponible: " + producto.getStock() + ", Solicitado: " + detalleInput.getCantidad());
            }
            
            // REGLA DE NEGOCIO: Descontar stock
            producto.setStock(producto.getStock() - detalleInput.getCantidad());
            productoRepository.save(producto);
            
            // Crear nuevo detalle
            DetalleVenta detalle = new DetalleVenta();
            detalle.setProducto(producto);
            detalle.setCantidad(detalleInput.getCantidad());
            detalle.setPrecioUnitario(detalleInput.getPrecioUnitario());
            detalle.calcularSubtotal(); // Calcular subtotal
            
            venta.addDetalle(detalle);
        }
        
        // Recalcular total
        venta.calcularTotal();
        
        return ventaRepository.save(venta);
    }
    
    @MutationMapping
    public boolean deleteVenta(@Argument Long id) {
        Venta venta = ventaRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Venta no encontrada"));
        
        // REGLA DE NEGOCIO: Restaurar stock antes de eliminar la venta
        for (DetalleVenta detalle : venta.getDetalles()) {
            var producto = detalle.getProducto();
            if (producto.getStock() != null) {
                producto.setStock(producto.getStock() + detalle.getCantidad());
                productoRepository.save(producto);
            }
        }
        
        ventaRepository.delete(venta);
        return true;
    }
}
