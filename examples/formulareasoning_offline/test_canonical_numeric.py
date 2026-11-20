"""Invented unitless fixtures only; these checks are not benchmark scores."""
from copy import deepcopy
import socket
import sys
import unittest
from canonical_numeric import (
    BOTTOM, ZERO, GridConfig, Label, canonicalize_answer, canonicalize_numeric,
)


class CanonicalChecks(unittest.TestCase):
    def setUp(self):
        self.config = GridConfig(-6, 9)

    def value(self, token):
        return canonicalize_numeric(token, self.config)

    def test_exact_decimal_and_rational_agree(self):
        self.assertEqual(self.value("1/8").label, self.value("0.125").label)
        self.assertEqual(self.value("1/3").label, Label("finite", 1, 333333, -1))

    def test_half_even_ties(self):
        self.assertEqual(self.value("1.234565").label, Label("finite", 1, 123456, 0))
        self.assertEqual(self.value("1.234575").label, Label("finite", 1, 123458, 0))
        self.assertEqual(self.value("-1.234565").label, Label("finite", -1, 123456, 0))

    def test_rounding_carry_before_range_check(self):
        self.assertEqual(self.value("9.999995").label, Label("finite", 1, 100000, 1))
        self.assertEqual(self.value("9.999995e9").reason, "rounded_exponent_out_of_range")

    def test_range_boundaries(self):
        self.assertEqual(self.value("1e-6").label.kind, "finite")
        self.assertEqual(self.value("1e9").label.kind, "finite")
        for token in ("1e-7", "1e10"):
            with self.subTest(token=token):
                self.assertEqual(self.value(token).label, BOTTOM)

    def test_zero_has_single_label(self):
        for token in ("0", "-0", "+0.000", "0e9999", "0/-7"):
            with self.subTest(token=token):
                self.assertEqual(self.value(token).label, ZERO)

    def test_units_expressions_and_nonfinite_rejected(self):
        for token in ("3 kg", "3%", "1+2", "NaN", "Infinity", "1,000", "1 or 2", ""):
            with self.subTest(token=token):
                self.assertEqual(self.value(token).label, BOTTOM)

    def test_float_bool_and_none_rejected(self):
        for token in (1.25, True, None):
            with self.subTest(token=token):
                self.assertEqual(self.value(token).reason, "exact_string_required")

    def test_parser_bounds_and_zero_denominator(self):
        self.assertEqual(self.value("1/0").reason, "zero_denominator")
        self.assertEqual(self.value("1e10001").reason, "literal_exponent_limit")
        self.assertEqual(self.value("1" * 4097).reason, "input_length_limit")

    def test_answer_schema_is_exact(self):
        for raw in ({"answer": "1", "other": "2"}, ["1"], {}, "1"):
            with self.subTest(raw=raw):
                self.assertEqual(canonicalize_answer(raw, self.config).label, BOTTOM)
        self.assertEqual(canonicalize_answer(None, self.config).reason, "no_answer")

    def test_input_not_mutated(self):
        raw = {"answer": " 0.125 "}
        saved = deepcopy(raw)
        self.assertEqual(canonicalize_answer(raw, self.config).label, self.value("1/8").label)
        self.assertEqual(raw, saved)

    def test_global_grid_config_validation_and_size(self):
        self.assertEqual(self.config.alphabet_size, 28_800_002)
        for args in ((True, 9), (-6, 1.5), (9, -6), (-10001, 9)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                GridConfig(*args)

    def test_generated_finite_labels_round_trip(self):
        # Exact strings, no float conversion and no numerical acceptance tolerance.
        for numerator in range(-100, 101):
            label = self.value(f"{numerator}/7").label
            if label.kind == "zero":
                text = "0"
            else:
                text = f"{label.sign * label.coefficient}e{label.exponent - 5}"
            self.assertEqual(self.value(text).label, label)

    def test_bottom_is_invalid_not_a_correct_answer(self):
        # Two invalid parses share bottom. Never count that equality as correctness.
        for token in ("malformed", "also malformed"):
            self.assertEqual(self.value(token).label.kind, "bottom")
            self.assertIsNotNone(self.value(token).reason)

    def test_demo_blocks_network_before_socket_creation(self):
        # The entry point installs this audit tripwire. Direct unittest is not the demo.
        with self.assertRaisesRegex(PermissionError, "contributor demo"):
            socket.socket()

    def test_demo_blocks_child_process_audit_event(self):
        # Test the audit event without launching any child, even if the guard regresses.
        with self.assertRaisesRegex(PermissionError, "contributor demo"):
            sys.audit("subprocess.Popen", "not-executed", [], None, None)
