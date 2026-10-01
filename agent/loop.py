"""Agent main loop: reason → act → observe, until the LLM says we're done."""
from __future__ import annotations
from .schemas import AgentStep
from .llm import LLMProvider


class AgentLoop:
    def __init__(self, llm: LLMProvider, tools: dict, max_steps: int = 10,
                 verbose: bool = True):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.verbose = verbose
        self.steps: list[AgentStep] = []
        self.context: dict = {}

    def run(self, goal: str) -> dict:
        if self.verbose:
            print(f"[AGENT] goal: {goal}  (planner: {self.llm.name})\n")
        final = None
        for i in range(self.max_steps):
            decision = self.llm.decide_next(
                goal, self.steps, self.context, list(self.tools))
            if decision.get("final"):
                final = decision["final"]
                if self.verbose:
                    print("── done ────────────────────────────────")
                    print(f"FINAL: {final}\n")
                break
            thought = decision["thought"]
            tool_name = decision["tool"]
            args = dict(decision.get("args", {}))
            tool = self.tools[tool_name]
            result = tool.run(context=self.context, **args)
            self.context.update(result.get("context_updates", {}))
            step = AgentStep(
                thought=thought,
                action_tool=tool_name,
                action_args=args,
                observation=result.get("summary", ""),
                simulated=True,
            )
            self.steps.append(step)
            if self.verbose:
                self._print_step(i + 1, step)
        return {"steps": self.steps, "context": self.context, "final": final}

    @staticmethod
    def _print_step(n: int, step: AgentStep) -> None:
        print(f"── Step {n} ──────────────────────────────")
        print(f"THOUGHT: {step.thought}")
        arg_str = ", ".join(f"{k}={v!r}" for k, v in step.action_args.items())
        print(f"ACTION: {step.action_tool}({arg_str})")
        print(f"OBSERVATION: {step.observation}\n")
