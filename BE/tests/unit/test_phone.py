import pytest

from utils.phone import normalize_phone, phones_match


@pytest.mark.unit
def test_normalize_phone_strips_non_digits_and_converts_381_prefix() -> None:
    assert normalize_phone("+381 64 123-4567") == "0641234567"
    assert normalize_phone("0641234567") == "0641234567"


@pytest.mark.unit
def test_phones_match_accepts_equivalent_numbers() -> None:
    assert phones_match("0641234567", "0641234567") is True
    assert phones_match("+381641234567", "064 123 4567") is True
    assert phones_match("0641234567", "0619999999") is False
    assert phones_match("", "0641234567") is False
