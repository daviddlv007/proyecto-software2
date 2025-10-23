package com.supermercado.resolver;

import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;

import com.supermercado.model.Producto;
import com.supermercado.repository.ProductoRepository;
import com.supermercado.repository.CategoriaRepository;
import com.supermercado.input.ProductoInput;

import java.util.List;

@Controller
public class ProductoResolver {
    
    private final ProductoRepository repository;
    private final CategoriaRepository categoriaRepository;
    
    public ProductoResolver(ProductoRepository repository, CategoriaRepository categoriaRepository) {
        this.repository = repository;
        this.categoriaRepository = categoriaRepository;
    }
    
    @QueryMapping
    public List<Producto> productos() {
        return repository.findAll();
    }
    
    @MutationMapping
    public Producto createProducto(@Argument ProductoInput input) {
        Producto producto = new Producto();
        producto.setNombre(input.getNombre());
        producto.setDescripcion(input.getDescripcion());
        producto.setImagenUrl(input.getImagenUrl());
        producto.setPrecio(input.getPrecio());
        producto.setStock(input.getStock());
        producto.setCategoria(categoriaRepository.findById(input.getCategoriaIdAsLong())
            .orElseThrow(() -> new RuntimeException("Categoría no encontrada")));
        return repository.save(producto);
    }

    @MutationMapping
    public Producto updateProducto(@Argument Long id, @Argument ProductoInput input) {
        Producto producto = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Producto no encontrado"));
        producto.setNombre(input.getNombre());
        producto.setDescripcion(input.getDescripcion());
        producto.setImagenUrl(input.getImagenUrl());
        producto.setPrecio(input.getPrecio());
        producto.setStock(input.getStock());
        if (input.getCategoriaId() != null) {
            producto.setCategoria(categoriaRepository.findById(input.getCategoriaIdAsLong())
                .orElseThrow(() -> new RuntimeException("Categoría no encontrada")));
        }
        return repository.save(producto);
    }

    @MutationMapping
    public Boolean deleteProducto(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
