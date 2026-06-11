from strategy import generate_signal


def scan_market():

    symbols = [
        "2330",
        "2454",
        "2317"
    ]

    results = []

    for symbol in symbols:

        signal = generate_signal(symbol)

        if signal:
            results.append(signal)

    return results
