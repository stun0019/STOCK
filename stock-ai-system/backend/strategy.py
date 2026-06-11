from risk import calculate_target


def generate_signal(symbol):

    mock_price = 100

    ema20 = 105
    ema60 = 95

    if ema20 > ema60:

        entry = mock_price

        stop_loss = entry - 5

        target = calculate_target(
            entry,
            stop_loss
        )

        return {
            "symbol": symbol,
            "direction": "LONG",
            "entry": entry,
            "stop_loss": stop_loss,
            "target": target,
            "score": 80
        }

    return None
