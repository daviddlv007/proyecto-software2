package com.supermercado.controller;

import com.stripe.Stripe;
import com.stripe.exception.StripeException;
import com.stripe.model.checkout.Session;
import com.stripe.param.checkout.SessionCreateParams;
import com.supermercado.model.Venta;
import com.supermercado.repository.VentaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.ui.Model;
import org.springframework.http.ResponseEntity;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Controller
@RequestMapping("/api/payments")
public class StripePaymentController {

    private static final Logger logger = LoggerFactory.getLogger(StripePaymentController.class);

    @Autowired
    private VentaRepository ventaRepository;

    @Value("${stripe.secret.key}")
    private String stripeSecretKey;

    @Value("${app.success.url}")
    private String successUrl;

    @Value("${app.cancel.url}")
    private String cancelUrl;

    @Value("${currency:USD}")
    private String currency;

    /**
     * Crea una sesión de checkout de Stripe
     */
    @PostMapping("/create-checkout-session")
    @ResponseBody
    public ResponseEntity<Map<String, String>> createCheckoutSession(@RequestParam Long ventaId) {
        try {
            // Configurar Stripe
            Stripe.apiKey = stripeSecretKey;

            // Buscar la venta
            Optional<Venta> ventaOpt = ventaRepository.findById(ventaId);
            if (ventaOpt.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "Venta no encontrada"));
            }

            Venta venta = ventaOpt.get();
            
            // Convertir total a centavos (Stripe usa centavos)
            long amountInCents = BigDecimal.valueOf(venta.getTotal()).multiply(new BigDecimal("100")).longValue();

            // Crear sesión de checkout
            SessionCreateParams params = SessionCreateParams.builder()
                .setMode(SessionCreateParams.Mode.PAYMENT)
                .setSuccessUrl(successUrl + "?session_id={CHECKOUT_SESSION_ID}&venta_id=" + ventaId)
                .setCancelUrl(cancelUrl + "?venta_id=" + ventaId)
                .addLineItem(
                    SessionCreateParams.LineItem.builder()
                        .setPriceData(
                            SessionCreateParams.LineItem.PriceData.builder()
                                .setCurrency(currency)
                                .setProductData(
                                    SessionCreateParams.LineItem.PriceData.ProductData.builder()
                                        .setName("Compra Supermercado - Orden #" + ventaId)
                                        .setDescription("Total de productos: " + venta.getDetalles().size())
                                        .build()
                                )
                                .setUnitAmount(amountInCents)
                                .build()
                        )
                        .setQuantity(1L)
                        .build()
                )
                .putMetadata("venta_id", ventaId.toString())
                .build();

            Session session = Session.create(params);

            logger.info("✅ Sesión de Stripe creada exitosamente: {} para venta: {}", session.getId(), ventaId);

            // Retornar URL de checkout
            Map<String, String> response = new HashMap<>();
            response.put("checkout_url", session.getUrl());
            response.put("session_id", session.getId());
            
            return ResponseEntity.ok(response);

        } catch (StripeException e) {
            logger.error("❌ Error creando sesión de Stripe para venta {}: {}", ventaId, e.getMessage());
            return ResponseEntity.badRequest().body(Map.of("error", "Error procesando pago: " + e.getMessage()));
        } catch (Exception e) {
            logger.error("❌ Error inesperado para venta {}: {}", ventaId, e.getMessage());
            return ResponseEntity.badRequest().body(Map.of("error", "Error interno del servidor"));
        }
    }

    /**
     * Página de pago exitoso
     */
    @GetMapping("/success")
    public String paymentSuccess(@RequestParam String session_id, 
                                @RequestParam Long venta_id, 
                                Model model) {
        try {
            Stripe.apiKey = stripeSecretKey;
            
            // Verificar sesión
            Session session = Session.retrieve(session_id);
            
            // Buscar venta
            Optional<Venta> ventaOpt = ventaRepository.findById(venta_id);
            if (ventaOpt.isPresent()) {
                Venta venta = ventaOpt.get();
                
                // Actualizar estado de pago si es necesario
                // venta.setEstadoPago("PAGADO");
                // ventaRepository.save(venta);
                
                model.addAttribute("venta", venta);
                model.addAttribute("session", session);
                model.addAttribute("success", true);
                
                logger.info("✅ Pago exitoso para venta {} con sesión {}", venta_id, session_id);
            }

        } catch (Exception e) {
            logger.error("❌ Error verificando pago exitoso: {}", e.getMessage());
            model.addAttribute("error", "Error verificando el pago");
        }

        return "payment-result";
    }

    /**
     * Página de pago cancelado
     */
    @GetMapping("/cancel")
    public String paymentCancel(@RequestParam Long venta_id, Model model) {
        try {
            Optional<Venta> ventaOpt = ventaRepository.findById(venta_id);
            if (ventaOpt.isPresent()) {
                Venta venta = ventaOpt.get();
                model.addAttribute("venta", venta);
                model.addAttribute("success", false);
                
                logger.info("⚠️ Pago cancelado para venta {}", venta_id);
            }
        } catch (Exception e) {
            logger.error("❌ Error manejando cancelación: {}", e.getMessage());
        }

        return "payment-result";
    }

    /**
     * Webhook para recibir eventos de Stripe
     */
    @PostMapping("/webhook")
    @ResponseBody
    public ResponseEntity<String> handleStripeWebhook(@RequestBody String payload, 
                                                     @RequestHeader("Stripe-Signature") String sigHeader) {
        try {
            // Aquí implementarías la verificación del webhook
            logger.info("📩 Webhook de Stripe recibido");
            
            // Procesar evento de pago completado
            // Event event = Webhook.constructEvent(payload, sigHeader, webhookSecret);
            
            return ResponseEntity.ok("OK");
            
        } catch (Exception e) {
            logger.error("❌ Error procesando webhook: {}", e.getMessage());
            return ResponseEntity.badRequest().body("Error");
        }
    }
}