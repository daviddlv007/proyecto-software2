package com.supermercado.resolver;
import org.springframework.stereotype.Controller;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.Argument;
import java.util.List;
import com.supermercado.model.Categoria;
import com.supermercado.repository.CategoriaRepository;

@Controller
public class CategoriaResolver {
    private final CategoriaRepository repository;

    public CategoriaResolver(CategoriaRepository repository) {
        this.repository = repository;
    }

    @QueryMapping
    public List<Categoria> allCategorias() {
        return repository.findAll();
    }

    @MutationMapping
    public Categoria createCategoria(@Argument String nombre, @Argument String descripcion) {
        Categoria obj = new Categoria();
        obj.setNombre(nombre);
        obj.setDescripcion(descripcion);
        return repository.save(obj);
    }

    @MutationMapping
    public Categoria updateCategoria(@Argument Long id, @Argument String nombre, @Argument String descripcion) {
        Categoria obj = repository.findById(id).orElseThrow();
        if (nombre != null) obj.setNombre(nombre);
        if (descripcion != null) obj.setDescripcion(descripcion);
        return repository.save(obj);
    }

    @MutationMapping
    public Boolean deleteCategoria(@Argument Long id) {
        repository.deleteById(id);
        return true;
    }
}
