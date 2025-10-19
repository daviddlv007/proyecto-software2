package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import com.supermercado.model.Producto;
import com.supermercado.repository.ProductoRepository;
import com.supermercado.repository.CategoriaRepository;

@Controller
public class ProductoResolver {
    private final ProductoRepository repository;
    private final CategoriaRepository categoriaRepository;

    public ProductoResolver(ProductoRepository repository, CategoriaRepository categoriaRepository) {
        this.repository = repository;
        this.categoriaRepository = categoriaRepository;
    }

    @QueryMapping
    public List<Producto> allProductos() {
        return repository.findAll();
    }

    @MutationMapping
    public Producto createProducto(@Argument String nombre, @Argument String descripcion, @Argument String imagenUrl, @Argument Double precio, @Argument Integer stock, @Argument Long categoriaId) {
        Producto obj = new Producto();
        obj.setNombre(nombre);
        obj.setDescripcion(descripcion);
        obj.setImagenUrl(imagenUrl);
        obj.setPrecio(precio);
        obj.setStock(stock);
        obj.setCategoria(categoriaRepository.findById(categoriaId).orElseThrow());
        return repository.save(obj);
    }

    @MutationMapping
    public Producto updateProducto(@Argument Long id, @Argument String nombre, @Argument String descripcion, @Argument String imagenUrl, @Argument Double precio, @Argument Integer stock, @Argument Long categoriaId) {
        Producto obj = repository.findById(id).orElseThrow();
        if (nombre != null) obj.setNombre(nombre);
        if (descripcion != null) obj.setDescripcion(descripcion);
        if (imagenUrl != null) obj.setImagenUrl(imagenUrl);
        if (precio != null) obj.setPrecio(precio);
        if (stock != null) obj.setStock(stock);
        if (categoriaId != null) obj.setCategoria(categoriaRepository.findById(categoriaId).orElseThrow());
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteProducto(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
