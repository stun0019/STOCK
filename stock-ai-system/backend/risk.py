def calculate_target(
    entry,
    stop_loss,
    rr=3
):

    risk = entry - stop_loss

    target = entry + (risk * rr)

    return round(target, 2)
