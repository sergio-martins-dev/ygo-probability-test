import random
from collections import Counter


def check_custom_clumps(hand_cards, card_data, clump_rules):
    results = {}
    for i, rule in enumerate(clump_rules):
        carta_a = rule[0]

        # Formato: [CartaA, "!Tag"] — carta única + negação
        if len(rule) == 2 and rule[1].startswith('!'):
            if carta_a in hand_cards:
                negacao = rule[1][1:]
                has_negacao = any(negacao in card_data[c][1:] or negacao == c for c in hand_cards)
                results[i] = not has_negacao
            else:
                results[i] = False

        # Formato: [CartaA, CartaB] ou [CartaA, CartaB, "!Tag"]
        else:
            carta_b = rule[1]
            if carta_a in hand_cards and carta_b in hand_cards:
                if len(rule) > 2 and rule[2].startswith('!'):
                    negacao = rule[2][1:]
                    has_negacao = any(negacao in card_data[c][1:] or negacao == c for c in hand_cards)
                    results[i] = not has_negacao
                else:
                    results[i] = True
            else:
                results[i] = False

    return results


def count_distinct_plays(hand_cards, card_data, combo_patterns):
    unique_plays = set()
    hand_tags = Counter()
    for c in hand_cards:
        hand_tags.update(card_data[c][1:])
        hand_tags[c] += 1

    for card_name in hand_cards:
        if 'Starter' in card_data[card_name][1:] or 'Extender' in card_data[card_name][1:]:
            unique_plays.add(f"Source_{card_name}")

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

        if plays == 0 or is_any_clump:
            stats['dead_hand'] += 1

        for i, triggered in clumps.items():
            if triggered:
                stats[f'clump_{i}'] += 1

        if plays >= 2:
            stats['multi_play'] += 1

        tech_count = sum(1 for c in hand if 'Tech' in deck_data[c][1:])
        if tech_count >= min_techs and plays >= (1 if min_techs == 0 else 2):
            stats['good_hand'] += 1

    clump_details = []
    for i, rule in enumerate(clump_rules):
        count = stats[f'clump_{i}']
        clump_details.append({
            "rule": rule,
            "count": count,
            "percentage": round(count / num_hands * 100, 4)
        })

    result = {
        "hands_analyzed": num_hands,
        "deck_size": deck_size,
        "min_techs": min_techs,
        "sixth_card": sixth_card,
        "success_rate": round(stats['good_hand'] / num_hands * 100, 2),
        "resilience_rate": round(stats['multi_play'] / num_hands * 100, 2),
        "dead_hand_rate": round(stats['dead_hand'] / num_hands * 100, 2),
        "clumps": clump_details,
    }

    if sixth_card:
        result["sixth_card_used_rate"] = round(stats['sixth_used'] / num_hands * 100, 2)

    return result