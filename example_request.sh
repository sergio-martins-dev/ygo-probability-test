# Exemplo de chamada — salve como branded_despia.json e use com curl

# POST /simulate/batch  →  roda min_techs 0, 1 e 2 de uma vez
# POST /simulate        →  roda para um min_techs específico

PAYLOAD='{
  "iterations": 1000000,
  "deck_setup": {
    "Aluber":              [2, "NS", "AlvoCartesia", "Starter"],
    "Cartesia":            [2, "NS", "AlvoSpirits", "AlvoCartesia"],
    "Fuwalos":             [3, "AlvoSpirits", "Tech"],
    "White Dragon":        [2, "AlvoCartesia", "AlvoSpirits", "Extender", "Starter"],
    "Incredible Ecclesia": [2, "NS", "AlvoCartesia", "AlvoSpirits", "Starter"],
    "Dogmatika Ecclesia":  [1, "NS", "AlvoCartesia", "AlvoSpirits", "Starter"],
    "Quem":                [1, "NS", "AlvoCartesia", "AlvoSpirits", "Brick"],
    "Albaz":               [1, "AlvoCartesia", "AlvoSpirits", "Brick"],
    "Albion Shrouded":     [1, "AlvoCartesia", "AlvoSpirits", "Brick"],
    "Magnamhut":           [1, "AlvoCartesia", "AlvoSpirits", "Tech"],
    "Mercourier":          [1, "AlvoCartesia", "AlvoSpirits", "Brick"],
    "Droll":               [2, "Tech", "AlvoSpirits"],
    "Lava Golem":          [3, "Tech", "AlvoSpirits"],
    "Bolota":              [3, "Tech", "AlvoSpirits"],
    "High Spirits":        [3],
    "Nadir Servant":       [3, "Starter", "Extender"],
    "Gold Sarcophagus":    [1, "Starter", "Extender"],
    "Branded Fusion":      [1, "Starter", "Extender"],
    "Branded Opening":     [2, "Starter", "Extender"],
    "Super Polymerization":[3, "Tech"],
    "Fallen & Virtuous":   [3, "Tech"]
  },
  "combo_patterns": [
    ["Quem", "Albion Shrouded"],
    ["Quem", "Magnamhut"],
    ["Quem", "Fallen & Virtuous"],
    ["Mercourier", "Magnamhut"],
    ["Cartesia", "AlvoCartesia"],
    ["High Spirits", "AlvoSpirits"]
  ],
  "clump_rules": [
    ["Mercourier", "Gold Sarcophagus"],
    ["Lava Golem", "!Extender"],
    ["Bolota", "!Extender"]
  ]
}'

# Batch (min_techs 0/1/2 juntos):
# curl -s -X POST http://localhost:8000/simulate/batch \
#      -H "Content-Type: application/json" \
#      -d "$PAYLOAD" | python3 -m json.tool

# Single (min_techs específico — adicione "min_techs": 1 ao payload):
# curl -s -X POST http://localhost:8000/simulate \
#      -H "Content-Type: application/json" \
#      -d "$PAYLOAD" | python3 -m json.tool
