"""
Task Automation Agent - Custom Evaluators

This module defines custom evaluators for the Task Automation Agent.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from pydantic_evals.evaluators import Evaluator, EvaluatorContext
from pydantic_evals.otel.span_tree import SpanTree

from src.evals.models import TaskInput, TaskOutput, TaskMetadata

@dataclass
class SuccessEvaluator(Evaluator[TaskInput, TaskOutput]):
    """
    Evaluator that checks if the task was completed successfully.

    This evaluator simply checks the 'success' field in the output.
    """

    def evaluate(self, ctx: EvaluatorContext[TaskInput, TaskOutput]) -> float:
        """
        Evaluate if the task was completed successfully.

        Args:
            ctx: The evaluator context containing input, output, and expected output

        Returns:
            1.0 if the task was successful, 0.0 otherwise
        """
        if ctx.output and ctx.output.success:
            return 1.0
        return 0.0

@dataclass
class ToolUsageEvaluator(Evaluator[TaskInput, TaskOutput]):
    """
    Evaluator that checks if the expected tools were used.

    This evaluator uses the span tree to check if the expected tools were called.
    """

    def evaluate(self, ctx: EvaluatorContext[TaskInput, TaskOutput]) -> float:
        """
        Evaluate if the expected tools were used.

        Args:
            ctx: The evaluator context containing input, output, and expected output

        Returns:
            Score between 0.0 and 1.0 representing the tool usage
        """
        # Get the span tree from the context
        span_tree = ctx.span_tree
        if not span_tree:
            return 0.0

        # Get the expected tools from the metadata
        expected_tools = ctx.metadata.expected_tools if ctx.metadata else []
        if not expected_tools:
            return 1.0

        # Check if each expected tool was used
        used_tools = []

        for tool in expected_tools:
            # Find spans with the tool name
            tool_spans = span_tree.find(lambda node: tool.lower() in node.name.lower())
            if tool_spans:
                used_tools.append(tool)

        # Calculate the tool usage score
        if not expected_tools:
            tool_usage_score = 1.0
        else:
            tool_usage_score = len(used_tools) / len(expected_tools)

        return tool_usage_score

@dataclass
class PerformanceEvaluator(Evaluator[TaskInput, TaskOutput]):
    """
    Evaluator that checks the performance of the task execution.

    This evaluator uses the span tree to measure the execution time and
    compares it to the expected timeout.
    """

    def evaluate(self, ctx: EvaluatorContext[TaskInput, TaskOutput]) -> float:
        """
        Evaluate the performance of the task execution.

        Args:
            ctx: The evaluator context containing input, output, and expected output

        Returns:
            Score between 0.0 and 1.0 representing the performance
        """
        # Get the span tree from the context
        span_tree = ctx.span_tree
        if not span_tree:
            return 0.0

        # Get the timeout from the metadata
        timeout_seconds = ctx.metadata.timeout_seconds if ctx.metadata else 60

        # Get the root span duration
        if not span_tree.roots:
            return 0.0

        root_span = span_tree.roots[0]
        if not root_span:
            return 0.0

        duration_seconds = root_span.duration.total_seconds()

        # Calculate the performance score (1.0 if within timeout, decreasing as it approaches timeout)
        if duration_seconds <= timeout_seconds:
            # Linear score from 0.5 to 1.0 based on how much of the timeout was used
            performance_score = 1.0 - (0.5 * duration_seconds / timeout_seconds)
        else:
            # If exceeded timeout, score from 0.0 to 0.5 based on how much it exceeded
            # Score approaches 0 as duration approaches 2x timeout
            overage_factor = min((duration_seconds - timeout_seconds) / timeout_seconds, 1.0)
            performance_score = 0.5 * (1.0 - overage_factor)

        return performance_score

@dataclass
class LLMResultEvaluator(Evaluator[TaskInput, TaskOutput]):
    """
    Evaluator that uses an LLM to judge the quality of the task result.

    This evaluator uses the LLMJudge to evaluate the quality of the task result.
    """

    def __init__(self, model: str = "openai:gpt-4o"):
        """
        Initialize the LLMResultEvaluator.

        Args:
            model: The model to use for evaluation
        """
        self.model = model

    async def evaluate(self, ctx: EvaluatorContext[TaskInput, TaskOutput]) -> float:
        """
        Evaluate the quality of the task result using an LLM.

        Args:
            ctx: The evaluator context containing input, output, and expected output

        Returns:
            Score between 0.0 and 1.0 representing the quality of the result
        """
        from pydantic_evals.evaluators import LLMJudge

        # Create an LLMJudge with a custom rubric
        judge = LLMJudge(
            rubric=f"""
            Evaluate the quality of the task automation result based on the following criteria:
            1. Does the result address the task described in the input?
            2. Are the steps taken logical and appropriate for the task?
            3. Is the result clear and understandable?

            Task description: {ctx.inputs.task_description}
            """,
            model=self.model,
            include_input=True
        )

        # Evaluate using the LLMJudge
        score = await judge.evaluate(ctx)
        return score
