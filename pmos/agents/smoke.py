"""SmokeAgent — one-sub-task LLM agent. Proves the full call path:
template → SHA capture → assembly → adapter → response → state + telemetry.

Use this as the smoke test for the LLM stack when wiring up a new model
adapter or making changes to LLMAgent. Not a real production agent.
"""

from __future__ import annotations

from pmos.agents.llm import LLMAgent
from pmos.prompts import PromptComponents
from pmos.state import AgentRunState


class SmokeAgent(LLMAgent):
    name = "smoke"

    def sub_tasks(self):
        return [("ping", self._ping)]

    def _ping(self, state: AgentRunState) -> dict:
        response = self._call_template(
            state,
            "ping",
            PromptComponents(
                project_context=state.inputs.get("project_context", ""),
            ),
        )
        return {
            "text": response.text,
            "tokens_in": response.tokens_in,
            "tokens_out": response.tokens_out,
            "model": response.model,
        }
