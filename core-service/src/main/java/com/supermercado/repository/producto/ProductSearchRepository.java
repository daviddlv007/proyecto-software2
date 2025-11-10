package com.supermercado.repository.producto;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import java.util.*;

@Repository
public class ProductSearchRepository {
  private final JdbcTemplate jdbc;
  public ProductSearchRepository(JdbcTemplate jdbc) { this.jdbc = jdbc; }

  public List<Map<String, Object>> findByNamesApprox(List<String> names) {
    if (names == null || names.isEmpty()) return List.of();
    String sql = """
      SELECT id, nombre, stock, precio
      FROM productos
      WHERE LOWER(nombre) LIKE LOWER(?) LIMIT 50
      """;
    List<Map<String,Object>> all = new ArrayList<>();
    for (String n : names) {
      // búsqueda simple por LIKE; podemos mejorar con pg_trgm luego
      all.addAll(jdbc.queryForList(sql, "%" + n + "%"));
    }
    return all;
  }
}
