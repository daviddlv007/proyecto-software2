package com.supermercado.payments;

import com.stripe.Stripe;
import com.stripe.model.checkout.Session;
import com.stripe.param.checkout.SessionCreateParams;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import com.supermercado.repository.VentaRepository;
import com.supermercado.model.Venta;

@Service
public class PaymentService {

  @Value("${STRIPE_SECRET_KEY:}") private String stripeKey;
  @Value("${APP_SUCCESS_URL:http://localhost:5173/pago-exitoso}") private String successUrl;
  @Value("${APP_CANCEL_URL:http://localhost:5173/pago-cancelado}")  private String cancelUrl;
  @Value("${CURRENCY:USD}") private String currency;

  private final QRCodeService qrCodeService;
  private final VentaRepository ventaRepository;

  public PaymentService(QRCodeService qrCodeService, VentaRepository ventaRepository) {
    this.qrCodeService = qrCodeService;
    this.ventaRepository = ventaRepository;
  }

  @PostConstruct
  public void init() {
    if (stripeKey != null && !stripeKey.isBlank()) {
      Stripe.apiKey = stripeKey;
    }
  }

  public String createCheckoutUrl(Long ventaId, long amountCents) throws Exception {
    if (stripeKey == null || stripeKey.isBlank()) {
      throw new IllegalStateException("Payments disabled (STRIPE_SECRET_KEY vacío).");
    }

    SessionCreateParams.LineItem.PriceData.ProductData product =
      SessionCreateParams.LineItem.PriceData.ProductData.builder()
        .setName("Venta #" + ventaId)
        .build();

    SessionCreateParams.LineItem.PriceData price =
      SessionCreateParams.LineItem.PriceData.builder()
        .setCurrency(currency.toLowerCase())
        .setUnitAmount(amountCents)
        .setProductData(product)
        .build();

    SessionCreateParams.LineItem lineItem =
      SessionCreateParams.LineItem.builder()
        .setQuantity(1L)
        .setPriceData(price)
        .build();

    SessionCreateParams params =
      SessionCreateParams.builder()
        .setMode(SessionCreateParams.Mode.PAYMENT)
        .addLineItem(lineItem)
        .setSuccessUrl(successUrl)
        .setCancelUrl(cancelUrl)
        .putMetadata("ventaId", String.valueOf(ventaId))
        .build();

    Session session = Session.create(params);
    return session.getUrl();
  }

  // NUEVO: Método para crear pago con QR
  public QRPaymentInfo createQRPayment(Long ventaId, Double amount) {
    Venta venta = ventaRepository.findById(ventaId)
        .orElseThrow(() -> new IllegalArgumentException("Venta no encontrada: " + ventaId));

    String paymentData = qrCodeService.generatePaymentData(ventaId, amount, currency);
    String qrImageBase64 = qrCodeService.generateQRCodeBase64(paymentData, 300, 300);
    
    venta.setQrCheckoutUrl(qrImageBase64);
    venta.setPaymentStatus("PENDING");
    venta.setPaymentProvider("QR");
    ventaRepository.save(venta);
    
    return new QRPaymentInfo(qrImageBase64, paymentData, ventaId);
  }

  public record QRPaymentInfo(String qrImageBase64, String qrData, Long ventaId) {}
}