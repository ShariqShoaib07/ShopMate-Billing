from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


_ONES = [
    "Zero",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
]
_TEENS = [
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen",
]
_TENS = [
    "",
    "",
    "Twenty",
    "Thirty",
    "Forty",
    "Fifty",
    "Sixty",
    "Seventy",
    "Eighty",
    "Ninety",
]
_PLACE_NAMES = ["", "Thousand", "Lakh", "Crore", "Arab", "Kharab"]


def rupees_in_words(amount: Decimal | int | float | str) -> str:
    value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    rupees = int(value)
    paise = int((value - Decimal(rupees)) * 100)

    words = _integer_in_words(rupees)
    if paise:
        paise_words = _integer_in_words(paise)
        return f"{words} Rupees and {paise_words} Paisa Only"
    return f"{words} Rupees Only"


def _integer_in_words(number: int) -> str:
    if number == 0:
        return _ONES[0]

    groups: list[int] = []
    groups.append(number % 1000)
    number //= 1000
    while number > 0:
        groups.append(number % 100)
        number //= 100

    parts: list[str] = []
    for index, group in reversed(list(enumerate(groups))):
        if group == 0:
            continue
        words = _convert_group(group)
        place_name = _PLACE_NAMES[index] if index < len(_PLACE_NAMES) else ""
        parts.append(f"{words} {place_name}".strip())

    return " ".join(parts)


def _convert_group(number: int) -> str:
    parts: list[str] = []
    if number >= 100:
        parts.append(_ONES[number // 100])
        parts.append("Hundred")
        number %= 100

    if number >= 20:
        parts.append(_TENS[number // 10])
        if number % 10:
            parts.append(_ONES[number % 10])
    elif number >= 10:
        parts.append(_TEENS[number - 10])
    elif number > 0:
        parts.append(_ONES[number])

    return " ".join(parts)