"""Core components of the KG-Agent framework.

This module contains skeleton implementations for:
- Agent: orchestrates the reasoning loop
- ToolBox: container for tools the agent can call
- KGExecutor: lightweight interface to query/execute operations on a KG
- KnowledgeMemory: stores intermediate reasoning steps

All methods contain TODO markers and simple mock behavior suitable for unit tests and extension.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Tool(Protocol):
    """Protocol for toolbox tools.

    Concrete tools should implement execute which takes a string instruction and optional context.
    """

    def execute(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Any:
        ...


@dataclass()
class KnowledgeMemory:
    """Simple memory to store intermediate reasoning steps.

    Attributes:
        steps: list of recorded steps (strings or structured objects)
    """

    steps: List[Dict[str, Any]] = field(default_factory=list)

    def add_step(self, step_type: str, content: Any) -> None:
        """Add a new step to memory.

        Args:
            step_type: type identifier for the step (e.g., 'query', 'tool_call', 'observation')
            content: payload (str or structured data)
        """
        logger.debug("Adding memory step: %s", step_type)
        self.steps.append({"type": step_type, "content": content})

    def last(self, n: int = 1) -> List[Dict[str, Any]]:
        """Return last n memory entries."""
        if n <= 0:
            return []
        return self.steps[-n:]


class KGExecutor:
    """Lightweight executor to interact with a Knowledge Graph.

    This is a placeholder for actual KG access. Implementers can replace the internal storage
    with RDFLib, a database connection, or a custom KG API.
    """

    def __init__(self) -> None:
        # simple in-memory representation: list of triples
        self.triples: List[Tuple[Any, Any, Any]] = []

    def load_triples(self, triples: List[Tuple[Any, Any, Any]]) -> None:
        """Load triples into the executor.

        Args:
            triples: list of (subject, predicate, object) tuples
        """
        logger.info("Loading %d triples into KGExecutor", len(triples))
        self.triples.extend(triples)

    def query(self, pattern: Tuple[Optional[Any], Optional[Any], Optional[Any]]) -> List[Tuple[Any, Any, Any]]:
        """Query triples by pattern where elements can be None as wildcard.

        Args:
            pattern: (s, p, o) with optional None wildcard

        Returns:
            Matching triples list
        """
        s_pat, p_pat, o_pat = pattern
        results = [t for t in self.triples if
                   (s_pat is None or t[0] == s_pat) and
                   (p_pat is None or t[1] == p_pat) and
                   (o_pat is None or t[2] == o_pat)]
        logger.debug("Query %s -> %d results", pattern, len(results))
        return results

    def execute_program(self, program: str) -> Any:
        """Execute a small program (string) over the KG.

        The paper suggests using program language to formulate multi-hop reasoning. Here we
        provide a placeholder that should be replaced by a proper parser and executor.
        """
        logger.info("Executing program on KG (placeholder): %s", program)
        # TODO: Implement a proper program parser/executor that maps program constructs
        # to KG queries and reasoning steps.
        return {"result": None, "note": "execute_program is a placeholder"}


class ToolBox:
    """Registry and dispatcher for tools the agent can call.

    Tools are simply callables/objects that implement the Tool protocol.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, tool: Tool) -> None:
        """Register a tool under a name."""
        logger.info("Registering tool: %s", name)
        self._tools[name] = tool

    def call(self, name: str, instruction: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Call a tool by name.

        Raises:
            KeyError: if tool not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool {name} not found in toolbox")
        logger.debug("Calling tool %s with instruction: %s", name, instruction)
        return self._tools[name].execute(instruction, context=context)


class Agent:
    """Autonomous agent that orchestrates reasoning over a KG.

    The agent maintains a loop: observe -> decide tool -> call tool -> update memory -> repeat.
    LLM integration and tool selection logic should be implemented by the user.
    """

    def __init__(self, llm: Any = None, toolbox: Optional[ToolBox] = None, kg_executor: Optional[KGExecutor] = None) -> None:
        """Initialize the Agent.

        Args:
            llm: language model interface (could be a HuggingFace pipeline or custom wrapper)
            toolbox: ToolBox instance
            kg_executor: KGExecutor instance
        """
        self.llm = llm
        self.toolbox = toolbox or ToolBox()
        self.kg = kg_executor or KGExecutor()
        self.memory = KnowledgeMemory()
        self.max_steps = 10

    def decide_tool(self, prompt: str) -> str:
        """Decide which tool to call based on prompt and memory.

        This is a placeholder decision function. In practice, it uses the LLM to select the tool
        and generate the instruction/program to run.
        """
        logger.debug("Deciding tool for prompt: %s", prompt)
        # TODO: Integrate LLM to make tool selection and program generation
        # For demonstration return a default tool name if exists
        available = list(self.toolbox._tools.keys())
        return available[0] if available else "kg_query"

    def run(self, query: str) -> Any:
        """Run the agent loop to answer a complex query over the KG.

        Args:
            query: user question to be answered

        Returns:
            Final answer object (placeholder)
        """
        logger.info("Agent started for query: %s", query)
        self.memory.add_step("query", query)
        step = 0
        result = None
        while step < self.max_steps:
            logger.info("Agent step %d", step)
            tool_name = self.decide_tool(query)
            instruction = f"Perform operation for: {query} (step {step})"
            # If LLM was available, instruction would be generated by it
            try:
                out = self.toolbox.call(tool_name, instruction, context={"memory": self.memory.steps})
            except KeyError:
                logger.warning("Tool %s not found, stopping.", tool_name)
                break
            self.memory.add_step("tool_call", {"tool": tool_name, "out": out})
            # Simple termination condition: if tool returned a final answer
            if isinstance(out, dict) and out.get("final", False):
                result = out
                logger.info("Agent obtained final result at step %d", step)
                break
            step += 1
        logger.info("Agent finished after %d steps", step)
        return result


# Example concrete tool implementations (lightweight)

class KGQueryTool:
    """Tool that queries the KGExecutor with a simple pattern string.

    The `instruction` is expected to be a string that contains an s,p,o triple or a
    small query language. This is a placeholder to be replaced by a robust tool.
    """

    def __init__(self, kg_executor: KGExecutor) -> None:
        self.kg = kg_executor

    def execute(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Any:
        logger.debug("KGQueryTool received instruction: %s", instruction)
        # TODO: parse instruction into triple pattern; here we return all triples
        results = self.kg.query((None, None, None))
        # Example of a returning structure; `final` indicates completion
        return {"results": results, "final": False}


class FinalAnswerTool:
    """Tool that collects memory and synthesizes a final answer (placeholder).

    In practice: uses LLM to synthesize an answer from memory records.
    """

    def __init__(self, llm: Any = None) -> None:
        self.llm = llm

    def execute(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Any:
        logger.debug("FinalAnswerTool generating answer from memory")
        memory = (context or {}).get("memory", [])
        # TODO: call LLM to synthesize final answer from memory
        synthesized = f"SYNTHESIZED_ANSWER based on {len(memory)} steps"
        return {"answer": synthesized, "final": True}
