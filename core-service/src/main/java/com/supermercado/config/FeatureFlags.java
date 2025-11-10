package com.supermercado.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "feature")
public class FeatureFlags {
  private boolean delivery = false;
  private boolean payments = false;
  private boolean voiceAi = false;

  public boolean isDelivery() { return delivery; }
  public void setDelivery(boolean delivery) { this.delivery = delivery; }
  public boolean isPayments() { return payments; }
  public void setPayments(boolean payments) { this.payments = payments; }
  public boolean isVoiceAi() { return voiceAi; }
  public void setVoiceAi(boolean voiceAi) { this.voiceAi = voiceAi; }
}
