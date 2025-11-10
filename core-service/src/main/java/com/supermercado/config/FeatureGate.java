package com.supermercado.config;

import org.springframework.stereotype.Component;

@Component
public class FeatureGate {
  private final FeatureFlags flags;
  public FeatureGate(FeatureFlags flags) { this.flags = flags; }

  public void requireDelivery() { if (!flags.isDelivery()) throw new IllegalStateException("Delivery deshabilitado"); }
  public void requirePayments() { if (!flags.isPayments()) throw new IllegalStateException("Payments deshabilitado"); }
  public void requireVoiceAi()  { if (!flags.isVoiceAi())  throw new IllegalStateException("Voice/IA deshabilitado"); }
}
