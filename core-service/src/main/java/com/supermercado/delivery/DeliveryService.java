package com.supermercado.delivery;

import com.supermercado.config.DeliveryProperties;
import com.supermercado.config.FeatureGate;
import com.supermercado.model.Venta;
import com.supermercado.repository.VentaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DeliveryService {

    private final DeliveryProperties props;
    private final FeatureGate gate;
    private final VentaRepository ventaRepo;

    public DeliveryService(DeliveryProperties props, FeatureGate gate, VentaRepository ventaRepo) {
        this.props = props;
        this.gate = gate;
        this.ventaRepo = ventaRepo;
    }

    public DeliveryQuote calculateQuote(double clientLat, double clientLng) {
        gate.requireDelivery();
        
        double distance = calculateDistance(
            props.getOriginLat(), 
            props.getOriginLng(), 
            clientLat, 
            clientLng
        );
        
        double fee = props.getBaseFee() + (distance * props.getPerKm());
        int estimatedMinutes = (int) Math.ceil(distance * 3);
        
        return new DeliveryQuote(distance, fee, estimatedMinutes);
    }

    @Transactional
    public DeliveryInfo requestDelivery(Long ventaId, String address, 
                                         double latitude, double longitude) {
        gate.requireDelivery();
        
        Venta venta = ventaRepo.findById(ventaId)
            .orElseThrow(() -> new IllegalArgumentException("Venta no encontrada"));

        DeliveryQuote quote = calculateQuote(latitude, longitude);
        
        venta.setDeliveryAddress(address);
        venta.setDeliveryLat(latitude);
        venta.setDeliveryLng(longitude);
        venta.setDeliveryDistanceKm(quote.distance());
        venta.setDeliveryFee(quote.fee());
        venta.setDeliveryEtaMinutes(quote.estimatedMinutes());
        venta.setDeliveryStatus("PENDING");
        
        ventaRepo.save(venta);
        
        return new DeliveryInfo(
            "PENDING",
            address,
            quote.distance(),
            quote.fee(),
            quote.estimatedMinutes(),
            null
        );
    }

    @Transactional
    public DeliveryInfo updateStatus(Long ventaId, String status, String riderId) {
        gate.requireDelivery();
        
        Venta venta = ventaRepo.findById(ventaId)
            .orElseThrow(() -> new IllegalArgumentException("Venta no encontrada"));

        venta.setDeliveryStatus(status);
        if (riderId != null) {
            venta.setDeliveryRiderId(riderId);
        }
        
        ventaRepo.save(venta);
        
        return new DeliveryInfo(
            venta.getDeliveryStatus(),
            venta.getDeliveryAddress(),
            venta.getDeliveryDistanceKm(),
            venta.getDeliveryFee(),
            venta.getDeliveryEtaMinutes(),
            venta.getDeliveryRiderId()
        );
    }

    private double calculateDistance(double lat1, double lng1, double lat2, double lng2) {
        final int EARTH_RADIUS_KM = 6371;
        
        double dLat = Math.toRadians(lat2 - lat1);
        double dLng = Math.toRadians(lng2 - lng1);
        
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                   Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                   Math.sin(dLng / 2) * Math.sin(dLng / 2);
        
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return EARTH_RADIUS_KM * c;
    }

    public record DeliveryQuote(double distance, double fee, int estimatedMinutes) {}
    public record DeliveryInfo(String status, String address, Double distance, 
                               Double fee, Integer eta, String riderId) {}
}