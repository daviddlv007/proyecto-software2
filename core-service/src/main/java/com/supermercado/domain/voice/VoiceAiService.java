package com.supermercado.domain.voice;

import com.fasterxml.jackson.databind.JsonNode;
import com.supermercado.config.FeatureGate;
import com.supermercado.external.OpenAIClient;
import com.supermercado.repository.producto.ProductSearchRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class VoiceAiService {

  private final FeatureGate gate;
  private final OpenAIClient openai;
  private final ProductSearchRepository productRepo;

  public VoiceAiService(FeatureGate gate, OpenAIClient openai, ProductSearchRepository productRepo) {
    this.gate = gate; this.openai = openai; this.productRepo = productRepo;
  }

  public Result generateFromAudio(MultipartFile audio) {
    gate.requireVoiceAi();
    String transcript = openai.transcribe(audio);     // 1) STT
    return generateFromText(transcript).withTranscript(transcript);
  }

  public Result generateFromText(String text) {
    gate.requireVoiceAi();
    var extracted = openai.extractShoppingList(text);  // 2) GPT -> JSON {items:[...]}
    JsonNode itemsNode = extracted.json().path("items");
    List<Item> items = new ArrayList<>();
    if (itemsNode.isArray()) {
      for (JsonNode it : itemsNode) {
        String nombre = optStr(it,"nombre");
        double cantidad = optNum(it,"cantidad",1);
        String unidad = optStr(it,"unidad");
        if (nombre != null && !nombre.isBlank()) items.add(new Item(nombre, cantidad, unidad));
      }
    }

    // 3) Buscar en DB por nombre aproximado
    List<String> names = items.stream().map(i -> i.nombre).collect(Collectors.toList());
    var matches = productRepo.findByNamesApprox(names);

    // 4) Mapear disponibilidad
    List<Availability> availability = new ArrayList<>();
    for (Item it : items) {
      // elige el primer match por simplicidad
      Map<String,Object> best = matches.stream()
        .filter(m -> ((String)m.get("nombre")).toLowerCase().contains(it.nombre.toLowerCase()))
        .findFirst().orElse(null);

      if (best == null) {
        availability.add(Availability.notFound(it));
        continue;
      }

      int stock = ((Number)best.get("stock")).intValue();
      double req = it.cantidad;
      if (stock >= req) {
        availability.add(Availability.ok(it, best));
      } else if (stock > 0) {
        availability.add(Availability.partial(it, best, stock));
      } else {
        availability.add(Availability.out(it, best));
      }
    }

    return new Result(null, items, availability);
  }

  private String optStr(JsonNode n, String f) {
    return n.has(f) && !n.get(f).isNull() ? n.get(f).asText() : null;
  }
  private double optNum(JsonNode n, String f, double dft) {
    return n.has(f) && !n.get(f).isNull() ? n.get(f).asDouble(dft) : dft;
  }

  // --- DTOs de respuesta ---
  public record Item(String nombre, double cantidad, String unidad) {}
  public static class Availability {
    public String nombre;
    public Long productoId;
    public String matchNombre;
    public int stock;
    public double solicitado;
    public String status; // OK | PARTIAL | OUT | NOT_FOUND
    public double faltante;

    static Availability ok(Item it, Map<String,Object> m) {
      Availability a = base(it, m); a.status="OK"; a.faltante=0; return a; }
    static Availability partial(Item it, Map<String,Object> m, int stock) {
      Availability a = base(it, m); a.status="PARTIAL"; a.faltante=Math.max(0, it.cantidad-stock); return a; }
    static Availability out(Item it, Map<String,Object> m) {
      Availability a = base(it, m); a.status="OUT"; a.faltante=it.cantidad; a.stock=0; return a; }
    static Availability notFound(Item it) {
      Availability a = new Availability(); a.nombre=it.nombre; a.productoId=null; a.matchNombre=null;
      a.stock=0; a.solicitado=it.cantidad; a.status="NOT_FOUND"; a.faltante=it.cantidad; return a; }

    static Availability base(Item it, Map<String,Object> m) {
      Availability a = new Availability();
      a.nombre = it.nombre;
      a.solicitado = it.cantidad;
      a.productoId = ((Number)m.get("id")).longValue();
      a.matchNombre = String.valueOf(m.get("nombre"));
      a.stock = ((Number)m.get("stock")).intValue();
      return a;
    }
  }

  public static class Result {
    private String transcript;
    private List<Item> items;
    private List<Availability> availability;

    public Result(String transcript, List<Item> items, List<Availability> availability) {
      this.transcript = transcript; this.items = items; this.availability = availability;
    }
    public Result withTranscript(String t) { this.transcript = t; return this; }

    public String getTranscript() { return transcript; }
    public List<Item> getItems() { return items; }
    public List<Availability> getAvailability() { return availability; }
  }
}
