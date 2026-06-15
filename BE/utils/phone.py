def normalize_phone(phone: str) -> str:
    digits = "".join(character for character in phone if character.isdigit())

    if digits.startswith("381") and len(digits) >= 11:
        return f"0{digits[3:]}"

    return digits


def phones_match(stored_phone: str, provided_phone: str) -> bool:
    stored = normalize_phone(stored_phone)
    provided = normalize_phone(provided_phone)

    if not stored or not provided:
        return False

    if stored == provided:
        return True

    if len(stored) >= 9 and len(provided) >= 9:
        return stored[-9:] == provided[-9:]

    return False
