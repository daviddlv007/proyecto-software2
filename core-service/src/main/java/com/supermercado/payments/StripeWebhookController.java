package com.supermercado.payments;

import com.stripe.exception.SignatureVerificationException;
import com.stripe.model.Event;
import com.stripe.model.checkout.Session;
import com.stripe.net.Webhook;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.supermercado.model.Venta;
import com.supermercado.repository.VentaRepository;


@RestController
@RequestMapping("/webhooks/stripe")
public class StripeWebhookController {

  @Value("${STRIPE_WEBHOOK_SECRET:}") private String webhookSecret;
  private final VentaRepository ventaRepo;

  public StripeWebhookController(VentaRepository ventaRepo) { this.ventaRepo = ventaRepo; }

  @PostMapping
  public ResponseEntity<String> handle(@RequestHeader("Stripe-Signature") String sig,
                                       @RequestBody String payload) {
    if (webhookSecret == null || webhookSecret.isBlank()) {
      // ignoramos si no hay secreto configurado
      return ResponseEntity.ok("ignored");
    }
    try {
      Event event = Webhook.constructEvent(payload, sig, webhookSecret);

      if ("checkout.session.completed".equals(event.getType())) {
        Session session = (Session) event.getDataObjectDeserializer()
          .getObject().orElse(null);
        if (session != null) {
          String ventaIdStr = session.getMetadata().get("ventaId");
          if (ventaIdStr != null) {
            Long ventaId = Long.valueOf(ventaIdStr);
            Venta v = ventaRepo.findById(ventaId).orElse(null);
            if (v != null) {
              v.setPaymentStatus("PAID");
              v.setCheckoutSessionId(session.getId());
              v.setPaymentIntentId(session.getPaymentIntent());
              ventaRepo.save(v);
            }
          }
        }
      }
      return ResponseEntity.ok("ok");
    } catch (SignatureVerificationException e) {
      return ResponseEntity.badRequest().body("invalid signature");
    } catch (Exception e) {
      return ResponseEntity.badRequest().body("error");
    }
  }
}
