import re
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from simulator import run_simulation

app = FastAPI(
    title="YGO Deck Simulator",
    description="Monte Carlo simulation for Yu-Gi-Oh! deck consistency analysis",
    version="1.0.0"
)


class SimulationRequest(BaseModel):
    deck_setup: dict = Field(..., description="Card name → [quantity, ...tags]")
    combo_patterns: list = Field(default=[], description="List of tag combos that trigger plays")
    clump_rules: list = Field(default=[], description="List of clump rules, supports !Tag negation")
    min_techs: int = Field(default=0, ge=0, description="Minimum techs required in hand for good_hand metric")
    iterations: int = Field(default=100000, ge=1000, le=10000000, description="Number of hands to simulate (1k–10M)")

    @field_validator('deck_setup')
    @classmethod
    def validate_deck(cls, v):
        for card, data in v.items():
            if not isinstance(data, list) or len(data) < 1:
                raise ValueError(f"Card '{card}' must be a list with at least [quantity]")
            if not isinstance(data[0], int) or data[0] < 1:
                raise ValueError(f"Card '{card}' quantity must be a positive integer")
        total = sum(d[0] for d in v.values())
        if total < 5:
            raise ValueError(f"Deck has only {total} cards. Minimum is 5.")
        return v


class ClumpDetail(BaseModel):
    rule: list
    count: int
    percentage: float


class SimulationResponse(BaseModel):
    hands_analyzed: int
    deck_size: int
    min_techs: int
    sixth_card: bool
    success_rate: float
    good_hand_rate: float
    resilience_rate: float
    dead_hand_rate: float
    clumps: list[ClumpDetail]
    sixth_card_used_rate: Optional[float] = None


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    try:
        result = run_simulation(
            deck_data=req.deck_setup,
            combo_patterns=req.combo_patterns,
            clump_rules=req.clump_rules,
            min_techs=req.min_techs,
            num_hands=req.iterations,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@app.post("/simulate/batch")
def simulate_batch(req: SimulationRequest):
    """Roda a simulação para min_techs = 0, 1 e 2, em mãos de 5 e 6 cartas (6ª só se for jogável)."""
    results = {}
    for sixth in [False, True]:
        key = "hand_6_if_playable" if sixth else "hand_5"
        results[key] = {}
        for techs in [0, 1, 2]:
            try:
                results[key][f"min_techs_{techs}"] = run_simulation(
                    deck_data=req.deck_setup,
                    combo_patterns=req.combo_patterns,
                    clump_rules=req.clump_rules,
                    min_techs=techs,
                    num_hands=req.iterations,
                    sixth_card=sixth,
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
    return results


app.mount("/static", StaticFiles(directory="static"), name="static")


# ──────────────────────────────────────
# DECK PARSER
# ──────────────────────────────────────

class ParseDeckRequest(BaseModel):
    text: str = Field(..., description="Raw YGO deck text with Monster/Spell/Trap/Extra/Side sections")


class ParseDeckResponse(BaseModel):
    deck_setup: dict
    card_count: int
    sections: dict


_IGNORED_SECTIONS = {"extra", "side"}
_SECTION_HEADER   = re.compile(r"^(Monster|Spell|Trap|Extra|Side)s?$", re.IGNORECASE)
_CARD_LINE        = re.compile(r"^(\d+)x?\s+(.+)$")


@app.post("/decks/parse", response_model=ParseDeckResponse)
def parse_deck(req: ParseDeckRequest):
    """Parse raw YGO deck text into deck_setup format. Ignores Extra and Side deck."""
    deck_setup: dict = {}
    sections: dict   = {}
    current_section  = None

    for raw_line in req.text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m_section = _SECTION_HEADER.match(line)
        if m_section:
            current_section = m_section.group(1).capitalize()
            if current_section.lower() not in _IGNORED_SECTIONS:
                sections.setdefault(current_section, [])
            continue

        if current_section is None or current_section.lower() in _IGNORED_SECTIONS:
            continue

        m_card = _CARD_LINE.match(line)
        if m_card:
            qty  = int(m_card.group(1))
            name = m_card.group(2).strip()
            # Se a carta já apareceu (duplicata no texto), soma a quantidade
            if name in deck_setup:
                deck_setup[name][0] += qty
            else:
                deck_setup[name] = [qty]
            sections[current_section].append(name)

    card_count = sum(v[0] for v in deck_setup.values())
    return {"deck_setup": deck_setup, "card_count": card_count, "sections": sections}
