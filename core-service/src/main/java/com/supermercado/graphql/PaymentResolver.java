package com.supermercado.graphql;

import com.supermercado.payments.PaymentService;
import com.supermercado.repository.VentaRepository;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.stereotype.Controller;

import java.math.BigDecimal;
import java.util.Map;

@Controller
public class PaymentResolver {

  private final PaymentService paymentService;
  private final VentaRepository ventaRepo;

  public PaymentResolver(PaymentService paymentService, VentaRepository ventaRepo) {
    this.paymentService = paymentService;
    this.ventaRepo = ventaRepo;
  }

  @MutationMapping
  public Map<String,String> startPayment(@Argument Long ventaId) throws Exception {
    var venta = ventaRepo.findById(ventaId).orElseThrow();
    Double total = venta.getTotal();
    long cents = BigDecimal.valueOf(total).multiply(BigDecimal.valueOf(100)).longValue();
    String url = paymentService.createCheckoutUrl(ventaId, cents);
    return Map.of("url", url);
  }

  @MutationMapping
  public PaymentService.QRPaymentInfo createQRPayment(@Argument Long ventaId) {
    var venta = ventaRepo.findById(ventaId).orElseThrow();
    Double total = venta.getTotal();
    return paymentService.createQRPayment(ventaId, total);
  }
}