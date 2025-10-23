package com.supermercado.resolver.base;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.function.Function;

/**
 * Resolver base genérico que elimina código repetitivo
 * Implementa operaciones CRUD comunes para todas las entidades
 */
public abstract class BaseResolver<T, ID, CreateInput, UpdateInput> {
    
    protected final JpaRepository<T, ID> repository;
    
    protected BaseResolver(JpaRepository<T, ID> repository) {
        this.repository = repository;
    }
    
    // Operaciones CRUD genéricas
    public List<T> findAll() {
        return repository.findAll();
    }
    
    public T create(CreateInput input) {
        T entity = mapToEntity(input);
        return repository.save(entity);
    }
    
    public T update(ID id, UpdateInput input) {
        T entity = repository.findById(id)
            .orElseThrow(() -> new RuntimeException("Entity not found with id: " + id));
        updateEntity(entity, input);
        return repository.save(entity);
    }
    
    public Boolean delete(ID id) {
        repository.deleteById(id);
        return true;
    }
    
    // Métodos abstractos que cada resolver debe implementar
    protected abstract T mapToEntity(CreateInput input);
    protected abstract void updateEntity(T entity, UpdateInput input);
}