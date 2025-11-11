package com.supermercado.graphql;

import com.supermercado.payments.PaymentService;
import com.supermercado.controller.StripePaymentController;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.stereotype.Controller;
import org.springframework.http.ResponseEntity;

import java.util.Map;

@Controller
public class PaymentResolver {

  private final StripePaymentController stripeController;

  public PaymentResolver(StripePaymentController stripeController) {
    this.stripeController = stripeController;
  }

  @MutationMapping
  public Map<String,String> startPayment(@Argument Long ventaId) {
    // Usar el nuevo controller de Stripe
    ResponseEntity<Map<String, String>> response = stripeController.createCheckoutSession(ventaId);
    if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
      return response.getBody();
    } else {
      Map<String, String> errorBody = response.getBody();
      String errorMessage = (errorBody != null) ? errorBody.get("error") : "Error desconocido";
      throw new RuntimeException("Error creando sesión de pago: " + errorMessage);
    }
  }

  @MutationMapping
  public PaymentService.QRPaymentInfo createQRPayment(@Argument Long ventaId) {
    // Usar el nuevo sistema: generar QR que apunte a la URL real de Stripe
    ResponseEntity<Map<String, String>> response = stripeController.createCheckoutSession(ventaId);
    
    if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
      String checkoutUrl = response.getBody().get("checkout_url");
      
      if (checkoutUrl == null) {
        throw new RuntimeException("URL de checkout no encontrada en la respuesta");
      }
      
      // Crear QR que apunte a la URL real de Stripe
      return new PaymentService.QRPaymentInfo(
        "", // qrImageBase64 - se genera dinámicamente en el frontend
        checkoutUrl, // La URL real de Stripe como datos del QR
        ventaId
      );
    } else {
      Map<String, String> errorBody = response.getBody();
      String errorMessage = (errorBody != null) ? errorBody.get("error") : "Error desconocido";
      throw new RuntimeException("Error generando QR de pago: " + errorMessage);
    }
  }
}