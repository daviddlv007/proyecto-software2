package com.supermercado.graphql;

import com.supermercado.config.FeatureGate;
import com.supermercado.domain.voice.VoiceAiService;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

@Controller
public class VoiceResolver {
  private final FeatureGate gate;
  private final VoiceAiService service;
  public VoiceResolver(FeatureGate gate, VoiceAiService service) { this.gate = gate; this.service = service; }

  @QueryMapping
  public VoiceAiService.Result generateShoppingList(@Argument String text) {
    gate.requireVoiceAi();
    return service.generateFromText(text);
  }
}
