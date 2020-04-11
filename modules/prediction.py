import math
from functools import cmp_to_key


def minimum_rate_from_given_and_base(given_price, base_price):
    return 10000 * (given_price - 1) / base_price


def maximum_rate_from_given_and_base(given_price, base_price):
    return 10000 * given_price / base_price


def generate_pattern_0_with_lengths(given_prices, high_phase_1_len, dec_phase_1_len, high_phase_2_len, dec_phase_2_len,
                                    high_phase_3_len):
    # PATTERN 0: high, decreasing, high, decreasing, high
    base_price = given_prices[0]
    predicted_prices = [
        {
            "min": base_price,
            "max": base_price
        },
        {
            "min": base_price,
            "max": base_price
        },
    ]

    # High Phase 1
    for i in range(2, 2 + high_phase_1_len):
        min_pred = math.floor(0.9 * base_price)
        max_pred = math.ceil(1.4 * base_price)
        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

    # Dec Phase 1
    min_rate = 6000
    max_rate = 8000
    for i in range(2 + high_phase_1_len, 2 + high_phase_1_len + dec_phase_1_len):
        min_pred = math.floor(min_rate * base_price / 10000)
        max_pred = math.ceil(max_rate * base_price / 10000)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]
            min_rate = minimum_rate_from_given_and_base(given_prices[i], base_price)
            max_rate = maximum_rate_from_given_and_base(given_prices[i], base_price)

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

        min_rate -= 1000
        max_rate -= 400

    # High Phase 2
    for i in range(2 + high_phase_1_len + dec_phase_1_len, 2 + high_phase_1_len + dec_phase_1_len + high_phase_2_len):
        min_pred = math.floor(0.9 * base_price)
        max_pred = math.ceil(1.4 * base_price)
        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

    # Dec Phase 2
    min_rate = 6000
    max_rate = 8000
    for i in range(2 + high_phase_1_len + dec_phase_1_len + high_phase_2_len,
                   2 + high_phase_1_len + dec_phase_1_len + high_phase_2_len + dec_phase_2_len):
        min_pred = math.floor(min_rate * base_price / 10000)
        max_pred = math.ceil(max_rate * base_price / 10000)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]
            min_rate = minimum_rate_from_given_and_base(given_prices[i], base_price)
            max_rate = maximum_rate_from_given_and_base(given_prices[i], base_price)

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

        min_rate -= 1000
        max_rate -= 400

    # High Phase 3
    if 2 + high_phase_1_len + dec_phase_1_len + high_phase_2_len + dec_phase_2_len + high_phase_3_len != 14:
        return

    for i in range(2 + high_phase_1_len + dec_phase_1_len + high_phase_2_len + dec_phase_2_len, 14):
        min_pred = math.floor(0.9 * base_price)
        max_pred = math.ceil(1.4 * base_price)
        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred,
        })

    yield {
        "pattern_description": "high, decreasing, high, decreasing, high",
        "pattern_number": 0,
        "prices": predicted_prices
    }


def generate_pattern_0(given_prices):
    for dec_phase_1_len in range(2, 4):
        for high_phase_1_len in range(0, 7):
            for high_phase_3_len in range(0, 7 - high_phase_1_len):
                yield generate_pattern_0_with_lengths(given_prices,
                                                      high_phase_1_len,
                                                      dec_phase_1_len,
                                                      7 - high_phase_1_len - high_phase_3_len,
                                                      5 - dec_phase_1_len, high_phase_3_len)


def generate_pattern_1_with_peak(given_prices, peak_start):
    # PATTERN 1: decreasing middle, high spike, random low
    base_price = given_prices[0]
    predicted_prices = [
        {
            "min": base_price,
            "max": base_price
        },
        {
            "min": base_price,
            "max": base_price
        }
    ]

    min_rate = 8500
    max_rate = 9000

    for i in range(2, peak_start):
        min_pred = math.floor(min_rate * base_price / 10000)
        max_pred = math.ceil(max_rate * base_price / 10000)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return
            min_pred = given_prices[i]
            max_pred = given_prices[i]
            min_rate = minimum_rate_from_given_and_base(given_prices[i], base_price)
            max_rate = maximum_rate_from_given_and_base(given_prices[i], base_price)

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

        min_rate -= 500
        max_rate -= 300

    # Now each day is independent of next
    min_randoms = [0.9, 1.4, 2.0, 1.4, 0.9, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
    max_randoms = [1.4, 2.0, 6.0, 2.0, 1.4, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
    for i in range(peak_start, 14):
        min_pred = math.floor(min_randoms[i - peak_start] * base_price)
        max_pred = math.ceil(max_randoms[i - peak_start] * base_price)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return
            min_pred = given_prices[i]
            max_pred = given_prices[i]

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

    yield {
        "pattern_description": "decreasing, high spike, random lows",
        "pattern_number": 1,
        "prices": predicted_prices
    }


def generate_pattern_1(given_prices):
    for peak_start in range(3, 10):
        yield generate_pattern_1_with_peak(given_prices, peak_start)


def generate_pattern_2_generator(given_prices):
    # PATTERN 2: consistently decreasing
    base_price = given_prices[0]
    predicted_prices = [
        {
            "min": base_price,
            "max": base_price
        },
        {
            "min": base_price,
            "max": base_price
        },
    ]

    min_rate = 8500
    max_rate = 9000
    for i in range(2, 14):
        min_pred = math.floor(min_rate * base_price / 10000)
        max_pred = math.ceil(max_rate * base_price / 10000)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]
            min_rate = minimum_rate_from_given_and_base(given_prices[i], base_price)
            max_rate = maximum_rate_from_given_and_base(given_prices[i], base_price)

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

        min_rate -= 500
        max_rate -= 300

    yield {
        "pattern_description": "always decreasing",
        "pattern_number": 2,
        "prices": predicted_prices
    }


def generate_pattern_2(given_prices):
    yield generate_pattern_2_generator(given_prices)


def generate_pattern_3_with_peak(given_prices, peak_start):
    # PATTERN 3: decreasing, spike, decreasing
    base_price = given_prices[0]
    predicted_prices = [
        {
            "min": base_price,
            "max": base_price
        },
        {
            "min": base_price,
            "max": base_price
        },
    ]

    min_rate = 4000
    max_rate = 9000

    for i in range(2, peak_start):
        min_pred = math.floor(min_rate * base_price / 10000)
        max_pred = math.ceil(max_rate * base_price / 10000)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]
            min_rate = minimum_rate_from_given_and_base(given_prices[i], base_price)
            max_rate = maximum_rate_from_given_and_base(given_prices[i], base_price)

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

        min_rate -= 500
        max_rate -= 300

    # The peak
    for i in range(peak_start, peak_start + 2):
        min_pred = math.floor(0.9 * base_price)
        max_pred = math.ceil(1.4 * base_price)
        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

    # Main spike 1
    min_pred = math.floor(1.4 * base_price) - 1
    max_pred = math.ceil(2.0 * base_price) - 1
    if given_prices[peak_start + 2]:
        if given_prices[peak_start + 2] < min_pred or given_prices[peak_start + 2] > max_pred:
            # Given price is out of predicted range, so this is the wrong pattern
            return
        min_pred = given_prices[peak_start + 2]
        max_pred = given_prices[peak_start + 2]

    predicted_prices.append({
        "min": min_pred,
        "max": max_pred
    })

    # Main spike 2
    min_pred = predicted_prices[peak_start + 2]["min"]
    max_pred = math.ceil(2.0 * base_price)
    if given_prices[peak_start + 3]:
        if given_prices[peak_start + 3] < min_pred or given_prices[peak_start + 3] > max_pred:
            # Given price is out of predicted range, so this is the wrong pattern
            return

        min_pred = given_prices[peak_start + 3]
        max_pred = given_prices[peak_start + 3]

    predicted_prices.append({
        "min": min_pred,
        "max": max_pred
    })

    # Main spike 3
    min_pred = math.floor(1.4 * base_price) - 1
    max_pred = predicted_prices[peak_start + 3]["max"] - 1
    if given_prices[peak_start + 4]:
        if given_prices[peak_start + 4] < min_pred or given_prices[peak_start + 4] > max_pred:
            # Given price is out of predicted range, so this is the wrong pattern
            return

        min_pred = given_prices[peak_start + 4]
        max_pred = given_prices[peak_start + 4]

    predicted_prices.append({
        "min": min_pred,
        "max": max_pred
    })

    if peak_start + 5 < 14:
        min_rate = 4000
        max_rate = 9000

    for i in range(peak_start + 5, 14):
        min_pred = math.floor(min_rate * base_price / 10000)
        max_pred = math.ceil(max_rate * base_price / 10000)

        if given_prices[i]:
            if given_prices[i] < min_pred or given_prices[i] > max_pred:
                # Given price is out of predicted range, so this is the wrong pattern
                return

            min_pred = given_prices[i]
            max_pred = given_prices[i]
            min_rate = minimum_rate_from_given_and_base(given_prices[i], base_price)
            max_rate = maximum_rate_from_given_and_base(given_prices[i], base_price)

        predicted_prices.append({
            "min": min_pred,
            "max": max_pred
        })

        min_rate -= 500
        max_rate -= 300

    yield {
        "pattern_description": "decreasing, spike, decreasing",
        "pattern_number": 3,
        "prices": predicted_prices
    }


def generate_pattern_3(given_prices):
    for peak_start in range(2, 10):
        yield generate_pattern_3_with_peak(given_prices, peak_start)


def generate_possibilities(sell_prices):
    if sell_prices[0]:
        yield generate_pattern_0(sell_prices)
        yield generate_pattern_1(sell_prices)
        yield generate_pattern_2(sell_prices)
        yield generate_pattern_3(sell_prices)
    else:
        for base_price in range(90, 110):
            sell_prices[0] = sell_prices[1] = base_price
            yield generate_pattern_0(sell_prices)
            yield generate_pattern_1(sell_prices)
            yield generate_pattern_2(sell_prices)
            yield generate_pattern_3(sell_prices)


# not sure about this either
def analyze_possibilities(sell_prices):
    generated_possibilities = list(generate_possibilities(sell_prices))
    possibilities = []
    for poss_generator in generated_possibilities:
        for poss_gen in poss_generator:
            for poss in poss_gen:
                possibilities.append(poss)

    global_min_max = []
    for day in range(0, 14):
        prices = {
            "min": 999,
            "max": 0
        }

        for poss in possibilities:
            if poss["prices"][day]["min"] < prices["min"]:
                prices["min"] = poss["prices"][day]["min"]

            if poss["prices"][day]["max"] > prices["max"]:
                prices["max"] = poss["prices"][day]["max"]

        global_min_max.append(prices)

    possibilities.append({
        "pattern_description": "predicted min/max across all patterns",
        "pattern_number": 4,
        "prices": global_min_max
    })

    for poss in possibilities:
        week_mins = []
        week_maxes = []

        for day in poss["prices"][1:]:
            week_mins.append(day["min"])
            week_maxes.append(day["max"])

        poss["week_min"] = min(week_mins)
        poss["week_max"] = max(week_maxes)

    sorted(possibilities, key=cmp_to_key(lambda x, y: x["week_max"] < y["week_max"]))
    return possibilities
