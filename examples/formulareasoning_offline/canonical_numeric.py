"""Offline, synthetic-only, unitless six-significant-digit prototype.

This is NOT the Courtroom/FormulaReasoning scorer. See README.md for the
unsupported typed-normalization, reference-audit, and registration requirements.
All accepted arithmetic is integer/rational; binary floats are never adjudicated.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import re
from typing import Any

PRECISION = 6
MAX_INPUT_CHARACTERS = 4096
MAX_LITERAL_EXPONENT = 10_000
MAX_CONFIG_EXPONENT = 10_000
_DECIMAL = re.compile(
    r"(?P<sign>[+-]?)(?:(?P<integer>[0-9]+)(?:\.(?P<fraction>[0-9]*))?"
    r"|\.(?P<only_fraction>[0-9]+))(?:[eE](?P<exponent>[+-]?[0-9]+))?\Z"
)
_RATIONAL = re.compile(r"(?P<numerator>[+-]?[0-9]+)\s*/\s*(?P<denominator>[+-]?[0-9]+)\Z")


@dataclass(frozen=True)
class GridConfig:
    """One explicit global interval, not item-specific or study-registered here."""

    e_min: int
    e_max: int

    def __post_init__(self) -> None:
        if type(self.e_min) is not int or type(self.e_max) is not int:
            raise ValueError("Exponent bounds must be integers, not booleans or floats")
        if not -MAX_CONFIG_EXPONENT <= self.e_min <= self.e_max <= MAX_CONFIG_EXPONENT:
            raise ValueError("Require -10000 <= e_min <= e_max <= 10000")

    @property
    def alphabet_size(self) -> int:
        """Full signed numeric grid plus zero and bottom, not observed labels."""
        return 2 + 1_800_000 * (self.e_max - self.e_min + 1)


@dataclass(frozen=True)
class Label:
    kind: str
    sign: int | None = None
    coefficient: int | None = None
    exponent: int | None = None

    def as_dict(self) -> dict[str, Any]:
        if self.kind == "finite":
            return {
                "kind": self.kind,
                "sign": self.sign,
                "coefficient": self.coefficient,
                "exponent": self.exponent,
            }
        return {"kind": self.kind}


BOTTOM = Label("bottom")
ZERO = Label("zero")


@dataclass(frozen=True)
class CanonicalResult:
    label: Label
    reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {"label": self.label.as_dict(), "reason": self.reason}


def _failure(reason: str) -> CanonicalResult:
    return CanonicalResult(BOTTOM, reason)


def _bounded_signed_integer(text: str, bound: int) -> int:
    # Remove leading zeros before converting an exponent to keep parsing bounded.
    negative = text.startswith("-")
    digits = text.lstrip("+-").lstrip("0") or "0"
    if len(digits) > len(str(bound)):
        raise ValueError("literal_exponent_limit")
    value = int(digits)
    if value > bound:
        raise ValueError("literal_exponent_limit")
    return -value if negative else value


def _parse_exact(token: str) -> Fraction:
    match = _DECIMAL.fullmatch(token)
    if match:
        exponent = _bounded_signed_integer(match["exponent"] or "0", MAX_LITERAL_EXPONENT)
        integer = match["integer"] or "0"
        fractional = match["fraction"]
        if fractional is None:
            fractional = match["only_fraction"] or ""
        coefficient = int(integer + fractional)
        if match["sign"] == "-":
            coefficient = -coefficient
        power = exponent - len(fractional)
        if power >= 0:
            return Fraction(coefficient * 10**power)
        return Fraction(coefficient, 10**(-power))
    match = _RATIONAL.fullmatch(token)
    if match:
        denominator = int(match["denominator"])
        if denominator == 0:
            raise ValueError("zero_denominator")
        return Fraction(int(match["numerator"]), denominator)
    raise ValueError("unsupported_or_malformed_number")


def _decimal_digits(n: int) -> int:
    """Exact digit count without converting potentially large integers to text."""
    # The bit-length estimate need not be exact; both corrections are exact.
    estimate = max(1, (n.bit_length() * 30103) // 100000 + 1)
    while n < 10 ** (estimate - 1):
        estimate -= 1
    while n >= 10**estimate:
        estimate += 1
    return estimate


def _normalized_exponent(numerator: int, denominator: int) -> int:
    exponent = _decimal_digits(numerator) - _decimal_digits(denominator)
    if exponent >= 0:
        if numerator < denominator * 10**exponent:
            exponent -= 1
    elif numerator * 10**(-exponent) < denominator:
        exponent -= 1
    return exponent


def _round_exact(value: Fraction, config: GridConfig) -> CanonicalResult:
    if not value:
        return CanonicalResult(ZERO)
    sign = 1 if value > 0 else -1
    numerator, denominator = abs(value.numerator), value.denominator
    exponent = _normalized_exponent(numerator, denominator)
    shift = PRECISION - 1 - exponent
    if shift >= 0:
        numerator *= 10**shift
    else:
        denominator *= 10**(-shift)
    coefficient, remainder = divmod(numerator, denominator)
    doubled = 2 * remainder
    if doubled > denominator or (doubled == denominator and coefficient % 2):
        coefficient += 1
    # A carry must precede the bounds check: 9.999995 -> 1.00000e1.
    if coefficient == 10**PRECISION:
        coefficient //= 10
        exponent += 1
    if not config.e_min <= exponent <= config.e_max:
        return _failure("rounded_exponent_out_of_range")
    return CanonicalResult(Label("finite", sign, coefficient, exponent))


def canonicalize_numeric(token: Any, config: GridConfig) -> CanonicalResult:
    """Canonicalize an exact *unitless* string, or fail closed to bottom.

    Supported syntax: an ASCII decimal/scientific literal, or integer/integer.
    No expression evaluation, units, percentages, binary floats, uncertainty,
    intervals, multiple candidates, or target-specific metadata are accepted.
    """
    if not isinstance(config, GridConfig):
        raise TypeError("Use an explicit GridConfig")
    if type(token) is not str:
        return _failure("exact_string_required")
    if len(token) > MAX_INPUT_CHARACTERS:
        return _failure("input_length_limit")
    token = token.strip()
    if not token:
        return _failure("empty_number")
    try:
        value = _parse_exact(token)
    except ValueError as error:
        return _failure(str(error))
    return _round_exact(value, config)


def canonicalize_answer(raw: Any, config: GridConfig) -> CanonicalResult:
    """Synthetic schema: null/no-answer, or exactly {\"answer\": \"number\"}.

    Extra fields or multiple candidates are rejected, never searched for a
    favorable value. This minimal schema is not the paper's registered schema.
    Input objects are neither normalized in place nor mutated.
    """
    if not isinstance(config, GridConfig):
        raise TypeError("Use an explicit GridConfig")
    if raw is None:
        return _failure("no_answer")
    if type(raw) is not dict or set(raw) != {"answer"}:
        return _failure("unsupported_or_ambiguous_answer_object")
    return canonicalize_numeric(raw["answer"], config)
