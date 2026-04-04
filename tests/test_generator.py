"""Unit tests for the Password Generator module."""

import math

import pytest

from src.generator import LowEntropyError, PasswordGenerator


def test_generate_random_returns_string_and_meta():
    gen = PasswordGenerator(min_length=8)
    result = gen.generate_random(length=16)

    assert isinstance(result, tuple)
    assert isinstance(result[0], str)
    assert isinstance(result[1], dict)
    assert "entropy_bits" in result[1]
    assert len(result[0]) == 16


def test_entropy_calculation():
    gen = PasswordGenerator()
    # H = L * log2(N)
    entropy = gen.calculate_entropy("A" * 16, 26)
    expected = 16 * math.log2(26)
    assert abs(entropy - expected) < 0.01


def test_low_entropy_raises_error():
    gen = PasswordGenerator(min_entropy=200)
    with pytest.raises(LowEntropyError):
        gen.generate_random(length=12, check_entropy=True)


def test_no_random_used():
    import src.generator

    with open(src.generator.__file__, encoding="utf-8") as f:
        content = f.read()

    assert "import random" not in content
    assert "import secrets" in content
