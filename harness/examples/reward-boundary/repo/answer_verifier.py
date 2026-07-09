SOURCE = "The contract total is 17 units. Delivery is due Friday."


def accepted(output, source=SOURCE):
    return output.get("answer") == "17 units"
