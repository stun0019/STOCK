
class OddsError(ValueError):
    """Raised when odds or probability inputs are invalid."""


def validate_decimal_odds(odds):
    odds = float(odds)
    if odds <= 1:
        raise OddsError("Decimal odds must be greater than 1.0.")
    return odds


def validate_probability(probability):
    probability = float(probability)
    if probability < 0 or probability > 1:
        raise OddsError("Probability must be between 0 and 1.")
    return probability


def implied_probability(odds):
    odds = validate_decimal_odds(odds)
    return 1 / odds


def calculate_ev(probability, odds):
    probability = validate_probability(probability)
    odds = validate_decimal_odds(odds)
    return (probability * odds) - 1
