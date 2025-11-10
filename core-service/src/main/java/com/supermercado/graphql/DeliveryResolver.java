package com.supermercado.graphql;

import com.supermercado.delivery.DeliveryService;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Controller
public class DeliveryResolver {

    private final DeliveryService deliveryService;

    public DeliveryResolver(DeliveryService deliveryService) {
        this.deliveryService = deliveryService;
    }

    @QueryMapping
    public DeliveryService.DeliveryQuote getDeliveryQuote(
        @Argument Double latitude,
        @Argument Double longitude
    ) {
        return deliveryService.calculateQuote(latitude, longitude);
    }

    @MutationMapping
    public DeliveryService.DeliveryInfo requestDelivery(@Argument Map<String, Object> input) {
        Long ventaId = Long.valueOf(input.get("ventaId").toString());
        String address = (String) input.get("address");
        Double latitude = Double.valueOf(input.get("latitude").toString());
        Double longitude = Double.valueOf(input.get("longitude").toString());
        
        return deliveryService.requestDelivery(ventaId, address, latitude, longitude);
    }

    @MutationMapping
    public DeliveryService.DeliveryInfo updateDeliveryStatus(
        @Argument Long ventaId,
        @Argument String status,
        @Argument String riderId  // Quitado required = false
    ) {
        return deliveryService.updateStatus(ventaId, status, riderId);
    }
}