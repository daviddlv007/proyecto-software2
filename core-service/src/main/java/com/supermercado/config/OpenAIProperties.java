package com.supermercado.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "openai")
public class OpenAIProperties {
  private String apiKey;
  private String transcribeModel = "whisper-1";
  private String textModel = "gpt-4o-mini";

  public String getApiKey() { return apiKey; }
  public void setApiKey(String apiKey) { this.apiKey = apiKey; }
  public String getTranscribeModel() { return transcribeModel; }
  public void setTranscribeModel(String transcribeModel) { this.transcribeModel = transcribeModel; }
  public String getTextModel() { return textModel; }
  public void setTextModel(String textModel) { this.textModel = textModel; }
}
