from app.services.llm import build_prompt
from app.models import RetrievedChunk


def test_prompt_contains_question_and_sources():
    chunks = [RetrievedChunk("policy.txt", 1, 0.9, "Employees need manager approval.")]
    prompt = build_prompt("Who approves purchases?", chunks)
    assert "Who approves purchases?" in prompt
    assert "policy.txt" in prompt
