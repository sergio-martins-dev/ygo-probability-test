import random
from collections import Counter


def check_custom_clumps(hand_cards, card_data, clump_rules):
    """
    Avalia regras de clump contra a mão atual.
    Cada regra é uma lista de condições:
      - "Tag" ou "NomeDaCarta": pelo menos 1 carta na mão tem essa tag ou esse nome
      - "!Tag" ou "!NomeDaCarta": nenhuma carta na mão tem essa tag ou esse nome
    Todas as condições devem ser satisfeitas para o clump disparar.
    """
    # Constrói Counter com tags + nomes das cartas na mão
    hand_tags = Counter()
    for c in hand_cards:
        hand_tags[c] += 1
        for tag in card_data[c][1:]:
            hand_tags[tag] += 1

    results = {}
    for i, rule in enumerate(clump_rules):
        triggered = True
        for condition in rule:
            if condition.startswith('!'):
                key = condition[1:]
                if hand_tags[key] > 0:
                    triggered = False
                    break
            else:
                if hand_tags[condition] == 0:
                    triggered = False
                    break
        results[i] = triggered

    return results


def count_distinct_plays(hand_cards, card_data, combo_patterns):
    unique_plays = set()
    hand_tags = Counter()
    for c in hand_cards:
        hand_tags.update(card_data[c][1:])
        hand_tags[c] += 1

    ns_starter_found = False
    for card_name in hand_cards:
        tags = card_data[card_name][1:]
        is_starter   = 'Starter'       in tags
        is_extender  = 'Extender'      in tags
        is_ns        = 'Normal Summon' in tags
        if is_starter or is_extender:
            if is_starter and is_ns:
                # Todos os Starters de Normal Summon disputam UM slot de invocação
                ns_starter_found = True
            else:
                unique_plays.add(f"Source_{card_name}")
    if ns_starter_found:
        unique_plays.add("Source_NS_SLOT")

    for i, pattern in enumerate(combo_patterns):
        pattern_counts = Counter(pattern)
        if all(hand_tags[tag] >= need for tag, need in pattern_counts.items()):
            unique_plays.add(f"Combo_{i}")

    return len(unique_plays)


def _is_playable(card_name: str, card_data: dict, combo_patterns: list) -> bool:
    """Retorna True se a carta é Starter, Extender ou habilita algum combo."""
    tags = set(card_data[card_name][1:])
    if 'Starter' in tags or 'Extender' in tags:
        return True
    for pattern in combo_patterns:
        if card_name in pattern or tags.intersection(pattern):
            return True
    return False


def run_simulation(deck_data: dict, combo_patterns: list, clump_rules: list, min_techs: int, num_hands: int, sixth_card: bool = False) -> dict:
    deck = []
    for card_name, data in deck_data.items():
        deck.extend([card_name] * data[0])

    deck_size = len(deck)
    min_size = 6 if sixth_card else 5
    if deck_size < min_size:
        raise ValueError(f"Deck tem apenas {deck_size} cartas. Mínimo necessário: {min_size}.")

    stats = Counter()

    for _ in range(num_hands):
        drawn = random.sample(deck, 6 if sixth_card else 5)

        if sixth_card:
            sixth = drawn[5]
            hand = drawn if _is_playable(sixth, deck_data, combo_patterns) else drawn[:5]
            stats['sixth_used'] += 1 if len(hand) == 6 else 0
        else:
            hand = drawn

        plays = count_distinct_plays(hand, deck_data, combo_patterns)
        clumps = check_custom_clumps(hand, deck_data, clump_rules)

        is_any_clump = any(clumps.values())

        # dead_hand: only when there are truly no plays available
        # clump conflicts are tracked separately — they may or may not kill the hand
        if plays == 0:
            stats['dead_hand'] += 1

        for i, triggered in clumps.items():
            if triggered:
                stats[f'clump_{i}'] += 1

        # Auto-clump de Normal Summon: 2+ cartas NS na mesma mão brigam pelo slot
        ns_in_hand = sum(1 for c in hand if 'Normal Summon' in deck_data[c][1:])
        if ns_in_hand >= 2:
            stats['clump_ns'] += 1

        tech_count = sum(1 for c in hand if 'Tech' in deck_data[c][1:])
        has_enough_techs = tech_count >= min_techs

        # success_rate: chance de ver o "ingrediente principal"
        #   min_techs=0 → 1+ plays
        #   min_techs>0 → N+ techs (independente de plays)
        if min_techs == 0:
            stats['success'] += 1 if plays >= 1 else 0
        else:
            stats['success'] += 1 if has_enough_techs else 0

        # good_hand_rate: tem o ingrediente principal + pelo menos 1 play
        if has_enough_techs and plays >= 1:
            stats['good_hand'] += 1

        # resilience_rate: tem o ingrediente principal + pelo menos 2 plays
        if has_enough_techs and plays >= 2:
            stats['resilience'] += 1

    clump_details = []
    for i, rule in enumerate(clump_rules):
        count = stats[f'clump_{i}']
        clump_details.append({
            "rule": rule,
            "count": count,
            "percentage": round(count / num_hands * 100, 4)
        })

    # Adiciona auto-clump NS no topo se o deck tiver cartas de Normal Summon
    if any('Normal Summon' in data[1:] for data in deck_data.values()):
        ns_count = stats['clump_ns']
        clump_details.insert(0, {
            "rule": ["Normal Summon", "Normal Summon"],
            "count": ns_count,
            "percentage": round(ns_count / num_hands * 100, 4)
        })

    result = {
        "hands_analyzed": num_hands,
        "deck_size": deck_size,
        "min_techs": min_techs,
        "sixth_card": sixth_card,
        "success_rate": round(stats['success'] / num_hands * 100, 2),
        "good_hand_rate": round(stats['good_hand'] / num_hands * 100, 2),
        "resilience_rate": round(stats['resilience'] / num_hands * 100, 2),
        "dead_hand_rate": round(stats['dead_hand'] / num_hands * 100, 2),
        "clumps": clump_details,
    }

    if sixth_card:
        result["sixth_card_used_rate"] = round(stats['sixth_used'] / num_hands * 100, 2)

    return result