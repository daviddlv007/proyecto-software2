package com.supermercado.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "jwt")
public class JwtProperties {
    private String secret = "change-this-super-secret-key-in-production-minimum-256-bits";
    private long expiration = 86400000;

    public String getSecret() { return secret; }
    public void setSecret(String secret) { this.secret = secret; }
    
    public long getExpiration() { return expiration; }
    public void setExpiration(long expiration) { this.expiration = expiration; }
}