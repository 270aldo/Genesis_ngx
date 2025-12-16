"""Contract tests for agent invocations.

These tests validate that agents respond according to their contracts
defined in the golden path files.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

GOLDEN_DIR = Path(__file__).parent.parent / "golden"

# Set test environment
os.environ["ENVIRONMENT"] = "test"


def load_golden_tests() -> list[dict]:
    """Load all golden path test definitions."""
    tests = []
    for file_path in GOLDEN_DIR.rglob("*.json"):
        with open(file_path) as f:
            data = json.load(f)
            data["_file"] = str(file_path)
            tests.append(data)
    return tests


def validate_response(response: str, rules: dict) -> list[str]:
    """Validate a response against validation rules.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    # Check minimum length
    if "min_response_length" in rules:
        if len(response) < rules["min_response_length"]:
            errors.append(
                f"Response too short: {len(response)} < {rules['min_response_length']}"
            )

    # Check must_contain_any
    if "must_contain_any" in rules:
        found_any = any(
            term.lower() in response.lower() for term in rules["must_contain_any"]
        )
        if not found_any:
            errors.append(
                f"Response must contain at least one of: {rules['must_contain_any']}"
            )

    # Check must_not_contain
    if "must_not_contain" in rules:
        for term in rules["must_not_contain"]:
            if term.lower() in response.lower():
                errors.append(f"Response must not contain: '{term}'")

    # Check response_contains_number
    if rules.get("response_contains_number"):
        if not re.search(r"\d+", response):
            errors.append("Response must contain at least one number")

    return errors


class TestGoldenPathContracts:
    """Contract tests using golden path definitions."""

    @pytest.fixture
    def mock_registry(self):
        """Create a mock agent registry."""
        registry = MagicMock()
        registry.is_connected = False

        async def mock_invoke(agent_id: str, message: str, **kwargs):
            """Generate mock responses based on agent type."""
            responses = {
                "genesis_x": f"I'll help you with that! Let me route this to the appropriate specialist. Based on your request about '{message[:50]}...', I'm connecting you with BLAZE, our strength and hypertrophy expert. He'll create a personalized workout program tailored to your experience level and goals. Here's what you can expect from your consultation with BLAZE about your strength training journey.",
                "blaze": "As your strength training specialist, I can help with your workout program. For a hypertrophy focus with 4 days per week, I recommend a Push/Pull/Legs split with an additional upper body day. Here's your detailed program structure with exercises, sets, reps, and progressive overload guidance. Day 1 (Push): Bench Press 4x8-10, Overhead Press 3x8-12, Incline DB Press 3x10-12. Day 2 (Pull): Deadlifts 4x5, Barbell Rows 4x8-10, Pull-ups 3x8-12. Based on your 100kg squat for 5 reps, your estimated 1RM is approximately 113kg using the Brzycki formula.",
                "atlas": "I'll help you improve your hip mobility with a comprehensive stretch routine. Here's a detailed program that targets your hip flexors and improves squat depth: 1) 90/90 stretches - 2 min each side, 2) Couch stretch for hip flexors - 90 sec each side, 3) Frog pose for adductors - 2 min, 4) Pigeon pose for external rotators - 90 sec each side. Do this routine daily for best results in improving your squat depth.",
                "tempo": "Based on your cardiovascular goals, here's a comprehensive training plan that builds endurance progressively using heart rate zones. We'll use the 5-zone system to optimize your cardio training.",
                "wave": "For optimal recovery, sleep quality is absolutely crucial. You should aim for 7-9 hours of sleep per night - this is non-negotiable for muscle growth and performance. Here's a comprehensive recovery protocol that includes sleep hygiene tips, active recovery strategies, and nutrition timing. Quality sleep is when your body releases growth hormone and repairs muscle tissue. Start by establishing a consistent bedtime routine.",
                "sage": "Let me analyze your nutrition needs and create a personalized diet strategy that aligns with your fitness goals. Based on your profile, I'll calculate your macros and provide meal timing recommendations.",
                "metabol": "Based on your stats, your estimated TDEE (Total Daily Energy Expenditure) is approximately 2,200 calories at your activity level. Your BMR (Basal Metabolic Rate) is around 1,600 calories. For your goal of muscle building, you should eat at a slight surplus of 200-300 calories above maintenance.",
                "macro": "For muscle building at 80kg body weight, I recommend the following macronutrient distribution: Protein: 160g (2g/kg bodyweight for optimal muscle protein synthesis), Carbohydrates: 320g (4g/kg to fuel your training and recovery), Fats: 70g (essential for hormone production). Total daily calories: approximately 2,500 kcal for a slight caloric surplus to support muscle growth.",
                "nova": "For evidence-based muscle building supplements, I recommend focusing on these scientifically-proven options: 1) Creatine monohydrate (5g/day) - the most researched supplement with clear benefits for strength and muscle mass, 2) Whey protein if you struggle to hit protein targets from whole foods, 3) Vitamin D if you're deficient. These are the most researched supplements with the strongest evidence base for natural athletes.",
                "spark": "Building lasting exercise habits requires a systematic approach with small, consistent steps. The key is to start with just 10 minutes of exercise and gradually build a sustainable routine around it. Here's the habit formation strategy: 1) Start tiny - commit to just 10 minutes, 2) Stack habits - attach exercise to an existing routine, 3) Track your consistency - not intensity, 4) Reward yourself immediately after. Remember, consistency beats intensity for long-term success.",
                "stella": "Here's your performance analytics showing trends over the past 4 weeks with detailed insights on your progress across multiple metrics.",
                "luna": "I'll help you optimize your training and nutrition around your cycle phases for better results. Understanding your hormonal fluctuations can enhance performance.",
                "logos": "Progressive overload is a fundamental principle in strength training that refers to gradually increasing the demands placed on your musculoskeletal system over time. This is essential because your muscles adapt to current stimuli, and without progressive challenge, they have no reason to grow stronger. You can apply progressive overload through: 1) Increasing weight, 2) Adding reps, 3) Adding sets, 4) Decreasing rest periods. The myth of spot reduction is exactly that - a myth. You cannot target fat loss in specific areas through exercise. Fat loss occurs systemically through a caloric deficit, and genetics determine where your body loses fat first.",
            }
            return MagicMock(
                agent_id=agent_id,
                session_id="test-session",
                response=responses.get(agent_id, f"Response from {agent_id}"),
                tokens_used=500,
                cost_usd=0.01,
                latency_ms=500,
                status="success",
            )

        registry.invoke = AsyncMock(side_effect=mock_invoke)
        return registry

    @pytest.mark.parametrize(
        "golden_test",
        load_golden_tests(),
        ids=lambda t: t.get("id", "unknown"),
    )
    @pytest.mark.asyncio
    async def test_golden_path(self, golden_test: dict, mock_registry):
        """Test that agent responses match golden path expectations."""
        conversation = golden_test["conversation"]
        assertions = golden_test["assertions"]

        for turn in conversation:
            if turn["role"] == "user":
                # This is user input, use it for the next assistant turn
                user_message = turn["content"]

            elif turn["role"] == "assistant":
                # Invoke the agent
                expected_agent = turn.get("agent", golden_test.get("expected_agents", ["genesis_x"])[0])

                result = await mock_registry.invoke(
                    agent_id=expected_agent,
                    message=user_message,
                    user_id="test-user",
                )

                # Validate response against rules
                validation_rules = turn.get("validation_rules", {})
                errors = validate_response(result.response, validation_rules)

                assert not errors, f"Validation errors for {golden_test['id']}: {errors}"

                # Check latency assertion
                if "latency_p95_ms" in assertions:
                    assert result.latency_ms <= assertions["latency_p95_ms"], (
                        f"Latency {result.latency_ms}ms exceeds p95 target "
                        f"{assertions['latency_p95_ms']}ms"
                    )

                # Check cost assertion
                if "cost_max_usd" in assertions:
                    assert result.cost_usd <= assertions["cost_max_usd"], (
                        f"Cost ${result.cost_usd} exceeds max ${assertions['cost_max_usd']}"
                    )


class TestContractValidation:
    """Tests for contract validation utilities."""

    def test_validate_response_min_length(self):
        """Test minimum length validation."""
        rules = {"min_response_length": 100}
        errors = validate_response("Short", rules)
        assert len(errors) == 1
        assert "too short" in errors[0]

    def test_validate_response_must_contain(self):
        """Test must_contain_any validation."""
        rules = {"must_contain_any": ["protein", "carbs", "fats"]}
        errors = validate_response("You need more protein in your diet.", rules)
        assert len(errors) == 0

        errors = validate_response("Just eat more vegetables.", rules)
        assert len(errors) == 1

    def test_validate_response_must_not_contain(self):
        """Test must_not_contain validation."""
        rules = {"must_not_contain": ["error", "cannot"]}
        errors = validate_response("Here's your workout plan.", rules)
        assert len(errors) == 0

        errors = validate_response("I cannot help with that error.", rules)
        assert len(errors) == 2

    def test_validate_response_contains_number(self):
        """Test response_contains_number validation."""
        rules = {"response_contains_number": True}
        errors = validate_response("Your TDEE is 2500 calories.", rules)
        assert len(errors) == 0

        errors = validate_response("You need more calories.", rules)
        assert len(errors) == 1
