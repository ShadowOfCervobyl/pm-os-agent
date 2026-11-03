"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict and
whether the task brief carried an injection. It runs at temperature 0 so the same draft
gets the same verdict. The revision cap and the checks that act on the verdict live in
`agent.py`.
"""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM


def review(client, model: str, proposed_output: str, source_data: str) -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output."""
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
        ],
        # json_schema, not json_object: Anthropic's OpenAI-compatible endpoint rejects json_object.
        response_format={"type": "json_schema", "json_schema": {
            "name": "verdict", "strict": True, "schema": {
                "type": "object",
                "properties": {"verdict": {"type": "string", "enum": ["pass", "fail"]},
                               "reasons": {"type": "array", "items": {"type": "string"}},
                               "injection_in_task": {"type": "boolean"}},
                "required": ["verdict", "reasons", "injection_in_task"],
                "additionalProperties": False}}},
    )
    usage = resp.usage
    try:
        verdict = json.loads(resp.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"],
                   "injection_in_task": False}
    verdict["_usage"] = {"prompt": usage.prompt_tokens, "completion": usage.completion_tokens}
    return verdict
