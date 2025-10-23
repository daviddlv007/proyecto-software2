package com.supermercado.resolver;

import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;

import com.supermercado.model.Categoria;
import com.supermercado.repository.CategoriaRepository;
import com.supermercado.input.CategoriaInput;

import java.util.List;

@Controller
public class CategoriaResolver {
    
    private final CategoriaRepository repository;
    
    public CategoriaResolver(CategoriaRepository repository) {
        this.repository = repository;
    }
    
    @QueryMapping
    public List<Categoria> categorias() {
        return repository.findAll();
    }
    
    @MutationMapping
    public Categoria createCategoria(@Argument CategoriaInput input) {
        Categoria categoria = new Categoria();
        categoria.setNombre(input.getNombre());
        categoria.setDescripcion(input.getDescripcion());
        return repository.save(categoria);
    }
    
    @MutationMapping
    public Categoria updateCategoria(@Argument Long id, @Argument CategoriaInput input) {
        Categoria categoria = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Categoría no encontrada"));
        categoria.setNombre(input.getNombre());
        categoria.setDescripcion(input.getDescripcion());
        return repository.save(categoria);
    }
    
    @MutationMapping
    public Boolean deleteCategoria(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
