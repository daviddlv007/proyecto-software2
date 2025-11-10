package com.supermercado.web;

import com.supermercado.domain.voice.VoiceAiService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.util.Map;

@RestController
@RequestMapping("/voice")
public class VoiceController {

  private final VoiceAiService service;
  public VoiceController(VoiceAiService service) { this.service = service; }

  @PostMapping(value="/shopping-list", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
  public VoiceAiService.Result shoppingList(@RequestPart("file") MultipartFile file) {
    return service.generateFromAudio(file);
  }
  @PostMapping("/shopping-list-text")
    public VoiceAiService.Result shoppingListFromText(@RequestBody Map<String, String> request) {
        String text = request.get("text");
        if (text == null || text.isBlank()) {
            throw new IllegalArgumentException("Campo 'text' es requerido");
        }
        return service.generateFromText(text);
    }
}
