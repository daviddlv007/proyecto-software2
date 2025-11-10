package com.supermercado.external;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.supermercado.config.OpenAIProperties;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.multipart.MultipartFile;

import java.nio.charset.StandardCharsets;
import java.util.Map;

@Component
public class OpenAIClient {

  private final WebClient web;
  private final ObjectMapper mapper = new ObjectMapper();
  private final OpenAIProperties props;

  public OpenAIClient(OpenAIProperties props) {
    this.props = props;
    this.web = WebClient.builder()
        .baseUrl("https://api.openai.com")
        .defaultHeader("Authorization", "Bearer " + props.getApiKey())
        .build();
  }

  /** Transcribe audio a texto con Whisper (whisper-1). */
  public String transcribe(MultipartFile audio) {
    try {
      byte[] bytes = audio.getBytes();
      var fileRes = new ByteArrayResource(bytes) {
        @Override public String getFilename() { return audio.getOriginalFilename(); }
      };

      MultipartBodyBuilder mb = new MultipartBodyBuilder();
      mb.part("file", fileRes)
        .filename(audio.getOriginalFilename())
        .contentType(MediaType.APPLICATION_OCTET_STREAM);
      mb.part("model", props.getTranscribeModel());

      String json = web.post()
          .uri("/v1/audio/transcriptions")
          .contentType(MediaType.MULTIPART_FORM_DATA)
          .body(BodyInserters.fromMultipartData(mb.build()))
          .retrieve()
          .bodyToMono(String.class)
          .block();

      JsonNode root = mapper.readTree(json);
      return root.path("text").asText(); // campo 'text' de transcriptions
    } catch (Exception e) {
      throw new RuntimeException("Error transcribing audio: " + e.getMessage(), e);
    }
  }

  /** Pide a GPT que extraiga una lista estructurada de productos/cantidades desde texto libre. */
  public ExtractResult extractShoppingList(String text) {
    try {
      // Forzamos JSON de salida con un prompt simple; también puedes usar response_format=json.
      String system = """
        Eres un asistente que extrae listas de compras en español.
        Devuelve JSON con este formato:
        { "items": [ { "nombre": "leche", "cantidad": 2, "unidad": "botellas" } ], "observaciones": "" }
        Si no encuentras items, devuelve items: [].
        """;

      var body = Map.of(
        "model", props.getTextModel(),
        "temperature", 0,
        "messages", new Object[] {
          Map.of("role", "system", "content", system),
          Map.of("role", "user",   "content", "Texto de usuario:\n" + text + "\nExtrae lista.")
        }
      );

      String json = web.post()
          .uri("/v1/chat/completions")
          .contentType(MediaType.APPLICATION_JSON)
          .bodyValue(body)
          .retrieve()
          .bodyToMono(String.class)
          .block();

      JsonNode root = mapper.readTree(json);
      String content = root.path("choices").get(0).path("message").path("content").asText();

      JsonNode parsed;
      try { parsed = mapper.readTree(content); }
      catch(Exception ignored) {
        // si el modelo devolvió texto con backticks, intenta limpiar
        String cleaned = content.replaceAll("```json", "").replaceAll("```", "").trim();
        parsed = mapper.readTree(cleaned);
      }

      return new ExtractResult(parsed);
    } catch (Exception e) {
      throw new RuntimeException("Error extracting list with GPT: " + e.getMessage(), e);
    }
  }

  public record ExtractResult(JsonNode json) {}
}
