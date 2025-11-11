package com.supermercado.input;

import lombok.Data;
import java.util.List;
import java.time.LocalDateTime;

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
        try {
            System.out.println("DEBUG: Parseando fecha: '" + fecha + "'");
            // Si contiene 'T', es formato DateTime completo
            if (fecha.contains("T")) {
                // Manejar formato ISO con milisegundos y zona horaria: "2025-11-11T15:30:00.000Z"
                if (fecha.endsWith("Z")) {
                    // Remover la Z y los milisegundos si existen
                    String fechaSinZ = fecha.substring(0, fecha.length() - 1);
                    System.out.println("DEBUG: Fecha sin Z: '" + fechaSinZ + "'");
                    if (fechaSinZ.contains(".")) {
                        fechaSinZ = fechaSinZ.substring(0, fechaSinZ.indexOf("."));
                        System.out.println("DEBUG: Fecha sin milisegundos: '" + fechaSinZ + "'");
                    }
                    LocalDateTime result = java.time.LocalDateTime.parse(fechaSinZ);
                    System.out.println("DEBUG: Fecha parseada exitosamente: " + result);
                    return result;
                } else if (fecha.contains(".")) {
                    // Formato con milisegundos pero sin Z: "2025-11-11T15:30:00.000"
                    String fechaSinMillis = fecha.substring(0, fecha.indexOf("."));
                    System.out.println("DEBUG: Fecha sin milisegundos (sin Z): '" + fechaSinMillis + "'");
                    LocalDateTime result = java.time.LocalDateTime.parse(fechaSinMillis);
                    System.out.println("DEBUG: Fecha parseada exitosamente: " + result);
                    return result;
                } else {
                    // Formato simple: "2025-11-11T15:30:00"
                    System.out.println("DEBUG: Formato simple DateTime: '" + fecha + "'");
                    LocalDateTime result = java.time.LocalDateTime.parse(fecha);
                    System.out.println("DEBUG: Fecha parseada exitosamente: " + result);
                    return result;
                }
            }
            // Si no, es solo fecha, convertir a LocalDateTime al inicio del día
            System.out.println("DEBUG: Solo fecha, convirtiendo a inicio del día: '" + fecha + "'");
            LocalDateTime result = java.time.LocalDate.parse(fecha).atStartOfDay();
            System.out.println("DEBUG: Fecha parseada exitosamente: " + result);
            return result;
        } catch (Exception e) {
            System.out.println("ERROR parseando fecha: '" + fecha + "' - " + e.getMessage());
            e.printStackTrace();
            return java.time.LocalDateTime.now();
        }
    }
}