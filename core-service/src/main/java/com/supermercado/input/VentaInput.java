package com.supermercado.input;

import lombok.Data;
import java.util.List;

@Data
public class VentaInput {
    private String clienteId;
    private String fecha;
    private List<DetalleVentaInput> detalles;
    
    public Long getClienteIdAsLong() {
        return clienteId != null ? Long.parseLong(clienteId) : null;
    }
    
    public java.time.LocalDateTime getFechaAsLocalDateTime() {
        if (fecha == null || fecha.isEmpty()) {
            return java.time.LocalDateTime.now();
        }
        return java.time.LocalDate.parse(fecha).atStartOfDay();
    }
}