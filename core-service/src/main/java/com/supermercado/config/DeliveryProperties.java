package com.supermercado.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "delivery")
public class DeliveryProperties {
    private double originLat = -17.7833;
    private double originLng = -63.1821;
    private double baseFee = 2.0;
    private double perKm = 0.5;
    private String mode = "driving";

    public double getOriginLat() { return originLat; }
    public void setOriginLat(double originLat) { this.originLat = originLat; }
    
    public double getOriginLng() { return originLng; }
    public void setOriginLng(double originLng) { this.originLng = originLng; }
    
    public double getBaseFee() { return baseFee; }
    public void setBaseFee(double baseFee) { this.baseFee = baseFee; }
    
    public double getPerKm() { return perKm; }
    public void setPerKm(double perKm) { this.perKm = perKm; }
    
    public String getMode() { return mode; }
    public void setMode(String mode) { this.mode = mode; }
}