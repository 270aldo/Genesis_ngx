"""Tests for JSON schema validation.

Validates that:
1. Request/response schemas are valid JSON Schema
2. Example payloads in schemas are valid
3. Golden path test files conform to expected structure
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Try to import jsonschema, skip tests if not available
try:
    import jsonschema
    from jsonschema import Draft7Validator

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"
GOLDEN_DIR = Path(__file__).parent.parent / "golden"


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestInvokeRequestSchema:
    """Tests for invoke_request.schema.json."""

    @pytest.fixture
    def schema(self) -> dict:
        """Load the request schema."""
        schema_path = SCHEMAS_DIR / "invoke_request.schema.json"
        with open(schema_path) as f:
            return json.load(f)

    def test_schema_is_valid(self, schema):
        """Test that the schema itself is valid JSON Schema."""
        Draft7Validator.check_schema(schema)

    def test_examples_are_valid(self, schema):
        """Test that all examples in the schema are valid."""
        validator = Draft7Validator(schema)
        for i, example in enumerate(schema.get("examples", [])):
            errors = list(validator.iter_errors(example))
            assert not errors, f"Example {i} has errors: {errors}"

    def test_minimal_request_valid(self, schema):
        """Test that a minimal valid request passes."""
        validator = Draft7Validator(schema)
        minimal = {
            "agent_id": "genesis_x",
            "message": "Hello",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
        }
        errors = list(validator.iter_errors(minimal))
        assert not errors

    def test_invalid_agent_rejected(self, schema):
        """Test that invalid agent_id is rejected."""
        validator = Draft7Validator(schema)
        invalid = {
            "agent_id": "invalid_agent",
            "message": "Hello",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
        }
        errors = list(validator.iter_errors(invalid))
        assert len(errors) > 0

    def test_empty_message_rejected(self, schema):
        """Test that empty message is rejected."""
        validator = Draft7Validator(schema)
        invalid = {
            "agent_id": "genesis_x",
            "message": "",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
        }
        errors = list(validator.iter_errors(invalid))
        assert len(errors) > 0


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestInvokeResponseSchema:
    """Tests for invoke_response.schema.json."""

    @pytest.fixture
    def schema(self) -> dict:
        """Load the response schema."""
        schema_path = SCHEMAS_DIR / "invoke_response.schema.json"
        with open(schema_path) as f:
            return json.load(f)

    def test_schema_is_valid(self, schema):
        """Test that the schema itself is valid JSON Schema."""
        Draft7Validator.check_schema(schema)

    def test_examples_are_valid(self, schema):
        """Test that all examples in the schema are valid."""
        validator = Draft7Validator(schema)
        for i, example in enumerate(schema.get("examples", [])):
            errors = list(validator.iter_errors(example))
            assert not errors, f"Example {i} has errors: {errors}"

    def test_success_response_valid(self, schema):
        """Test that a success response passes."""
        validator = Draft7Validator(schema)
        response = {
            "agent_id": "blaze",
            "session_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "response": "Here's your workout plan...",
            "status": "success",
        }
        errors = list(validator.iter_errors(response))
        assert not errors

    def test_error_response_valid(self, schema):
        """Test that an error response passes."""
        validator = Draft7Validator(schema)
        response = {
            "agent_id": "genesis_x",
            "session_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "response": "An error occurred",
            "status": "error",
            "error": {
                "code": -32000,
                "message": "Agent unavailable",
            },
        }
        errors = list(validator.iter_errors(response))
        assert not errors


@pytest.mark.skipif(not HAS_JSONSCHEMA, reason="jsonschema not installed")
class TestGoldenPathFiles:
    """Tests for golden path test file structure."""

    def get_golden_files(self) -> list[Path]:
        """Get all golden path JSON files."""
        return list(GOLDEN_DIR.rglob("*.json"))

    def test_golden_files_exist(self):
        """Test that golden path files exist."""
        files = self.get_golden_files()
        assert len(files) >= 5, f"Expected at least 5 golden files, found {len(files)}"

    def test_golden_files_valid_json(self):
        """Test that all golden files are valid JSON."""
        for file_path in self.get_golden_files():
            with open(file_path) as f:
                try:
                    data = json.load(f)
                    assert "id" in data, f"{file_path} missing 'id'"
                    assert "conversation" in data, f"{file_path} missing 'conversation'"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {file_path}: {e}")

    def test_golden_files_have_required_fields(self):
        """Test that golden files have required fields."""
        required_fields = ["id", "name", "domain", "conversation", "assertions"]
        for file_path in self.get_golden_files():
            with open(file_path) as f:
                data = json.load(f)
                for field in required_fields:
                    assert field in data, f"{file_path} missing required field '{field}'"

    def test_golden_conversations_have_structure(self):
        """Test that conversations have proper structure."""
        for file_path in self.get_golden_files():
            with open(file_path) as f:
                data = json.load(f)
                conversation = data["conversation"]
                assert len(conversation) >= 1, f"{file_path} has empty conversation"

                for i, turn in enumerate(conversation):
                    assert "role" in turn, f"{file_path} turn {i} missing 'role'"
                    assert turn["role"] in ["user", "assistant", "system"]
                    assert "content" in turn or "expected_behavior" in turn
