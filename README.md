# YGO Deck Simulator API

Monte Carlo simulation for Yu-Gi-Oh! deck consistency analysis.

## Quickstart

```bash
docker compose up --build
```

API disponível em `http://localhost:8000`  
Docs interativos: `http://localhost:8000/docs`

---

## Endpoints

### `GET /health`
Verifica se o serviço está rodando.

### `POST /simulate`
Simula para um `min_techs` específico.

### `POST /simulate/batch`
Simula para `min_techs` = 0, 1 e 2 simultaneamente.

---

## Payload

```json
{
  "iterations": 1000000,
  "min_techs": 0,
  "deck_setup": {
    "Nome da Carta": [quantidade, "Tag1", "Tag2"]
  },
  "combo_patterns": [
    ["Tag ou CartaA", "Tag ou CartaB"]
  ],
  "clump_rules": [
    ["CartaA", "CartaB"],
    ["CartaA", "!TagNegacao"]
  ]
}
```

**`iterations`**: 1.000 – 10.000.000  
**`deck_setup`**: chave = nome da carta, valor = `[qtd, ...tags]`  
**`combo_patterns`**: lista de tags/cartas que formam uma jogada combinada  
**`clump_rules`**: par de cartas que conflitam; `!Tag` nega (só conta clump se a tag estiver ausente)

---

## Resposta

```json
{
  "hands_analyzed": 1000000,
  "deck_size": 40,
  "min_techs": 0,
  "success_rate": 82.34,
  "resilience_rate": 61.12,
  "dead_hand_rate": 5.21,
  "clumps": [
    {
      "rule": ["Mercourier", "Gold Sarcophagus"],
      "count": 3201,
      "percentage": 0.3201
    }
  ]
}
```
