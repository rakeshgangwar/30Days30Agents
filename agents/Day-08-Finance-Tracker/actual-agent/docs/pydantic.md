# PydanticAI

> Agent Framework / shim to use Pydantic with LLMs

PydanticAI is a Python agent framework designed to make it less painful to build production grade
applications with Generative AI.

# Concepts documentation

## Introduction

Agents are PydanticAI's primary interface for interacting with LLMs.

In some use cases a single Agent will control an entire application or component, but multiple agents can also interact to embody more complex workflows.

The Agent class has full API documentation, but conceptually you can think of an agent as a container for:

| **Component** | **Description** | | --- | --- | | [System prompt(s)](#system-prompts) | A set of instructions for the LLM written by the developer. | | [Function tool(s)](../tools/) | Functions that the LLM may call to get information while generating a response. | | [Structured output type](../output/) | The structured datatype the LLM must return at the end of a run, if specified. | | [Dependency type constraint](../dependencies/) | System prompt functions, tools, and output validators may all use dependencies when they're run. | | [LLM model](../api/models/base/) | Optional default LLM model associated with the agent. Can also be specified when running the agent. | | [Model Settings](#additional-configuration) | Optional default model settings to help fine tune requests. Can also be specified when running the agent. |

In typing terms, agents are generic in their dependency and output types, e.g., an agent which required dependencies of type `Foobar` and produced outputs of type `list[str]` would have type `Agent[Foobar, list[str]]`. In practice, you shouldn't need to care about this, it should just mean your IDE can tell you when you have the right type, and if you choose to use [static type checking](#static-type-checking) it should work well with PydanticAI.

Here's a toy example of an agent that simulates a roulette wheel:

roulette_wheel.py

```python
from pydantic_ai import Agent, RunContext

roulette_agent = Agent(  # (1)!
    'openai:gpt-4o',
    deps_type=int,
    output_type=bool,
    system_prompt=(
        'Use the `roulette_wheel` function to see if the '
        'customer has won based on the number they provide.'
    ),
)


@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str:  # (2)!
    """check if the square is a winner"""
    return 'winner' if square == ctx.deps else 'loser'


# Run the agent
success_number = 18  # (3)!
result = roulette_agent.run_sync('Put my money on square eighteen', deps=success_number)
print(result.output)  # (4)!
#> True

result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.output)
#> False

```

1. Create an agent, which expects an integer dependency and produces a boolean output. This agent will have type `Agent[int, bool]`.
1. Define a tool that checks if the square is a winner. Here RunContext is parameterized with the dependency type `int`; if you got the dependency type wrong you'd get a typing error.
1. In reality, you might want to use a random number here e.g. `random.randint(0, 36)`.
1. `result.output` will be a boolean indicating if the square is a winner. Pydantic performs the output validation, and it'll be typed as a `bool` since its type is derived from the `output_type` generic parameter of the agent.

Agents are designed for reuse, like FastAPI Apps

Agents are intended to be instantiated once (frequently as module globals) and reused throughout your application, similar to a small FastAPI app or an APIRouter.

## Running Agents

There are four ways to run an agent:

1. agent.run() â€” a coroutine which returns a RunResult containing a completed response.
1. agent.run_sync() â€” a plain, synchronous function which returns a RunResult containing a completed response (internally, this just calls `loop.run_until_complete(self.run())`).
1. agent.run_stream() â€” a coroutine which returns a StreamedRunResult, which contains methods to stream a response as an async iterable.
1. agent.iter() â€” a context manager which returns an AgentRun, an async-iterable over the nodes of the agent's underlying Graph.

Here's a simple example demonstrating the first three:

run_agent.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.output)
#> Rome


async def main():
    result = await agent.run('What is the capital of France?')
    print(result.output)
    #> Paris

    async with agent.run_stream('What is the capital of the UK?') as response:
        print(await response.get_output())
        #> London

```

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

You can also pass messages from previous runs to continue a conversation or provide context, as described in [Messages and Chat History](../message-history/).

### Iterating Over an Agent's Graph

Under the hood, each `Agent` in PydanticAI uses **pydantic-graph** to manage its execution flow. **pydantic-graph** is a generic, type-centric library for building and running finite state machines in Python. It doesn't actually depend on PydanticAI â€” you can use it standalone for workflows that have nothing to do with GenAI â€” but PydanticAI makes use of it to orchestrate the handling of model requests and model responses in an agent's run.

In many scenarios, you don't need to worry about pydantic-graph at all; calling `agent.run(...)` simply traverses the underlying graph from start to finish. However, if you need deeper insight or control â€” for example to capture each tool invocation, or to inject your own logic at specific stages â€” PydanticAI exposes the lower-level iteration process via Agent.iter. This method returns an AgentRun, which you can async-iterate over, or manually drive node-by-node via the next method. Once the agent's graph returns an End, you have the final result along with a detailed history of all steps.

#### `async for` iteration

Here's an example of using `async for` with `iter` to record each node the agent executes:

agent_iter_async_for.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')


async def main():
    nodes = []
    # Begin an AgentRun, which is an async-iterable over the nodes of the agent's graph
    async with agent.iter('What is the capital of France?') as agent_run:
        async for node in agent_run:
            # Each node represents a step in the agent's execution
            nodes.append(node)
    print(nodes)
    """
    [
        UserPromptNode(
            user_prompt='What is the capital of France?',
            instructions=None,
            instructions_functions=[],
            system_prompts=(),
            system_prompt_functions=[],
            system_prompt_dynamic_functions={},
        ),
        ModelRequestNode(
            request=ModelRequest(
                parts=[
                    UserPromptPart(
                        content='What is the capital of France?',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    )
                ],
                instructions=None,
                kind='request',
            )
        ),
        CallToolsNode(
            model_response=ModelResponse(
                parts=[TextPart(content='Paris', part_kind='text')],
                usage=Usage(
                    requests=1,
                    request_tokens=56,
                    response_tokens=1,
                    total_tokens=57,
                    details=None,
                ),
                model_name='gpt-4o',
                timestamp=datetime.datetime(...),
                kind='response',
            )
        ),
        End(data=FinalResult(output='Paris', tool_name=None, tool_call_id=None)),
    ]
    """
    print(agent_run.result.output)
    #> Paris

```

- The `AgentRun` is an async iterator that yields each node (`BaseNode` or `End`) in the flow.
- The run ends when an `End` node is returned.

#### Using `.next(...)` manually

You can also drive the iteration manually by passing the node you want to run next to the `AgentRun.next(...)` method. This allows you to inspect or modify the node before it executes or skip nodes based on your own logic, and to catch errors in `next()` more easily:

agent_iter_next.py

```python
from pydantic_ai import Agent
from pydantic_graph import End

agent = Agent('openai:gpt-4o')


async def main():
    async with agent.iter('What is the capital of France?') as agent_run:
        node = agent_run.next_node  # (1)!

        all_nodes = [node]

        # Drive the iteration manually:
        while not isinstance(node, End):  # (2)!
            node = await agent_run.next(node)  # (3)!
            all_nodes.append(node)  # (4)!

        print(all_nodes)
        """
        [
            UserPromptNode(
                user_prompt='What is the capital of France?',
                instructions=None,
                instructions_functions=[],
                system_prompts=(),
                system_prompt_functions=[],
                system_prompt_dynamic_functions={},
            ),
            ModelRequestNode(
                request=ModelRequest(
                    parts=[
                        UserPromptPart(
                            content='What is the capital of France?',
                            timestamp=datetime.datetime(...),
                            part_kind='user-prompt',
                        )
                    ],
                    instructions=None,
                    kind='request',
                )
            ),
            CallToolsNode(
                model_response=ModelResponse(
                    parts=[TextPart(content='Paris', part_kind='text')],
                    usage=Usage(
                        requests=1,
                        request_tokens=56,
                        response_tokens=1,
                        total_tokens=57,
                        details=None,
                    ),
                    model_name='gpt-4o',
                    timestamp=datetime.datetime(...),
                    kind='response',
                )
            ),
            End(data=FinalResult(output='Paris', tool_name=None, tool_call_id=None)),
        ]
        """

```

1. We start by grabbing the first node that will be run in the agent's graph.
1. The agent run is finished once an `End` node has been produced; instances of `End` cannot be passed to `next`.
1. When you call `await agent_run.next(node)`, it executes that node in the agent's graph, updates the run's history, and returns the *next* node to run.
1. You could also inspect or mutate the new `node` here as needed.

#### Accessing usage and the final output

You can retrieve usage statistics (tokens, requests, etc.) at any time from the AgentRun object via `agent_run.usage()`. This method returns a Usage object containing the usage data.

Once the run finishes, `agent_run.result` becomes a AgentRunResult object containing the final output (and related metadata).

______________________________________________________________________

### Streaming

Here is an example of streaming an agent run in combination with `async for` iteration:

streaming.py

```python
import asyncio
from dataclasses import dataclass
from datetime import date

from pydantic_ai import Agent
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPartDelta,
    ToolCallPartDelta,
)
from pydantic_ai.tools import RunContext


@dataclass
class WeatherService:
    async def get_forecast(self, location: str, forecast_date: date) -> str:
        # In real code: call weather API, DB queries, etc.
        return f'The forecast in {location} on {forecast_date} is 24Â°C and sunny.'

    async def get_historic_weather(self, location: str, forecast_date: date) -> str:
        # In real code: call a historical weather API or DB
        return (
            f'The weather in {location} on {forecast_date} was 18Â°C and partly cloudy.'
        )


weather_agent = Agent[WeatherService, str](
    'openai:gpt-4o',
    deps_type=WeatherService,
    output_type=str,  # We'll produce a final answer as plain text
    system_prompt='Providing a weather forecast at the locations the user provides.',
)


@weather_agent.tool
async def weather_forecast(
    ctx: RunContext[WeatherService],
    location: str,
    forecast_date: date,
) -> str:
    if forecast_date >= date.today():
        return await ctx.deps.get_forecast(location, forecast_date)
    else:
        return await ctx.deps.get_historic_weather(location, forecast_date)


output_messages: list[str] = []


async def main():
    user_prompt = 'What will the weather be like in Paris on Tuesday?'

    # Begin a node-by-node, streaming iteration
    async with weather_agent.iter(user_prompt, deps=WeatherService()) as run:
        async for node in run:
            if Agent.is_user_prompt_node(node):
                # A user prompt node => The user has provided input
                output_messages.append(f'=== UserPromptNode: {node.user_prompt} ===')
            elif Agent.is_model_request_node(node):
                # A model request node => We can stream tokens from the model's request
                output_messages.append(
                    '=== ModelRequestNode: streaming partial request tokens ==='
                )
                async with node.stream(run.ctx) as request_stream:
                    async for event in request_stream:
                        if isinstance(event, PartStartEvent):
                            output_messages.append(
                                f'[Request] Starting part {event.index}: {event.part!r}'
                            )
                        elif isinstance(event, PartDeltaEvent):
                            if isinstance(event.delta, TextPartDelta):
                                output_messages.append(
                                    f'[Request] Part {event.index} text delta: {event.delta.content_delta!r}'
                                )
                            elif isinstance(event.delta, ToolCallPartDelta):
                                output_messages.append(
                                    f'[Request] Part {event.index} args_delta={event.delta.args_delta}'
                                )
                        elif isinstance(event, FinalResultEvent):
                            output_messages.append(
                                f'[Result] The model produced a final output (tool_name={event.tool_name})'
                            )
            elif Agent.is_call_tools_node(node):
                # A handle-response node => The model returned some data, potentially calls a tool
                output_messages.append(
                    '=== CallToolsNode: streaming partial response & tool usage ==='
                )
                async with node.stream(run.ctx) as handle_stream:
                    async for event in handle_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            output_messages.append(
                                f'[Tools] The LLM calls tool={event.part.tool_name!r} with args={event.part.args} (tool_call_id={event.part.tool_call_id!r})'
                            )
                        elif isinstance(event, FunctionToolResultEvent):
                            output_messages.append(
                                f'[Tools] Tool call {event.tool_call_id!r} returned => {event.result.content}'
                            )
            elif Agent.is_end_node(node):
                assert run.result.output == node.data.output
                # Once an End node is reached, the agent run is complete
                output_messages.append(
                    f'=== Final Agent Output: {run.result.output} ==='
                )


if __name__ == '__main__':
    asyncio.run(main())

    print(output_messages)
    """
    [
        '=== UserPromptNode: What will the weather be like in Paris on Tuesday? ===',
        '=== ModelRequestNode: streaming partial request tokens ===',
        '[Request] Starting part 0: ToolCallPart(tool_name=\'weather_forecast\', args=\'{"location":"Pa\', tool_call_id=\'0001\', part_kind=\'tool-call\')',
        '[Request] Part 0 args_delta=ris","forecast_',
        '[Request] Part 0 args_delta=date":"2030-01-',
        '[Request] Part 0 args_delta=01"}',
        '=== CallToolsNode: streaming partial response & tool usage ===',
        '[Tools] The LLM calls tool=\'weather_forecast\' with args={"location":"Paris","forecast_date":"2030-01-01"} (tool_call_id=\'0001\')',
        "[Tools] Tool call '0001' returned => The forecast in Paris on 2030-01-01 is 24Â°C and sunny.",
        '=== ModelRequestNode: streaming partial request tokens ===',
        "[Request] Starting part 0: TextPart(content='It will be ', part_kind='text')",
        '[Result] The model produced a final output (tool_name=None)',
        "[Request] Part 0 text delta: 'warm and sunny '",
        "[Request] Part 0 text delta: 'in Paris on '",
        "[Request] Part 0 text delta: 'Tuesday.'",
        '=== CallToolsNode: streaming partial response & tool usage ===',
        '=== Final Agent Output: It will be warm and sunny in Paris on Tuesday. ===',
    ]
    """

```

______________________________________________________________________

### Additional Configuration

#### Usage Limits

PydanticAI offers a UsageLimits structure to help you limit your usage (tokens and/or requests) on model runs.

You can apply these settings by passing the `usage_limits` argument to the `run{_sync,_stream}` functions.

Consider the following example, where we limit the number of response tokens:

```py
from pydantic_ai import Agent
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

agent = Agent('anthropic:claude-3-5-sonnet-latest')

result_sync = agent.run_sync(
    'What is the capital of Italy? Answer with just the city.',
    usage_limits=UsageLimits(response_tokens_limit=10),
)
print(result_sync.output)
#> Rome
print(result_sync.usage())
"""
Usage(requests=1, request_tokens=62, response_tokens=1, total_tokens=63, details=None)
"""

try:
    result_sync = agent.run_sync(
        'What is the capital of Italy? Answer with a paragraph.',
        usage_limits=UsageLimits(response_tokens_limit=10),
    )
except UsageLimitExceeded as e:
    print(e)
    #> Exceeded the response_tokens_limit of 10 (response_tokens=32)

```

Restricting the number of requests can be useful in preventing infinite loops or excessive tool calling:

```py
from typing_extensions import TypedDict

from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits


class NeverOutputType(TypedDict):
    """
    Never ever coerce data to this type.
    """

    never_use_this: str


agent = Agent(
    'anthropic:claude-3-5-sonnet-latest',
    retries=3,
    output_type=NeverOutputType,
    system_prompt='Any time you get a response, call the `infinite_retry_tool` to produce another response.',
)


@agent.tool_plain(retries=5)  # (1)!
def infinite_retry_tool() -> int:
    raise ModelRetry('Please try again.')


try:
    result_sync = agent.run_sync(
        'Begin infinite retry loop!', usage_limits=UsageLimits(request_limit=3)  # (2)!
    )
except UsageLimitExceeded as e:
    print(e)
    #> The next request would exceed the request_limit of 3

```

1. This tool has the ability to retry 5 times before erroring, simulating a tool that might get stuck in a loop.
1. This run will error after 3 requests, preventing the infinite tool calling.

Note

This is especially relevant if you've registered many tools. The `request_limit` can be used to prevent the model from calling them in a loop too many times.

#### Model (Run) Settings

PydanticAI offers a settings.ModelSettings structure to help you fine tune your requests. This structure allows you to configure common parameters that influence the model's behavior, such as `temperature`, `max_tokens`, `timeout`, and more.

There are two ways to apply these settings:

1. Passing to `run{_sync,_stream}` functions via the `model_settings` argument. This allows for fine-tuning on a per-request basis.
1. Setting during Agent initialization via the `model_settings` argument. These settings will be applied by default to all subsequent run calls using said agent. However, `model_settings` provided during a specific run call will override the agent's default settings.

For example, if you'd like to set the `temperature` setting to `0.0` to ensure less random behavior, you can do the following:

```py
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

result_sync = agent.run_sync(
    'What is the capital of Italy?', model_settings={'temperature': 0.0}
)
print(result_sync.output)
#> Rome

```

### Model specific settings

If you wish to further customize model behavior, you can use a subclass of ModelSettings, like GeminiModelSettings, associated with your model of choice.

For example:

```py
from pydantic_ai import Agent, UnexpectedModelBehavior
from pydantic_ai.models.gemini import GeminiModelSettings

agent = Agent('google-gla:gemini-1.5-flash')

try:
    result = agent.run_sync(
        'Write a list of 5 very rude things that I might say to the universe after stubbing my toe in the dark:',
        model_settings=GeminiModelSettings(
            temperature=0.0,  # general model settings can also be specified
            gemini_safety_settings=[
                {
                    'category': 'HARM_CATEGORY_HARASSMENT',
                    'threshold': 'BLOCK_LOW_AND_ABOVE',
                },
                {
                    'category': 'HARM_CATEGORY_HATE_SPEECH',
                    'threshold': 'BLOCK_LOW_AND_ABOVE',
                },
            ],
        ),
    )
except UnexpectedModelBehavior as e:
    print(e)  # (1)!
    """
    Safety settings triggered, body:
    <safety settings details>
    """

```

1. This error is raised because the safety thresholds were exceeded.

## Runs vs. Conversations

An agent **run** might represent an entire conversation â€” there's no limit to how many messages can be exchanged in a single run. However, a **conversation** might also be composed of multiple runs, especially if you need to maintain state between separate interactions or API calls.

Here's an example of a conversation comprised of multiple runs:

conversation_example.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')

# First run
result1 = agent.run_sync('Who was Albert Einstein?')
print(result1.output)
#> Albert Einstein was a German-born theoretical physicist.

# Second run, passing previous messages
result2 = agent.run_sync(
    'What was his most famous equation?',
    message_history=result1.new_messages(),  # (1)!
)
print(result2.output)
#> Albert Einstein's most famous equation is (E = mc^2).

```

1. Continue the conversation; without `message_history` the model would not know who "his" was referring to.

*(This example is complete, it can be run "as is")*

## Type safe by design

PydanticAI is designed to work well with static type checkers, like mypy and pyright.

Typing is (somewhat) optional

PydanticAI is designed to make type checking as useful as possible for you if you choose to use it, but you don't have to use types everywhere all the time.

That said, because PydanticAI uses Pydantic, and Pydantic uses type hints as the definition for schema and validation, some types (specifically type hints on parameters to tools, and the `output_type` arguments to Agent) are used at runtime.

We (the library developers) have messed up if type hints are confusing you more than helping you, if you find this, please create an [issue](https://github.com/pydantic/pydantic-ai/issues) explaining what's annoying you!

In particular, agents are generic in both the type of their dependencies and the type of the outputs they return, so you can use the type hints to ensure you're using the right types.

Consider the following script with type mistakes:

type_mistakes.py

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext


@dataclass
class User:
    name: str


agent = Agent(
    'test',
    deps_type=User,  # (1)!
    output_type=bool,
)


@agent.system_prompt
def add_user_name(ctx: RunContext[str]) -> str:  # (2)!
    return f"The user's name is {ctx.deps}."


def foobar(x: bytes) -> None:
    pass


result = agent.run_sync('Does their name start with "A"?', deps=User('Anne'))
foobar(result.output)  # (3)!

```

1. The agent is defined as expecting an instance of `User` as `deps`.
1. But here `add_user_name` is defined as taking a `str` as the dependency, not a `User`.
1. Since the agent is defined as returning a `bool`, this will raise a type error since `foobar` expects `bytes`.

Running `mypy` on this will give the following output:

```bash
âž¤ uv run mypy type_mistakes.py
type_mistakes.py:18: error: Argument 1 to "system_prompt" of "Agent" has incompatible type "Callable[[RunContext[str]], str]"; expected "Callable[[RunContext[User]], str]"  [arg-type]
type_mistakes.py:28: error: Argument 1 to "foobar" has incompatible type "bool"; expected "bytes"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)

```

Running `pyright` would identify the same issues.

## System Prompts

System prompts might seem simple at first glance since they're just strings (or sequences of strings that are concatenated), but crafting the right system prompt is key to getting the model to behave as you want.

Tip

For most use cases, you should use `instructions` instead of "system prompts".

If you know what you are doing though and want to preserve system prompt messages in the message history sent to the LLM in subsequent completions requests, you can achieve this using the `system_prompt` argument/decorator.

See the section below on [Instructions](#instructions) for more information.

Generally, system prompts fall into two categories:

1. **Static system prompts**: These are known when writing the code and can be defined via the `system_prompt` parameter of the Agent constructor.
1. **Dynamic system prompts**: These depend in some way on context that isn't known until runtime, and should be defined via functions decorated with @agent.system_prompt.

You can add both to a single agent; they're appended in the order they're defined at runtime.

Here's an example using both types of system prompts:

system_prompts.py

```python
from datetime import date

from pydantic_ai import Agent, RunContext

agent = Agent(
    'openai:gpt-4o',
    deps_type=str,  # (1)!
    system_prompt="Use the customer's name while replying to them.",  # (2)!
)


@agent.system_prompt  # (3)!
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}."


@agent.system_prompt
def add_the_date() -> str:  # (4)!
    return f'The date is {date.today()}.'


result = agent.run_sync('What is the date?', deps='Frank')
print(result.output)
#> Hello Frank, the date today is 2032-01-02.

```

1. The agent expects a string dependency.
1. Static system prompt defined at agent creation time.
1. Dynamic system prompt defined via a decorator with RunContext, this is called just after `run_sync`, not when the agent is created, so can benefit from runtime information like the dependencies used on that run.
1. Another dynamic system prompt, system prompts don't have to have the `RunContext` parameter.

*(This example is complete, it can be run "as is")*

## Instructions

Instructions are similar to system prompts. The main difference is that when an explicit `message_history` is provided in a call to `Agent.run` and similar methods, *instructions* from any existing messages in the history are not included in the request to the model â€” only the instructions of the *current* agent are included.

You should use:

- `instructions` when you want your request to the model to only include system prompts for the *current* agent
- `system_prompt` when you want your request to the model to *retain* the system prompts used in previous requests (possibly made using other agents)

In general, we recommend using `instructions` instead of `system_prompt` unless you have a specific reason to use `system_prompt`.

instructions.py

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o',
    instructions='You are a helpful assistant that can answer questions and help with tasks.',  # (1)!
)

result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris

```

1. This will be the only instructions for this agent.

*(This example is complete, it can be run "as is")*

## Reflection and self-correction

Validation errors from both function tool parameter validation and [structured output validation](../output/#structured-output) can be passed back to the model with a request to retry.

You can also raise ModelRetry from within a [tool](../tools/) or [output validator function](../output/#output-validator-functions) to tell the model it should retry generating a response.

- The default retry count is **1** but can be altered for the entire agent, a specific tool, or an output validator.
- You can access the current retry count from within a tool or output validator via ctx.retry.

Here's an example:

tool_retry.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ModelRetry

from fake_database import DatabaseConn


class ChatResult(BaseModel):
    user_id: int
    message: str


agent = Agent(
    'openai:gpt-4o',
    deps_type=DatabaseConn,
    output_type=ChatResult,
)


@agent.tool(retries=2)
def get_user_by_name(ctx: RunContext[DatabaseConn], name: str) -> int:
    """Get a user's ID from their full name."""
    print(name)
    #> John
    #> John Doe
    user_id = ctx.deps.users.get(name=name)
    if user_id is None:
        raise ModelRetry(
            f'No user found with name {name!r}, remember to provide their full name'
        )
    return user_id


result = agent.run_sync(
    'Send a message to John Doe asking for coffee next week', deps=DatabaseConn()
)
print(result.output)
"""
user_id=123 message='Hello John, would you be free for coffee sometime next week? Let me know what works for you!'
"""

```

## Model errors

If models behave unexpectedly (e.g., the retry limit is exceeded, or their API returns `503`), agent runs will raise UnexpectedModelBehavior.

In these cases, capture_run_messages can be used to access the messages exchanged during the run to help diagnose the issue.

agent_model_errors.py

```python
from pydantic_ai import Agent, ModelRetry, UnexpectedModelBehavior, capture_run_messages

agent = Agent('openai:gpt-4o')


@agent.tool_plain
def calc_volume(size: int) -> int:  # (1)!
    if size == 42:
        return size**3
    else:
        raise ModelRetry('Please try again.')


with capture_run_messages() as messages:  # (2)!
    try:
        result = agent.run_sync('Please get me the volume of a box with size 6.')
    except UnexpectedModelBehavior as e:
        print('An error occurred:', e)
        #> An error occurred: Tool exceeded max retries count of 1
        print('cause:', repr(e.__cause__))
        #> cause: ModelRetry('Please try again.')
        print('messages:', messages)
        """
        messages:
        [
            ModelRequest(
                parts=[
                    UserPromptPart(
                        content='Please get me the volume of a box with size 6.',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    )
                ],
                instructions=None,
                kind='request',
            ),
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name='calc_volume',
                        args={'size': 6},
                        tool_call_id='pyd_ai_tool_call_id',
                        part_kind='tool-call',
                    )
                ],
                usage=Usage(
                    requests=1,
                    request_tokens=62,
                    response_tokens=4,
                    total_tokens=66,
                    details=None,
                ),
                model_name='gpt-4o',
                timestamp=datetime.datetime(...),
                kind='response',
            ),
            ModelRequest(
                parts=[
                    RetryPromptPart(
                        content='Please try again.',
                        tool_name='calc_volume',
                        tool_call_id='pyd_ai_tool_call_id',
                        timestamp=datetime.datetime(...),
                        part_kind='retry-prompt',
                    )
                ],
                instructions=None,
                kind='request',
            ),
            ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_name='calc_volume',
                        args={'size': 6},
                        tool_call_id='pyd_ai_tool_call_id',
                        part_kind='tool-call',
                    )
                ],
                usage=Usage(
                    requests=1,
                    request_tokens=72,
                    response_tokens=8,
                    total_tokens=80,
                    details=None,
                ),
                model_name='gpt-4o',
                timestamp=datetime.datetime(...),
                kind='response',
            ),
        ]
        """
    else:
        print(result.output)

```

1. Define a tool that will raise `ModelRetry` repeatedly in this case.
1. capture_run_messages is used to capture the messages exchanged during the run.

*(This example is complete, it can be run "as is")*

Note

If you call run, run_sync, or run_stream more than once within a single `capture_run_messages` context, `messages` will represent the messages exchanged during the first call only.

# Common Tools

PydanticAI ships with native tools that can be used to enhance your agent's capabilities.

## DuckDuckGo Search Tool

The DuckDuckGo search tool allows you to search the web for information. It is built on top of the [DuckDuckGo API](https://github.com/deedy5/duckduckgo_search).

### Installation

To use duckduckgo_search_tool, you need to install [`pydantic-ai-slim`](../install/#slim-install) with the `duckduckgo` optional group:

```bash
pip install "pydantic-ai-slim[duckduckgo]"

```

```bash
uv add "pydantic-ai-slim[duckduckgo]"

```

### Usage

Here's an example of how you can use the DuckDuckGo search tool with an agent:

main.py

```py
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'openai:o3-mini',
    tools=[duckduckgo_search_tool()],
    system_prompt='Search DuckDuckGo for the given query and return the results.',
)

result = agent.run_sync(
    'Can you list the top five highest-grossing animated films of 2025?'
)
print(result.output)
"""
I looked into several sources on animated boxâ€office performance in 2025, and while detailed
rankings can shift as more money is tallied, multiple independent reports have already
highlighted a couple of recordâ€breaking shows. For example:

â€¢ Ne Zha 2 â€“ News outlets (Variety, Wikipedia's "List of animated feature films of 2025", and others)
    have reported that this Chinese title not only became the highestâ€‘grossing animated film of 2025
    but also broke records as the highestâ€‘grossing nonâ€‘English animated film ever. One article noted
    its run exceeded US$1.7 billion.
â€¢ Inside Out 2 â€“ According to data shared on Statista and in industry news, this Pixar sequel has been
    on pace to set new records (with some sources even noting it as the highestâ€‘grossing animated film
    ever, as of January 2025).

Beyond those two, some entertainment trade sites (for example, a Just Jared article titled
"Top 10 Highest-Earning Animated Films at the Box Office Revealed") have begun listing a broader
topâ€‘10. Although full consolidated figures can sometimes differ by source and are updated daily during
a boxâ€‘office run, many of the industry trackers have begun to single out five films as the biggest
earners so far in 2025.

Unfortunately, although multiple articles discuss the "top animated films" of 2025, there isn't yet a
single, universally accepted list with final numbers that names the complete top five. (Boxâ€‘office
rankings, especially midâ€‘year, can be fluid as films continue to add to their totals.)

Based on what several sources note so far, the two undisputed leaders are:
1. Ne Zha 2
2. Inside Out 2

The remaining top spots (3â€“5) are reported by some outlets in their "Topâ€‘10 Animated Films"
lists for 2025 but the titles and order can vary depending on the source and the exact cutâ€‘off
date of the data. For the most upâ€‘toâ€‘date and detailed ranking (including the 3rd, 4th, and 5th
highestâ€‘grossing films), I recommend checking resources like:
â€¢ Wikipedia's "List of animated feature films of 2025" page
â€¢ Boxâ€‘office tracking sites (such as Box Office Mojo or The Numbers)
â€¢ Trade articles like the one on Just Jared

To summarize with what is clear from the current reporting:
1. Ne Zha 2
2. Inside Out 2
3â€“5. Other animated films (yet to be definitively finalized across all reporting outlets)

If you're looking for a final, consensus list of the top five, it may be best to wait until
the 2025 yearâ€‘end boxâ€‘office tallies are in or to consult a regularly updated entertainment industry source.

Would you like help finding a current source or additional details on where to look for the complete updated list?
"""

```

## Tavily Search Tool

Info

Tavily is a paid service, but they have free credits to explore their product.

You need to [sign up for an account](https://app.tavily.com/home) and get an API key to use the Tavily search tool.

The Tavily search tool allows you to search the web for information. It is built on top of the [Tavily API](https://tavily.com/).

### Installation

To use tavily_search_tool, you need to install [`pydantic-ai-slim`](../install/#slim-install) with the `tavily` optional group:

```bash
pip install "pydantic-ai-slim[tavily]"

```

```bash
uv add "pydantic-ai-slim[tavily]"

```

### Usage

Here's an example of how you can use the Tavily search tool with an agent:

main.py

```py
import os

from pydantic_ai.agent import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

api_key = os.getenv('TAVILY_API_KEY')
assert api_key is not None

agent = Agent(
    'openai:o3-mini',
    tools=[tavily_search_tool(api_key)],
    system_prompt='Search Tavily for the given query and return the results.',
)

result = agent.run_sync('Tell me the top news in the GenAI world, give me links.')
print(result.output)
"""
Here are some of the top recent news articles related to GenAI:

1. How CLEAR users can improve risk analysis with GenAI â€“ Thomson Reuters
   Read more: https://legal.thomsonreuters.com/blog/how-clear-users-can-improve-risk-analysis-with-genai/
   (This article discusses how CLEAR's new GenAI-powered tool streamlines risk analysis by quickly summarizing key information from various public data sources.)

2. TELUS Digital Survey Reveals Enterprise Employees Are Entering Sensitive Data Into AI Assistants More Than You Think â€“ FT.com
   Read more: https://markets.ft.com/data/announce/detail?dockey=600-202502260645BIZWIRE_USPRX____20250226_BW490609-1
   (This news piece highlights findings from a TELUS Digital survey showing that many enterprise employees use public GenAI tools and sometimes even enter sensitive data.)

3. The Essential Guide to Generative AI â€“ Virtualization Review
   Read more: https://virtualizationreview.com/Whitepapers/2025/02/SNOWFLAKE-The-Essential-Guide-to-Generative-AI.aspx
   (This guide provides insights into how GenAI is revolutionizing enterprise strategies and productivity, with input from industry leaders.)

Feel free to click on the links to dive deeper into each story!
"""

```

# Dependencies

PydanticAI uses a dependency injection system to provide data and services to your agent's [system prompts](../agents/#system-prompts), [tools](../tools/) and [output validators](../output/#output-validator-functions).

Matching PydanticAI's design philosophy, our dependency system tries to use existing best practice in Python development rather than inventing esoteric "magic", this should make dependencies type-safe, understandable easier to test and ultimately easier to deploy in production.

## Defining Dependencies

Dependencies can be any python type. While in simple cases you might be able to pass a single object as a dependency (e.g. an HTTP connection), dataclasses are generally a convenient container when your dependencies included multiple objects.

Here's an example of defining an agent that requires dependencies.

(**Note:** dependencies aren't actually used in this example, see [Accessing Dependencies](#accessing-dependencies) below)

unused_dependencies.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent


@dataclass
class MyDeps:  # (1)!
    api_key: str
    http_client: httpx.AsyncClient


agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,  # (2)!
)


async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run(
            'Tell me a joke.',
            deps=deps,  # (3)!
        )
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.

```

1. Define a dataclass to hold dependencies.
1. Pass the dataclass type to the `deps_type` argument of the Agent constructor. **Note**: we're passing the type here, NOT an instance, this parameter is not actually used at runtime, it's here so we can get full type checking of the agent.
1. When running the agent, pass an instance of the dataclass to the `deps` parameter.

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

## Accessing Dependencies

Dependencies are accessed through the RunContext type, this should be the first parameter of system prompt functions etc.

system_prompt_dependencies.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext


@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient


agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)


@agent.system_prompt  # (1)!
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:  # (2)!
    response = await ctx.deps.http_client.get(  # (3)!
        'https://example.com',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},  # (4)!
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'


async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.

```

1. RunContext may optionally be passed to a system_prompt function as the only argument.
1. RunContext is parameterized with the type of the dependencies, if this type is incorrect, static type checkers will raise an error.
1. Access dependencies through the .deps attribute.
1. Access dependencies through the .deps attribute.

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

### Asynchronous vs. Synchronous dependencies

[System prompt functions](../agents/#system-prompts), [function tools](../tools/) and [output validators](../output/#output-validator-functions) are all run in the async context of an agent run.

If these functions are not coroutines (e.g. `async def`) they are called with run_in_executor in a thread pool, it's therefore marginally preferable to use `async` methods where dependencies perform IO, although synchronous dependencies should work fine too.

`run` vs. `run_sync` and Asynchronous vs. Synchronous dependencies

Whether you use synchronous or asynchronous dependencies, is completely independent of whether you use `run` or `run_sync` â€” `run_sync` is just a wrapper around `run` and agents are always run in an async context.

Here's the same example as above, but with a synchronous dependency:

sync_dependencies.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext


@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.Client  # (1)!


agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)


@agent.system_prompt
def get_system_prompt(ctx: RunContext[MyDeps]) -> str:  # (2)!
    response = ctx.deps.http_client.get(
        'https://example.com', headers={'Authorization': f'Bearer {ctx.deps.api_key}'}
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'


async def main():
    deps = MyDeps('foobar', httpx.Client())
    result = await agent.run(
        'Tell me a joke.',
        deps=deps,
    )
    print(result.output)
    #> Did you hear about the toothpaste scandal? They called it Colgate.

```

1. Here we use a synchronous `httpx.Client` instead of an asynchronous `httpx.AsyncClient`.
1. To match the synchronous dependency, the system prompt function is now a plain function, not a coroutine.

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

## Full Example

As well as system prompts, dependencies can be used in [tools](../tools/) and [output validators](../output/#output-validator-functions).

full_example.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, ModelRetry, RunContext


@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient


agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)


@agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    response = await ctx.deps.http_client.get('https://example.com')
    response.raise_for_status()
    return f'Prompt: {response.text}'


@agent.tool  # (1)!
async def get_joke_material(ctx: RunContext[MyDeps], subject: str) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com#jokes',
        params={'subject': subject},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return response.text


@agent.output_validator  # (2)!
async def validate_output(ctx: RunContext[MyDeps], output: str) -> str:
    response = await ctx.deps.http_client.post(
        'https://example.com#validate',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
        params={'query': output},
    )
    if response.status_code == 400:
        raise ModelRetry(f'invalid response: {response.text}')
    response.raise_for_status()
    return output


async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.

```

1. To pass `RunContext` to a tool, use the tool decorator.
1. `RunContext` may optionally be passed to a output_validator function as the first argument.

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

## Overriding Dependencies

When testing agents, it's useful to be able to customise dependencies.

While this can sometimes be done by calling the agent directly within unit tests, we can also override dependencies while calling application code which in turn calls the agent.

This is done via the override method on the agent.

joke_app.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext


@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

    async def system_prompt_factory(self) -> str:  # (1)!
        response = await self.http_client.get('https://example.com')
        response.raise_for_status()
        return f'Prompt: {response.text}'


joke_agent = Agent('openai:gpt-4o', deps_type=MyDeps)


@joke_agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    return await ctx.deps.system_prompt_factory()  # (2)!


async def application_code(prompt: str) -> str:  # (3)!
    ...
    ...
    # now deep within application code we call our agent
    async with httpx.AsyncClient() as client:
        app_deps = MyDeps('foobar', client)
        result = await joke_agent.run(prompt, deps=app_deps)  # (4)!
    return result.output

```

1. Define a method on the dependency to make the system prompt easier to customise.
1. Call the system prompt factory from within the system prompt function.
1. Application code that calls the agent, in a real application this might be an API endpoint.
1. Call the agent from within the application code, in a real application this call might be deep within a call stack. Note `app_deps` here will NOT be used when deps are overridden.

*(This example is complete, it can be run "as is")*

test_joke_app.py

```python
from joke_app import MyDeps, application_code, joke_agent


class TestMyDeps(MyDeps):  # (1)!
    async def system_prompt_factory(self) -> str:
        return 'test prompt'


async def test_application_code():
    test_deps = TestMyDeps('test_key', None)  # (2)!
    with joke_agent.override(deps=test_deps):  # (3)!
        joke = await application_code('Tell me a joke.')  # (4)!
    assert joke.startswith('Did you hear about the toothpaste scandal?')

```

1. Define a subclass of `MyDeps` in tests to customise the system prompt factory.
1. Create an instance of the test dependency, we don't need to pass an `http_client` here as it's not used.
1. Override the dependencies of the agent for the duration of the `with` block, `test_deps` will be used when the agent is run.
1. Now we can safely call our application code, the agent will use the overridden dependencies.

## Examples

The following examples demonstrate how to use dependencies in PydanticAI:

- [Weather Agent](../examples/weather-agent/)
- [SQL Generation](../examples/sql-gen/)
- [RAG](../examples/rag/)

# Messages and chat history

PydanticAI provides access to messages exchanged during an agent run. These messages can be used both to continue a coherent conversation, and to understand how an agent performed.

### Accessing Messages from Results

After running an agent, you can access the messages exchanged during that run from the `result` object.

Both RunResult (returned by Agent.run, Agent.run_sync) and StreamedRunResult (returned by Agent.run_stream) have the following methods:

- all_messages(): returns all messages, including messages from prior runs. There's also a variant that returns JSON bytes, all_messages_json().
- new_messages(): returns only the messages from the current run. There's also a variant that returns JSON bytes, new_messages_json().

StreamedRunResult and complete messages

On StreamedRunResult, the messages returned from these methods will only include the final result message once the stream has finished.

E.g. you've awaited one of the following coroutines:

- StreamedRunResult.stream()
- StreamedRunResult.stream_text()
- StreamedRunResult.stream_structured()
- StreamedRunResult.get_output()

**Note:** The final result message will NOT be added to result messages if you use .stream_text(delta=True) since in this case the result content is never built as one string.

Example of accessing methods on a RunResult :

run_result_messages.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result = agent.run_sync('Tell me a joke.')
print(result.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

# all messages from the run
print(result.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                timestamp=datetime.datetime(...),
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.',
                part_kind='text',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=60,
            response_tokens=12,
            total_tokens=72,
            details=None,
        ),
        model_name='gpt-4o',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""

```

*(This example is complete, it can be run "as is")*

Example of accessing methods on a StreamedRunResult :

streamed_run_result_messages.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')


async def main():
    async with agent.run_stream('Tell me a joke.') as result:
        # incomplete messages before the stream finishes
        print(result.all_messages())
        """
        [
            ModelRequest(
                parts=[
                    SystemPromptPart(
                        content='Be a helpful assistant.',
                        timestamp=datetime.datetime(...),
                        dynamic_ref=None,
                        part_kind='system-prompt',
                    ),
                    UserPromptPart(
                        content='Tell me a joke.',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    ),
                ],
                instructions=None,
                kind='request',
            )
        ]
        """

        async for text in result.stream_text():
            print(text)
            #> Did you hear
            #> Did you hear about the toothpaste
            #> Did you hear about the toothpaste scandal? They called
            #> Did you hear about the toothpaste scandal? They called it Colgate.

        # complete messages once the stream finishes
        print(result.all_messages())
        """
        [
            ModelRequest(
                parts=[
                    SystemPromptPart(
                        content='Be a helpful assistant.',
                        timestamp=datetime.datetime(...),
                        dynamic_ref=None,
                        part_kind='system-prompt',
                    ),
                    UserPromptPart(
                        content='Tell me a joke.',
                        timestamp=datetime.datetime(...),
                        part_kind='user-prompt',
                    ),
                ],
                instructions=None,
                kind='request',
            ),
            ModelResponse(
                parts=[
                    TextPart(
                        content='Did you hear about the toothpaste scandal? They called it Colgate.',
                        part_kind='text',
                    )
                ],
                usage=Usage(
                    requests=0,
                    request_tokens=50,
                    response_tokens=12,
                    total_tokens=62,
                    details=None,
                ),
                model_name='gpt-4o',
                timestamp=datetime.datetime(...),
                kind='response',
            ),
        ]
        """

```

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

### Using Messages as Input for Further Agent Runs

The primary use of message histories in PydanticAI is to maintain context across multiple agent runs.

To use existing messages in a run, pass them to the `message_history` parameter of Agent.run, Agent.run_sync or Agent.run_stream.

If `message_history` is set and not empty, a new system prompt is not generated â€” we assume the existing message history includes a system prompt.

Reusing messages in a conversation

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync('Explain?', message_history=result1.new_messages())
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.

print(result2.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                timestamp=datetime.datetime(...),
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.',
                part_kind='text',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=60,
            response_tokens=12,
            total_tokens=72,
            details=None,
        ),
        model_name='gpt-4o',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Explain?',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            )
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='This is an excellent joke invented by Samuel Colvin, it needs no explanation.',
                part_kind='text',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=61,
            response_tokens=26,
            total_tokens=87,
            details=None,
        ),
        model_name='gpt-4o',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""

```

*(This example is complete, it can be run "as is")*

## Storing and loading messages (to JSON)

While maintaining conversation state in memory is enough for many applications, often times you may want to store the messages history of an agent run on disk or in a database. This might be for evals, for sharing data between Python and JavaScript/TypeScript, or any number of other use cases.

The intended way to do this is using a `TypeAdapter`.

We export ModelMessagesTypeAdapter that can be used for this, or you can create your own.

Here's an example showing how:

serialize messages to json

```python
from pydantic_core import to_jsonable_python

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter  # (1)!

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
history_step_1 = result1.all_messages()
as_python_objects = to_jsonable_python(history_step_1)  # (2)!
same_history_as_step_1 = ModelMessagesTypeAdapter.validate_python(as_python_objects)

result2 = agent.run_sync(  # (3)!
    'Tell me a different joke.', message_history=same_history_as_step_1
)

```

1. Alternatively, you can create a `TypeAdapter` from scratch:
   ```python
   from pydantic import TypeAdapter
   from pydantic_ai.messages import ModelMessage
   ModelMessagesTypeAdapter = TypeAdapter(list[ModelMessage])

   ```
1. Alternatively you can serialize to/from JSON directly:
   ```python
   from pydantic_core import to_json
   ...
   as_json_objects = to_json(history_step_1)
   same_history_as_step_1 = ModelMessagesTypeAdapter.validate_json(as_json_objects)

   ```
1. You can now continue the conversation with history `same_history_as_step_1` despite creating a new agent run.

*(This example is complete, it can be run "as is")*

## Other ways of using messages

Since messages are defined by simple dataclasses, you can manually create and manipulate, e.g. for testing.

The message format is independent of the model used, so you can use messages in different agents, or the same agent with different models.

In the example below, we reuse the message from the first agent run, which uses the `openai:gpt-4o` model, in a second agent run using the `google-gla:gemini-1.5-pro` model.

Reusing messages with a different model

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', system_prompt='Be a helpful assistant.')

result1 = agent.run_sync('Tell me a joke.')
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync(
    'Explain?',
    model='google-gla:gemini-1.5-pro',
    message_history=result1.new_messages(),
)
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.

print(result2.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content='Be a helpful assistant.',
                timestamp=datetime.datetime(...),
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='Tell me a joke.',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='Did you hear about the toothpaste scandal? They called it Colgate.',
                part_kind='text',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=60,
            response_tokens=12,
            total_tokens=72,
            details=None,
        ),
        model_name='gpt-4o',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
    ModelRequest(
        parts=[
            UserPromptPart(
                content='Explain?',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            )
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content='This is an excellent joke invented by Samuel Colvin, it needs no explanation.',
                part_kind='text',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=61,
            response_tokens=26,
            total_tokens=87,
            details=None,
        ),
        model_name='gemini-1.5-pro',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""

```

## Examples

For a more complete example of using messages in conversations, see the [chat app](../examples/chat-app/) example.

# Multi-agent Applications

There are roughly four levels of complexity when building applications with PydanticAI:

1. Single agent workflows â€” what most of the `pydantic_ai` documentation covers
1. [Agent delegation](#agent-delegation) â€” agents using another agent via tools
1. [Programmatic agent hand-off](#programmatic-agent-hand-off) â€” one agent runs, then application code calls another agent
1. [Graph based control flow](../graph/) â€” for the most complex cases, a graph-based state machine can be used to control the execution of multiple agents

Of course, you can combine multiple strategies in a single application.

## Agent delegation

"Agent delegation" refers to the scenario where an agent delegates work to another agent, then takes back control when the delegate agent (the agent called from within a tool) finishes.

Since agents are stateless and designed to be global, you do not need to include the agent itself in agent [dependencies](../dependencies/).

You'll generally want to pass ctx.usage to the usage keyword argument of the delegate agent run so usage within that run counts towards the total usage of the parent agent run.

Multiple models

Agent delegation doesn't need to use the same model for each agent. If you choose to use different models within a run, calculating the monetary cost from the final result.usage() of the run will not be possible, but you can still use UsageLimits to avoid unexpected costs.

agent_delegation_simple.py

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits

joke_selection_agent = Agent(  # (1)!
    'openai:gpt-4o',
    system_prompt=(
        'Use the `joke_factory` to generate some jokes, then choose the best. '
        'You must return just a single joke.'
    ),
)
joke_generation_agent = Agent(  # (2)!
    'google-gla:gemini-1.5-flash', output_type=list[str]
)


@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
    r = await joke_generation_agent.run(  # (3)!
        f'Please generate {count} jokes.',
        usage=ctx.usage,  # (4)!
    )
    return r.output  # (5)!


result = joke_selection_agent.run_sync(
    'Tell me a joke.',
    usage_limits=UsageLimits(request_limit=5, total_tokens_limit=300),
)
print(result.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.
print(result.usage())
"""
Usage(
    requests=3, request_tokens=204, response_tokens=24, total_tokens=228, details=None
)
"""

```

1. The "parent" or controlling agent.
1. The "delegate" agent, which is called from within a tool of the parent agent.
1. Call the delegate agent from within a tool of the parent agent.
1. Pass the usage from the parent agent to the delegate agent so the final result.usage() includes the usage from both agents.
1. Since the function returns `list[str]`, and the `output_type` of `joke_generation_agent` is also `list[str]`, we can simply return `r.output` from the tool.

*(This example is complete, it can be run "as is")*

The control flow for this example is pretty simple and can be summarised as follows:

```
graph TD
  START --> joke_selection_agent
  joke_selection_agent --> joke_factory["joke_factory (tool)"]
  joke_factory --> joke_generation_agent
  joke_generation_agent --> joke_factory
  joke_factory --> joke_selection_agent
  joke_selection_agent --> END
```

### Agent delegation and dependencies

Generally the delegate agent needs to either have the same [dependencies](../dependencies/) as the calling agent, or dependencies which are a subset of the calling agent's dependencies.

Initializing dependencies

We say "generally" above since there's nothing to stop you initializing dependencies within a tool call and therefore using interdependencies in a delegate agent that are not available on the parent, this should often be avoided since it can be significantly slower than reusing connections etc. from the parent agent.

agent_delegation_deps.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext


@dataclass
class ClientAndKey:  # (1)!
    http_client: httpx.AsyncClient
    api_key: str


joke_selection_agent = Agent(
    'openai:gpt-4o',
    deps_type=ClientAndKey,  # (2)!
    system_prompt=(
        'Use the `joke_factory` tool to generate some jokes on the given subject, '
        'then choose the best. You must return just a single joke.'
    ),
)
joke_generation_agent = Agent(
    'gemini-1.5-flash',
    deps_type=ClientAndKey,  # (4)!
    output_type=list[str],
    system_prompt=(
        'Use the "get_jokes" tool to get some jokes on the given subject, '
        'then extract each joke into a list.'
    ),
)


@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[ClientAndKey], count: int) -> list[str]:
    r = await joke_generation_agent.run(
        f'Please generate {count} jokes.',
        deps=ctx.deps,  # (3)!
        usage=ctx.usage,
    )
    return r.output


@joke_generation_agent.tool  # (5)!
async def get_jokes(ctx: RunContext[ClientAndKey], count: int) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com',
        params={'count': count},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return response.text


async def main():
    async with httpx.AsyncClient() as client:
        deps = ClientAndKey(client, 'foobar')
        result = await joke_selection_agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.
        print(result.usage())  # (6)!
        """
        Usage(
            requests=4,
            request_tokens=309,
            response_tokens=32,
            total_tokens=341,
            details=None,
        )
        """

```

1. Define a dataclass to hold the client and API key dependencies.
1. Set the `deps_type` of the calling agent â€” `joke_selection_agent` here.
1. Pass the dependencies to the delegate agent's run method within the tool call.
1. Also set the `deps_type` of the delegate agent â€” `joke_generation_agent` here.
1. Define a tool on the delegate agent that uses the dependencies to make an HTTP request.
1. Usage now includes 4 requests â€” 2 from the calling agent and 2 from the delegate agent.

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

This example shows how even a fairly simple agent delegation can lead to a complex control flow:

```
graph TD
  START --> joke_selection_agent
  joke_selection_agent --> joke_factory["joke_factory (tool)"]
  joke_factory --> joke_generation_agent
  joke_generation_agent --> get_jokes["get_jokes (tool)"]
  get_jokes --> http_request["HTTP request"]
  http_request --> get_jokes
  get_jokes --> joke_generation_agent
  joke_generation_agent --> joke_factory
  joke_factory --> joke_selection_agent
  joke_selection_agent --> END
```

## Programmatic agent hand-off

"Programmatic agent hand-off" refers to the scenario where multiple agents are called in succession, with application code and/or a human in the loop responsible for deciding which agent to call next.

Here agents don't need to use the same deps.

Here we show two agents used in succession, the first to find a flight and the second to extract the user's seat preference.

programmatic_handoff.py

```python
from typing import Literal, Union

from pydantic import BaseModel, Field
from rich.prompt import Prompt

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage, UsageLimits


class FlightDetails(BaseModel):
    flight_number: str


class Failed(BaseModel):
    """Unable to find a satisfactory choice."""


flight_search_agent = Agent[None, Union[FlightDetails, Failed]](  # (1)!
    'openai:gpt-4o',
    output_type=Union[FlightDetails, Failed],  # type: ignore
    system_prompt=(
        'Use the "flight_search" tool to find a flight '
        'from the given origin to the given destination.'
    ),
)


@flight_search_agent.tool  # (2)!
async def flight_search(
    ctx: RunContext[None], origin: str, destination: str
) -> Union[FlightDetails, None]:
    # in reality, this would call a flight search API or
    # use a browser to scrape a flight search website
    return FlightDetails(flight_number='AK456')


usage_limits = UsageLimits(request_limit=15)  # (3)!


async def find_flight(usage: Usage) -> Union[FlightDetails, None]:  # (4)!
    message_history: Union[list[ModelMessage], None] = None
    for _ in range(3):
        prompt = Prompt.ask(
            'Where would you like to fly from and to?',
        )
        result = await flight_search_agent.run(
            prompt,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.output, FlightDetails):
            return result.output
        else:
            message_history = result.all_messages(
                output_tool_return_content='Please try again.'
            )


class SeatPreference(BaseModel):
    row: int = Field(ge=1, le=30)
    seat: Literal['A', 'B', 'C', 'D', 'E', 'F']


# This agent is responsible for extracting the user's seat selection
seat_preference_agent = Agent[None, Union[SeatPreference, Failed]](  # (5)!
    'openai:gpt-4o',
    output_type=Union[SeatPreference, Failed],  # type: ignore
    system_prompt=(
        "Extract the user's seat preference. "
        'Seats A and F are window seats. '
        'Row 1 is the front row and has extra leg room. '
        'Rows 14, and 20 also have extra leg room. '
    ),
)


async def find_seat(usage: Usage) -> SeatPreference:  # (6)!
    message_history: Union[list[ModelMessage], None] = None
    while True:
        answer = Prompt.ask('What seat would you like?')

        result = await seat_preference_agent.run(
            answer,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.output, SeatPreference):
            return result.output
        else:
            print('Could not understand seat preference. Please try again.')
            message_history = result.all_messages()


async def main():  # (7)!
    usage: Usage = Usage()

    opt_flight_details = await find_flight(usage)
    if opt_flight_details is not None:
        print(f'Flight found: {opt_flight_details.flight_number}')
        #> Flight found: AK456
        seat_preference = await find_seat(usage)
        print(f'Seat preference: {seat_preference}')
        #> Seat preference: row=1 seat='A'

```

1. Define the first agent, which finds a flight. We use an explicit type annotation until [PEP-747](https://peps.python.org/pep-0747/) lands, see [structured output](../output/#structured-output). We use a union as the output type so the model can communicate if it's unable to find a satisfactory choice; internally, each member of the union will be registered as a separate tool.
1. Define a tool on the agent to find a flight. In this simple case we could dispense with the tool and just define the agent to return structured data, then search for a flight, but in more complex scenarios the tool would be necessary.
1. Define usage limits for the entire app.
1. Define a function to find a flight, which asks the user for their preferences and then calls the agent to find a flight.
1. As with `flight_search_agent` above, we use an explicit type annotation to define the agent.
1. Define a function to find the user's seat preference, which asks the user for their seat preference and then calls the agent to extract the seat preference.
1. Now that we've put our logic for running each agent into separate functions, our main app becomes very simple.

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main())` to run `main`)*

The control flow for this example can be summarised as follows:

```
graph TB
  START --> ask_user_flight["ask user for flight"]

  subgraph find_flight
    flight_search_agent --> ask_user_flight
    ask_user_flight --> flight_search_agent
  end

  flight_search_agent --> ask_user_seat["ask user for seat"]
  flight_search_agent --> END

  subgraph find_seat
    seat_preference_agent --> ask_user_seat
    ask_user_seat --> seat_preference_agent
  end

  seat_preference_agent --> END
```

## Pydantic Graphs

See the [graph](../graph/) documentation on when and how to use graphs.

## Examples

The following examples demonstrate how to use dependencies in PydanticAI:

- [Flight booking](../examples/flight-booking/)

# Function Tools

Function tools provide a mechanism for models to retrieve extra information to help them generate a response.

They're useful when it is impractical or impossible to put all the context an agent might need into the system prompt, or when you want to make agents' behavior more deterministic or reliable by deferring some of the logic required to generate a response to another (not necessarily AI-powered) tool.

Function tools vs. RAG

Function tools are basically the "R" of RAG (Retrieval-Augmented Generation) â€” they augment what the model can do by letting it request extra information.

The main semantic difference between PydanticAI Tools and RAG is RAG is synonymous with vector search, while PydanticAI tools are more general-purpose. (Note: we may add support for vector search functionality in the future, particularly an API for generating embeddings. See [#58](https://github.com/pydantic/pydantic-ai/issues/58))

There are a number of ways to register tools with an agent:

- via the @agent.tool decorator â€” for tools that need access to the agent context
- via the @agent.tool_plain decorator â€” for tools that do not need access to the agent context
- via the tools keyword argument to `Agent` which can take either plain functions, or instances of Tool

## Registering Function Tools via Decorator

`@agent.tool` is considered the default decorator since in the majority of cases tools will need access to the agent context.

Here's an example using both:

dice_game.py

```python
import random

from pydantic_ai import Agent, RunContext

agent = Agent(
    'google-gla:gemini-1.5-flash',  # (1)!
    deps_type=str,  # (2)!
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    ),
)


@agent.tool_plain  # (3)!
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))


@agent.tool  # (4)!
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps


dice_result = agent.run_sync('My guess is 4', deps='Anne')  # (5)!
print(dice_result.output)
#> Congratulations Anne, you guessed correctly! You're a winner!

```

1. This is a pretty simple task, so we can use the fast and cheap Gemini flash model.
1. We pass the user's name as the dependency, to keep things simple we use just the name as a string as the dependency.
1. This tool doesn't need any context, it just returns a random number. You could probably use a dynamic system prompt in this case.
1. This tool needs the player's name, so it uses `RunContext` to access dependencies which are just the player's name in this case.
1. Run the agent, passing the player's name as the dependency.

*(This example is complete, it can be run "as is")*

Let's print the messages from that game to see what happened:

dice_game_messages.py

```python
from dice_game import dice_result

print(dice_result.all_messages())
"""
[
    ModelRequest(
        parts=[
            SystemPromptPart(
                content="You're a dice game, you should roll the die and see if the number you get back matches the user's guess. If so, tell them they're a winner. Use the player's name in the response.",
                timestamp=datetime.datetime(...),
                dynamic_ref=None,
                part_kind='system-prompt',
            ),
            UserPromptPart(
                content='My guess is 4',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            ),
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            ToolCallPart(
                tool_name='roll_die',
                args={},
                tool_call_id='pyd_ai_tool_call_id',
                part_kind='tool-call',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=90,
            response_tokens=2,
            total_tokens=92,
            details=None,
        ),
        model_name='gemini-1.5-flash',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
    ModelRequest(
        parts=[
            ToolReturnPart(
                tool_name='roll_die',
                content='4',
                tool_call_id='pyd_ai_tool_call_id',
                timestamp=datetime.datetime(...),
                part_kind='tool-return',
            )
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            ToolCallPart(
                tool_name='get_player_name',
                args={},
                tool_call_id='pyd_ai_tool_call_id',
                part_kind='tool-call',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=91,
            response_tokens=4,
            total_tokens=95,
            details=None,
        ),
        model_name='gemini-1.5-flash',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
    ModelRequest(
        parts=[
            ToolReturnPart(
                tool_name='get_player_name',
                content='Anne',
                tool_call_id='pyd_ai_tool_call_id',
                timestamp=datetime.datetime(...),
                part_kind='tool-return',
            )
        ],
        instructions=None,
        kind='request',
    ),
    ModelResponse(
        parts=[
            TextPart(
                content="Congratulations Anne, you guessed correctly! You're a winner!",
                part_kind='text',
            )
        ],
        usage=Usage(
            requests=1,
            request_tokens=92,
            response_tokens=12,
            total_tokens=104,
            details=None,
        ),
        model_name='gemini-1.5-flash',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""

```

We can represent this with a diagram:

```
sequenceDiagram
    participant Agent
    participant LLM

    Note over Agent: Send prompts
    Agent ->> LLM: System: "You're a dice game..."<br>User: "My guess is 4"
    activate LLM
    Note over LLM: LLM decides to use<br>a tool

    LLM ->> Agent: Call tool<br>roll_die()
    deactivate LLM
    activate Agent
    Note over Agent: Rolls a six-sided die

    Agent -->> LLM: ToolReturn<br>"4"
    deactivate Agent
    activate LLM
    Note over LLM: LLM decides to use<br>another tool

    LLM ->> Agent: Call tool<br>get_player_name()
    deactivate LLM
    activate Agent
    Note over Agent: Retrieves player name
    Agent -->> LLM: ToolReturn<br>"Anne"
    deactivate Agent
    activate LLM
    Note over LLM: LLM constructs final response

    LLM ->> Agent: ModelResponse<br>"Congratulations Anne, ..."
    deactivate LLM
    Note over Agent: Game session complete
```

## Registering Function Tools via Agent Argument

As well as using the decorators, we can register tools via the `tools` argument to the Agent constructor. This is useful when you want to reuse tools, and can also give more fine-grained control over the tools.

dice_game_tool_kwarg.py

```python
import random

from pydantic_ai import Agent, RunContext, Tool

system_prompt = """\
You're a dice game, you should roll the die and see if the number
you get back matches the user's guess. If so, tell them they're a winner.
Use the player's name in the response.
"""


def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))


def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps


agent_a = Agent(
    'google-gla:gemini-1.5-flash',
    deps_type=str,
    tools=[roll_die, get_player_name],  # (1)!
    system_prompt=system_prompt,
)
agent_b = Agent(
    'google-gla:gemini-1.5-flash',
    deps_type=str,
    tools=[  # (2)!
        Tool(roll_die, takes_ctx=False),
        Tool(get_player_name, takes_ctx=True),
    ],
    system_prompt=system_prompt,
)

dice_result = {}
dice_result['a'] = agent_a.run_sync('My guess is 6', deps='Yashar')
dice_result['b'] = agent_b.run_sync('My guess is 4', deps='Anne')
print(dice_result['a'].output)
#> Tough luck, Yashar, you rolled a 4. Better luck next time.
print(dice_result['b'].output)
#> Congratulations Anne, you guessed correctly! You're a winner!

```

1. The simplest way to register tools via the `Agent` constructor is to pass a list of functions, the function signature is inspected to determine if the tool takes RunContext.
1. `agent_a` and `agent_b` are identical â€” but we can use Tool to reuse tool definitions and give more fine-grained control over how tools are defined, e.g. setting their name or description, or using a custom [`prepare`](#tool-prepare) method.

*(This example is complete, it can be run "as is")*

## Function Tool Output

Tools can return anything that Pydantic can serialize to JSON, as well as audio, video, image or document content depending on the types of [multi-modal input](../input/) the model supports:

function_tool_output.py

```python
from datetime import datetime

from pydantic import BaseModel

from pydantic_ai import Agent, DocumentUrl, ImageUrl
from pydantic_ai.models.openai import OpenAIResponsesModel


class User(BaseModel):
    name: str
    age: int


agent = Agent(model=OpenAIResponsesModel('gpt-4o'))


@agent.tool_plain
def get_current_time() -> datetime:
    return datetime.now()


@agent.tool_plain
def get_user() -> User:
    return User(name='John', age=30)


@agent.tool_plain
def get_company_logo() -> ImageUrl:
    return ImageUrl(url='https://iili.io/3Hs4FMg.png')


@agent.tool_plain
def get_document() -> DocumentUrl:
    return DocumentUrl(url='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf')


result = agent.run_sync('What time is it?')
print(result.output)
#> The current time is 10:45 PM on April 17, 2025.

result = agent.run_sync('What is the user name?')
print(result.output)
#> The user's name is John.

result = agent.run_sync('What is the company name in the logo?')
print(result.output)
#> The company name in the logo is "Pydantic."

result = agent.run_sync('What is the main content of the document?')
print(result.output)
#> The document contains just the text "Dummy PDF file."

```

*(This example is complete, it can be run "as is")*

Some models (e.g. Gemini) natively support semi-structured return values, while some expect text (OpenAI) but seem to be just as good at extracting meaning from the data. If a Python object is returned and the model expects a string, the value will be serialized to JSON.

## Function Tools vs. Structured Outputs

As the name suggests, function tools use the model's "tools" or "functions" API to let the model know what is available to call. Tools or functions are also used to define the schema(s) for structured responses, thus a model might have access to many tools, some of which call function tools while others end the run and produce a final output.

## Function tools and schema

Function parameters are extracted from the function signature, and all parameters except `RunContext` are used to build the schema for that tool call.

Even better, PydanticAI extracts the docstring from functions and (thanks to [griffe](https://mkdocstrings.github.io/griffe/)) extracts parameter descriptions from the docstring and adds them to the schema.

[Griffe supports](https://mkdocstrings.github.io/griffe/reference/docstrings/#docstrings) extracting parameter descriptions from `google`, `numpy`, and `sphinx` style docstrings. PydanticAI will infer the format to use based on the docstring, but you can explicitly set it using docstring_format. You can also enforce parameter requirements by setting `require_parameter_descriptions=True`. This will raise a UserError if a parameter description is missing.

To demonstrate a tool's schema, here we use FunctionModel to print the schema a model would receive:

tool_schema.py

```python
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

agent = Agent()


@agent.tool_plain(docstring_format='google', require_parameter_descriptions=True)
def foobar(a: int, b: str, c: dict[str, list[float]]) -> str:
    """Get me foobar.

    Args:
        a: apple pie
        b: banana cake
        c: carrot smoothie
    """
    return f'{a} {b} {c}'


def print_schema(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    tool = info.function_tools[0]
    print(tool.description)
    #> Get me foobar.
    print(tool.parameters_json_schema)
    """
    {
        'additionalProperties': False,
        'properties': {
            'a': {'description': 'apple pie', 'type': 'integer'},
            'b': {'description': 'banana cake', 'type': 'string'},
            'c': {
                'additionalProperties': {'items': {'type': 'number'}, 'type': 'array'},
                'description': 'carrot smoothie',
                'type': 'object',
            },
        },
        'required': ['a', 'b', 'c'],
        'type': 'object',
    }
    """
    return ModelResponse(parts=[TextPart('foobar')])


agent.run_sync('hello', model=FunctionModel(print_schema))

```

*(This example is complete, it can be run "as is")*

If a tool has a single parameter that can be represented as an object in JSON schema (e.g. dataclass, TypedDict, pydantic model), the schema for the tool is simplified to be just that object.

Here's an example where we use TestModel.last_model_request_parameters to inspect the tool schema that would be passed to the model.

single_parameter_tool.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agent = Agent()


class Foobar(BaseModel):
    """This is a Foobar"""

    x: int
    y: str
    z: float = 3.14


@agent.tool_plain
def foobar(f: Foobar) -> str:
    return str(f)


test_model = TestModel()
result = agent.run_sync('hello', model=test_model)
print(result.output)
#> {"foobar":"x=0 y='a' z=3.14"}
print(test_model.last_model_request_parameters.function_tools)
"""
[
    ToolDefinition(
        name='foobar',
        description='This is a Foobar',
        parameters_json_schema={
            'properties': {
                'x': {'type': 'integer'},
                'y': {'type': 'string'},
                'z': {'default': 3.14, 'type': 'number'},
            },
            'required': ['x', 'y'],
            'title': 'Foobar',
            'type': 'object',
        },
        outer_typed_dict_key=None,
        strict=None,
    )
]
"""

```

*(This example is complete, it can be run "as is")*

## Dynamic Function tools

Tools can optionally be defined with another function: `prepare`, which is called at each step of a run to customize the definition of the tool passed to the model, or omit the tool completely from that step.

A `prepare` method can be registered via the `prepare` kwarg to any of the tool registration mechanisms:

- @agent.tool decorator
- @agent.tool_plain decorator
- Tool dataclass

The `prepare` method, should be of type ToolPrepareFunc, a function which takes RunContext and a pre-built ToolDefinition, and should either return that `ToolDefinition` with or without modifying it, return a new `ToolDefinition`, or return `None` to indicate this tools should not be registered for that step.

Here's a simple `prepare` method that only includes the tool if the value of the dependency is `42`.

As with the previous example, we use TestModel to demonstrate the behavior without calling a real model.

tool_only_if_42.py

```python
from typing import Union

from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition

agent = Agent('test')


async def only_if_42(
    ctx: RunContext[int], tool_def: ToolDefinition
) -> Union[ToolDefinition, None]:
    if ctx.deps == 42:
        return tool_def


@agent.tool(prepare=only_if_42)
def hitchhiker(ctx: RunContext[int], answer: str) -> str:
    return f'{ctx.deps} {answer}'


result = agent.run_sync('testing...', deps=41)
print(result.output)
#> success (no tool calls)
result = agent.run_sync('testing...', deps=42)
print(result.output)
#> {"hitchhiker":"42 a"}

```

*(This example is complete, it can be run "as is")*

Here's a more complex example where we change the description of the `name` parameter to based on the value of `deps`

For the sake of variation, we create this tool using the Tool dataclass.

customize_name.py

```python
from __future__ import annotations

from typing import Literal

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel
from pydantic_ai.tools import Tool, ToolDefinition


def greet(name: str) -> str:
    return f'hello {name}'


async def prepare_greet(
    ctx: RunContext[Literal['human', 'machine']], tool_def: ToolDefinition
) -> ToolDefinition | None:
    d = f'Name of the {ctx.deps} to greet.'
    tool_def.parameters_json_schema['properties']['name']['description'] = d
    return tool_def


greet_tool = Tool(greet, prepare=prepare_greet)
test_model = TestModel()
agent = Agent(test_model, tools=[greet_tool], deps_type=Literal['human', 'machine'])

result = agent.run_sync('testing...', deps='human')
print(result.output)
#> {"greet":"hello a"}
print(test_model.last_model_request_parameters.function_tools)
"""
[
    ToolDefinition(
        name='greet',
        description='',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {
                'name': {'type': 'string', 'description': 'Name of the human to greet.'}
            },
            'required': ['name'],
            'type': 'object',
        },
        outer_typed_dict_key=None,
        strict=None,
    )
]
"""

```

*(This example is complete, it can be run "as is")*

## Tool Execution and Retries

When a tool is executed, its arguments (provided by the LLM) are first validated against the function's signature using Pydantic. If validation fails (e.g., due to incorrect types or missing required arguments), a `ValidationError` is raised, and the framework automatically generates a RetryPromptPart containing the validation details. This prompt is sent back to the LLM, informing it of the error and allowing it to correct the parameters and retry the tool call.

Beyond automatic validation errors, the tool's own internal logic can also explicitly request a retry by raising the ModelRetry exception. This is useful for situations where the parameters were technically valid, but an issue occurred during execution (like a transient network error, or the tool determining the initial attempt needs modification).

```python
from pydantic_ai import ModelRetry


def my_flaky_tool(query: str) -> str:
    if query == 'bad':
        # Tell the LLM the query was bad and it should try again
        raise ModelRetry("The query 'bad' is not allowed. Please provide a different query.")
    # ... process query ...
    return 'Success!'

```

Raising `ModelRetry` also generates a `RetryPromptPart` containing the exception message, which is sent back to the LLM to guide its next attempt. Both `ValidationError` and `ModelRetry` respect the `retries` setting configured on the `Tool` or `Agent`.
# Models

# Model Providers

PydanticAI is model-agnostic and has built-in support for multiple model providers:

- [OpenAI](openai/)
- [DeepSeek](openai/#openai-compatible-models)
- [Anthropic](anthropic/)
- [Gemini](gemini/) (via two different APIs: Generative Language API and VertexAI API)
- [Ollama](openai/#ollama)
- [Groq](groq/)
- [Mistral](mistral/)
- [Cohere](cohere/)
- [Bedrock](bedrock/)

## OpenAI-compatible Providers

Many models are compatible with the OpenAI API, and can be used with `OpenAIModel` in PydanticAI:

- [OpenRouter](openai/#openrouter)
- [Grok (xAI)](openai/#grok-xai)
- [Perplexity](openai/#perplexity)
- [Fireworks AI](openai/#fireworks-ai)
- [Together AI](openai/#together-ai)
- [Azure AI Foundry](openai/#azure-ai-foundry)

PydanticAI also comes with [`TestModel`](../api/models/test/) and [`FunctionModel`](../api/models/function/) for testing and development.

To use each model provider, you need to configure your local environment and make sure you have the right packages installed.

## Models and Providers

PydanticAI uses a few key terms to describe how it interacts with different LLMs:

- **Model**: This refers to the PydanticAI class used to make requests following a specific LLM API (generally by wrapping a vendor-provided SDK, like the `openai` python SDK). These classes implement a vendor-SDK-agnostic API, ensuring a single PydanticAI agent is portable to different LLM vendors without any other code changes just by swapping out the Model it uses. Model classes are named roughly in the format `<VendorSdk>Model`, for example, we have `OpenAIModel`, `AnthropicModel`, `GeminiModel`, etc. When using a Model class, you specify the actual LLM model name (e.g., `gpt-4o`, `claude-3-5-sonnet-latest`, `gemini-1.5-flash`) as a parameter.
- **Provider**: This refers to Model-specific classes which handle the authentication and connections to an LLM vendor. Passing a non-default *Provider* as a parameter to a Model is how you can ensure that your agent will make requests to a specific endpoint, or make use of a specific approach to authentication (e.g., you can use Vertex-specific auth with the `GeminiModel` by way of the `VertexProvider`). In particular, this is how you can make use of an AI gateway, or an LLM vendor that offers API compatibility with the vendor SDK used by an existing Model (such as `OpenAIModel`).

In short, you select a specific model name (like `gpt-4o`), PydanticAI uses the appropriate Model class (like `OpenAIModel`), and the provider handles the connection and authentication to the underlying service.

## Custom Models

To implement support for models not already supported, you will need to subclass the Model abstract base class.

For streaming, you'll also need to implement the following abstract base class:

- StreamedResponse

The best place to start is to review the source code for existing implementations, e.g. [`OpenAIModel`](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/models/openai.py).

For details on when we'll accept contributions adding new models to PydanticAI, see the [contributing guidelines](../contributing/#new-model-rules).

## Fallback Model

You can use FallbackModel to attempt multiple models in sequence until one successfully returns a result. Under the hood, PydanticAI automatically switches from one model to the next if the current model returns a 4xx or 5xx status code.

In the following example, the agent first makes a request to the OpenAI model (which fails due to an invalid API key), and then falls back to the Anthropic model.

fallback_model.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIModel

openai_model = OpenAIModel('gpt-4o')
anthropic_model = AnthropicModel('claude-3-5-sonnet-latest')
fallback_model = FallbackModel(openai_model, anthropic_model)

agent = Agent(fallback_model)
response = agent.run_sync('What is the capital of France?')
print(response.data)
#> Paris

print(response.all_messages())
"""
[
    ModelRequest(
        parts=[
            UserPromptPart(
                content='What is the capital of France?',
                timestamp=datetime.datetime(...),
                part_kind='user-prompt',
            )
        ],
        kind='request',
    ),
    ModelResponse(
        parts=[TextPart(content='Paris', part_kind='text')],
        model_name='claude-3-5-sonnet-latest',
        timestamp=datetime.datetime(...),
        kind='response',
    ),
]
"""

```

The `ModelResponse` message above indicates in the `model_name` field that the output was returned by the Anthropic model, which is the second model specified in the `FallbackModel`.

Note

Each model's options should be configured individually. For example, `base_url`, `api_key`, and custom clients should be set on each model itself, not on the `FallbackModel`.

In this next example, we demonstrate the exception-handling capabilities of `FallbackModel`. If all models fail, a FallbackExceptionGroup is raised, which contains all the exceptions encountered during the `run` execution.

fallback_model_failure.py

```python
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIModel

openai_model = OpenAIModel('gpt-4o')
anthropic_model = AnthropicModel('claude-3-5-sonnet-latest')
fallback_model = FallbackModel(openai_model, anthropic_model)

agent = Agent(fallback_model)
try:
    response = agent.run_sync('What is the capital of France?')
except* ModelHTTPError as exc_group:
    for exc in exc_group.exceptions:
        print(exc)

```

Since [`except*`](https://docs.python.org/3/reference/compound_stmts.html#except-star) is only supported in Python 3.11+, we use the [`exceptiongroup`](https://github.com/agronholm/exceptiongroup) backport package for earlier Python versions:

fallback_model_failure.py

```python
from exceptiongroup import catch

from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIModel


def model_status_error_handler(exc_group: BaseExceptionGroup) -> None:
    for exc in exc_group.exceptions:
        print(exc)


openai_model = OpenAIModel('gpt-4o')
anthropic_model = AnthropicModel('claude-3-5-sonnet-latest')
fallback_model = FallbackModel(openai_model, anthropic_model)

agent = Agent(fallback_model)
with catch({ModelHTTPError: model_status_error_handler}):
    response = agent.run_sync('What is the capital of France?')

```

By default, the `FallbackModel` only moves on to the next model if the current model raises a ModelHTTPError. You can customize this behavior by passing a custom `fallback_on` argument to the `FallbackModel` constructor.

# Anthropic

## Install

To use `AnthropicModel` models, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `anthropic` optional group:

```bash
pip install "pydantic-ai-slim[anthropic]"

```

```bash
uv add "pydantic-ai-slim[anthropic]"

```

## Configuration

To use [Anthropic](https://anthropic.com) through their API, go to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) to generate an API key.

`AnthropicModelName` contains a list of available Anthropic models.

## Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key'

```

You can then use `AnthropicModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('anthropic:claude-3-5-sonnet-latest')
...

```

Or initialise the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

model = AnthropicModel('claude-3-5-sonnet-latest')
agent = Agent(model)
...

```

## `provider` argument

You can provide a custom `Provider` via the `provider` argument:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

model = AnthropicModel(
    'claude-3-5-sonnet-latest', provider=AnthropicProvider(api_key='your-api-key')
)
agent = Agent(model)
...

```

## Custom HTTP Client

You can customize the `AnthropicProvider` with a custom `httpx.AsyncClient`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

custom_http_client = AsyncClient(timeout=30)
model = AnthropicModel(
    'claude-3-5-sonnet-latest',
    provider=AnthropicProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...

```

# Bedrock

## Install

To use `BedrockConverseModel`, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `bedrock` optional group:

```bash
pip install "pydantic-ai-slim[bedrock]"

```

```bash
uv add "pydantic-ai-slim[bedrock]"

```

## Configuration

To use [AWS Bedrock](https://aws.amazon.com/bedrock/), you'll need an AWS account with Bedrock enabled and appropriate credentials. You can use either AWS credentials directly or a pre-configured boto3 client.

`BedrockModelName` contains a list of available Bedrock models, including models from Anthropic, Amazon, Cohere, Meta, and Mistral.

## Environment variables

You can set your AWS credentials as environment variables ([among other options](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables)):

```bash
export AWS_ACCESS_KEY_ID='your-access-key'
export AWS_SECRET_ACCESS_KEY='your-secret-key'
export AWS_DEFAULT_REGION='us-east-1'  # or your preferred region

```

You can then use `BedrockConverseModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('bedrock:anthropic.claude-3-sonnet-20240229-v1:0')
...

```

Or initialize the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel

model = BedrockConverseModel('anthropic.claude-3-sonnet-20240229-v1:0')
agent = Agent(model)
...

```

## Customizing Bedrock Runtime API

You can customize the Bedrock Runtime API calls by adding additional parameters, such as [guardrail configurations](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) and [performance settings](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html). For a complete list of configurable parameters, refer to the documentation for BedrockModelSettings.

customize_bedrock_model_settings.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings

# Define Bedrock model settings with guardrail and performance configurations
bedrock_model_settings = BedrockModelSettings(
    bedrock_guardrail_config={
        'guardrailIdentifier': 'v1',
        'guardrailVersion': 'v1',
        'trace': 'enabled'
    },
    bedrock_performance_configuration={
        'latency': 'optimized'
    }
)


model = BedrockConverseModel(model_name='us.amazon.nova-pro-v1:0')

agent = Agent(model=model, model_settings=bedrock_model_settings)

```

## `provider` argument

You can provide a custom `BedrockProvider` via the `provider` argument. This is useful when you want to specify credentials directly or use a custom boto3 client:

```python
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider

# Using AWS credentials directly
model = BedrockConverseModel(
    'anthropic.claude-3-sonnet-20240229-v1:0',
    provider=BedrockProvider(
        region_name='us-east-1',
        aws_access_key_id='your-access-key',
        aws_secret_access_key='your-secret-key',
    ),
)
agent = Agent(model)
...

```

You can also pass a pre-configured boto3 client:

```python
import boto3

from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider

# Using a pre-configured boto3 client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
model = BedrockConverseModel(
    'anthropic.claude-3-sonnet-20240229-v1:0',
    provider=BedrockProvider(bedrock_client=bedrock_client),
)
agent = Agent(model)
...

```

# Cohere

## Install

To use `CohereModel`, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `cohere` optional group:

```bash
pip install "pydantic-ai-slim[cohere]"

```

```bash
uv add "pydantic-ai-slim[cohere]"

```

## Configuration

To use [Cohere](https://cohere.com/) through their API, go to [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys) and follow your nose until you find the place to generate an API key.

`CohereModelName` contains a list of the most popular Cohere models.

## Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export CO_API_KEY='your-api-key'

```

You can then use `CohereModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('cohere:command')
...

```

Or initialise the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel

model = CohereModel('command')
agent = Agent(model)
...

```

## `provider` argument

You can provide a custom `Provider` via the `provider` argument:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.providers.cohere import CohereProvider

model = CohereModel('command', provider=CohereProvider(api_key='your-api-key'))
agent = Agent(model)
...

```

You can also customize the `CohereProvider` with a custom `http_client`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.providers.cohere import CohereProvider

custom_http_client = AsyncClient(timeout=30)
model = CohereModel(
    'command',
    provider=CohereProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...

```

# Gemini

PydanticAI supports Google's Gemini models through two different APIs:

- Generative Language API (`generativelanguage.googleapis.com`)
- Vertex AI API (`*-aiplatform.googleapis.com`)

## Gemini via Generative Language API

### Install

To use `GeminiModel` models, you just need to install `pydantic-ai` or `pydantic-ai-slim`, no extra dependencies are required.

### Configuration

`GeminiModel` lets you use Google's Gemini models through their [Generative Language API](https://ai.google.dev/api/all-methods), `generativelanguage.googleapis.com`.

`GeminiModelName` contains a list of available Gemini models that can be used through this interface.

To use `GeminiModel`, go to [aistudio.google.com](https://aistudio.google.com/apikey) and select "Create API key".

### Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export GEMINI_API_KEY=your-api-key

```

You can then use `GeminiModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('google-gla:gemini-2.0-flash')
...

```

Note

The `google-gla` provider prefix represents the [Google **G**enerative **L**anguage **A**PI](https://ai.google.dev/api/all-methods) for `GeminiModel`s. `google-vertex` is used with [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models).

Or initialise the model directly with just the model name and provider:

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel('gemini-2.0-flash', provider='google-gla')
agent = Agent(model)
...

```

### `provider` argument

You can provide a custom `Provider` via the `provider` argument:

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

model = GeminiModel(
    'gemini-2.0-flash', provider=GoogleGLAProvider(api_key='your-api-key')
)
agent = Agent(model)
...

```

You can also customize the `GoogleGLAProvider` with a custom `http_client`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

custom_http_client = AsyncClient(timeout=30)
model = GeminiModel(
    'gemini-2.0-flash',
    provider=GoogleGLAProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...

```

## Gemini via VertexAI

If you are an enterprise user, you should use the `google-vertex` provider with `GeminiModel` which uses the `*-aiplatform.googleapis.com` API.

`GeminiModelName` contains a list of available Gemini models that can be used through this interface.

### Install

To use the `google-vertex` provider with `GeminiModel`, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `vertexai` optional group:

```bash
pip install "pydantic-ai-slim[vertexai]"

```

```bash
uv add "pydantic-ai-slim[vertexai]"

```

### Configuration

This interface has a number of advantages over `generativelanguage.googleapis.com` documented above:

1. The VertexAI API comes with more enterprise readiness guarantees.
1. You can [purchase provisioned throughput](https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput#purchase-provisioned-throughput) with VertexAI to guarantee capacity.
1. If you're running PydanticAI inside GCP, you don't need to set up authentication, it should "just work".
1. You can decide which region to use, which might be important from a regulatory perspective, and might improve latency.

The big disadvantage is that for local development you may need to create and configure a "service account", which can be challenging to get right.

Whichever way you authenticate, you'll need to have VertexAI enabled in your GCP account.

### Application default credentials

Luckily if you're running PydanticAI inside GCP, or you have the [`gcloud` CLI](https://cloud.google.com/sdk/gcloud) installed and configured, you should be able to use `VertexAIModel` without any additional setup.

To use `VertexAIModel`, with [application default credentials](https://cloud.google.com/docs/authentication/application-default-credentials) configured (e.g. with `gcloud`), you can simply use:

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel('gemini-2.0-flash', provider='google-vertex')
agent = Agent(model)
...

```

Internally this uses [`google.auth.default()`](https://google-auth.readthedocs.io/en/master/reference/google.auth.html) from the `google-auth` package to obtain credentials.

Won't fail until `agent.run()`

Because `google.auth.default()` requires network requests and can be slow, it's not run until you call `agent.run()`.

You may also need to pass the `project_id` argument to `GoogleVertexProvider` if application default credentials don't set a project, if you pass `project_id` and it conflicts with the project set by application default credentials, an error is raised.

### Service account

If instead of application default credentials, you want to authenticate with a service account, you'll need to create a service account, add it to your GCP project (note: this step is necessary even if you created the service account within the project), give that service account the "Vertex AI Service Agent" role, and download the service account JSON file.

Once you have the JSON file, you can use it thus:

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider

model = GeminiModel(
    'gemini-2.0-flash',
    provider=GoogleVertexProvider(service_account_file='path/to/service-account.json'),
)
agent = Agent(model)
...

```

Alternatively, if you already have the service account information in memory, you can pass it as a dictionary:

```python
import json

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider

service_account_info = json.loads(
    '{"type": "service_account", "project_id": "my-project-id"}'
)
model = GeminiModel(
    'gemini-2.0-flash',
    provider=GoogleVertexProvider(service_account_info=service_account_info),
)
agent = Agent(model)
...

```

### Customising region

Whichever way you authenticate, you can specify which region requests will be sent to via the `region` argument.

Using a region close to your application can improve latency and might be important from a regulatory perspective.

```python
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider

model = GeminiModel(
    'gemini-2.0-flash', provider=GoogleVertexProvider(region='asia-east1')
)
agent = Agent(model)
...

```

You can also customize the `GoogleVertexProvider` with a custom `http_client`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider

custom_http_client = AsyncClient(timeout=30)
model = GeminiModel(
    'gemini-2.0-flash',
    provider=GoogleVertexProvider(region='asia-east1', http_client=custom_http_client),
)
agent = Agent(model)
...

```

# Groq

## Install

To use `GroqModel`, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `groq` optional group:

```bash
pip install "pydantic-ai-slim[groq]"

```

```bash
uv add "pydantic-ai-slim[groq]"

```

## Configuration

To use [Groq](https://groq.com/) through their API, go to [console.groq.com/keys](https://console.groq.com/keys) and follow your nose until you find the place to generate an API key.

`GroqModelName` contains a list of available Groq models.

## Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export GROQ_API_KEY='your-api-key'

```

You can then use `GroqModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('groq:llama-3.3-70b-versatile')
...

```

Or initialise the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

model = GroqModel('llama-3.3-70b-versatile')
agent = Agent(model)
...

```

## `provider` argument

You can provide a custom `Provider` via the `provider` argument:

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

model = GroqModel(
    'llama-3.3-70b-versatile', provider=GroqProvider(api_key='your-api-key')
)
agent = Agent(model)
...

```

You can also customize the `GroqProvider` with a custom `httpx.AsyncHTTPClient`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

custom_http_client = AsyncClient(timeout=30)
model = GroqModel(
    'llama-3.3-70b-versatile',
    provider=GroqProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...

```

# Mistral

## Install

To use `MistralModel`, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `mistral` optional group:

```bash
pip install "pydantic-ai-slim[mistral]"

```

```bash
uv add "pydantic-ai-slim[mistral]"

```

## Configuration

To use [Mistral](https://mistral.ai) through their API, go to [console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/) and follow your nose until you find the place to generate an API key.

`LatestMistralModelNames` contains a list of the most popular Mistral models.

## Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export MISTRAL_API_KEY='your-api-key'

```

You can then use `MistralModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('mistral:mistral-large-latest')
...

```

Or initialise the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

model = MistralModel('mistral-small-latest')
agent = Agent(model)
...

```

## `provider` argument

You can provide a custom `Provider` via the `provider` argument:

```python
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

model = MistralModel(
    'mistral-large-latest', provider=MistralProvider(api_key='your-api-key', base_url='https://<mistral-provider-endpoint>')
)
agent = Agent(model)
...

```

You can also customize the provider with a custom `httpx.AsyncHTTPClient`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

custom_http_client = AsyncClient(timeout=30)
model = MistralModel(
    'mistral-large-latest',
    provider=MistralProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...

```

# OpenAI

## Install

To use OpenAI models, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `openai` optional group:

```bash
pip install "pydantic-ai-slim[openai]"

```

```bash
uv add "pydantic-ai-slim[openai]"

```

## Configuration

To use `OpenAIModel` through their main API, go to [platform.openai.com](https://platform.openai.com/) and follow your nose until you find the place to generate an API key.

## Environment variable

Once you have the API key, you can set it as an environment variable:

```bash
export OPENAI_API_KEY='your-api-key'

```

You can then use `OpenAIModel` by name:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')
...

```

Or initialise the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel('gpt-4o')
agent = Agent(model)
...

```

By default, the `OpenAIModel` uses the `OpenAIProvider` with the `base_url` set to `https://api.openai.com/v1`.

## Configure the provider

If you want to pass parameters in code to the provider, you can programmatically instantiate the OpenAIProvider and pass it to the model:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel('gpt-4o', provider=OpenAIProvider(api_key='your-api-key'))
agent = Agent(model)
...

```

## Custom OpenAI Client

`OpenAIProvider` also accepts a custom `AsyncOpenAI` client via the `openai_client` parameter, so you can customise the `organization`, `project`, `base_url` etc. as defined in the [OpenAI API docs](https://platform.openai.com/docs/api-reference).

You could also use the [`AsyncAzureOpenAI`](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints) client to use the Azure OpenAI API.

```python
from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)

model = OpenAIModel(
    'gpt-4o',
    provider=OpenAIProvider(openai_client=client),
)
agent = Agent(model)
...

```

## OpenAI Responses API

PydanticAI also supports OpenAI's [Responses API](https://platform.openai.com/docs/api-reference/responses) through the `OpenAIResponsesModel` class.

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel

model = OpenAIResponsesModel('gpt-4o')
agent = Agent(model)
...

```

The Responses API has built-in tools that you can use instead of building your own:

- [Web search](https://platform.openai.com/docs/guides/tools-web-search): allow models to search the web for the latest information before generating a response.
- [File search](https://platform.openai.com/docs/guides/tools-file-search): allow models to search your files for relevant information before generating a response.
- [Computer use](https://platform.openai.com/docs/guides/tools-computer-use): allow models to use a computer to perform tasks on your behalf.

You can use the `OpenAIResponsesModelSettings` class to make use of those built-in tools:

```python
from openai.types.responses import WebSearchToolParam  # (1)!

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model_settings = OpenAIResponsesModelSettings(
    openai_builtin_tools=[WebSearchToolParam(type='web_search_preview')],
)
model = OpenAIResponsesModel('gpt-4o')
agent = Agent(model=model, model_settings=model_settings)

result = agent.run_sync('What is the weather in Tokyo?')
print(result.output)
"""
As of 7:48 AM on Wednesday, April 2, 2025, in Tokyo, Japan, the weather is cloudy with a temperature of 53Â°F (12Â°C).
"""

```

1. The file search tool and computer use tool can also be imported from `openai.types.responses`.

You can learn more about the differences between the Responses API and Chat Completions API in the [OpenAI API docs](https://platform.openai.com/docs/guides/responses-vs-chat-completions).

## OpenAI-compatible Models

Many models are compatible with the OpenAI API, and can be used with `OpenAIModel` in PydanticAI. Before getting started, check the [installation and configuration](#install) instructions above.

To use another OpenAI-compatible API, you can make use of the `base_url` and `api_key` arguments from `OpenAIProvider`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    'model_name',
    provider=OpenAIProvider(
        base_url='https://<openai-compatible-api-endpoint>.com', api_key='your-api-key'
    ),
)
agent = Agent(model)
...

```

You can also use the `provider` argument with a custom provider class like the `DeepSeekProvider`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

model = OpenAIModel(
    'deepseek-chat',
    provider=DeepSeekProvider(api_key='your-deepseek-api-key'),
)
agent = Agent(model)
...

```

You can also customize any provider with a custom `http_client`:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

custom_http_client = AsyncClient(timeout=30)
model = OpenAIModel(
    'deepseek-chat',
    provider=DeepSeekProvider(
        api_key='your-deepseek-api-key', http_client=custom_http_client
    ),
)
agent = Agent(model)
...

```

### Ollama

To use [Ollama](https://ollama.com/), you must first download the Ollama client, and then download a model using the [Ollama model library](https://ollama.com/library).

You must also ensure the Ollama server is running when trying to make requests to it. For more information, please see the [Ollama documentation](https://github.com/ollama/ollama/tree/main/docs).

#### Example local usage

With `ollama` installed, you can run the server with the model you want to use:

```bash
ollama run llama3.2

```

(this will pull the `llama3.2` model if you don't already have it downloaded)

Then run your code, here's a minimal example:

```python
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


class CityLocation(BaseModel):
    city: str
    country: str


ollama_model = OpenAIModel(
    model_name='llama3.2', provider=OpenAIProvider(base_url='http://localhost:11434/v1')
)
agent = Agent(ollama_model, output_type=CityLocation)

result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
print(result.usage())
"""
Usage(requests=1, request_tokens=57, response_tokens=8, total_tokens=65, details=None)
"""

```

#### Example using a remote server

```python
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

ollama_model = OpenAIModel(
    model_name='qwen2.5-coder:7b',  # (1)!
    provider=OpenAIProvider(base_url='http://192.168.1.74:11434/v1'),  # (2)!
)


class CityLocation(BaseModel):
    city: str
    country: str


agent = Agent(model=ollama_model, output_type=CityLocation)

result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
print(result.usage())
"""
Usage(requests=1, request_tokens=57, response_tokens=8, total_tokens=65, details=None)
"""

```

1. The name of the model running on the remote server
1. The url of the remote server

### Azure AI Foundry

If you want to use [Azure AI Foundry](https://ai.azure.com/) as your provider, you can do so by using the `AzureProvider` class.

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.azure import AzureProvider

model = OpenAIModel(
    'gpt-4o',
    provider=AzureProvider(
        azure_endpoint='your-azure-endpoint',
        api_version='your-api-version',
        api_key='your-api-key',
    ),
)
agent = Agent(model)
...

```

### OpenRouter

To use [OpenRouter](https://openrouter.ai), first create an API key at [openrouter.ai/keys](https://openrouter.ai/keys).

Once you have the API key, you can use it with the `OpenAIProvider`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    'anthropic/claude-3.5-sonnet',
    provider=OpenAIProvider(
        base_url='https://openrouter.ai/api/v1',
        api_key='your-openrouter-api-key',
    ),
)
agent = Agent(model)
...

```

### Grok (xAI)

Go to [xAI API Console](https://console.x.ai/) and create an API key. Once you have the API key, you can use it with the `OpenAIProvider`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    'grok-2-1212',
    provider=OpenAIProvider(base_url='https://api.x.ai/v1', api_key='your-xai-api-key'),
)
agent = Agent(model)
...

```

### Perplexity

Follow the Perplexity [getting started](https://docs.perplexity.ai/guides/getting-started) guide to create an API key. Then, you can query the Perplexity API with the following:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    'sonar-pro',
    provider=OpenAIProvider(
        base_url='https://api.perplexity.ai',
        api_key='your-perplexity-api-key',
    ),
)
agent = Agent(model)
...

```

### Fireworks AI

Go to [Fireworks.AI](https://fireworks.ai/) and create an API key in your account settings. Once you have the API key, you can use it with the `OpenAIProvider`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    'accounts/fireworks/models/qwq-32b',  # model library available at https://fireworks.ai/models
    provider=OpenAIProvider(
        base_url='https://api.fireworks.ai/inference/v1',
        api_key='your-fireworks-api-key',
    ),
)
agent = Agent(model)
...

```

### Together AI

Go to [Together.ai](https://www.together.ai/) and create an API key in your account settings. Once you have the API key, you can use it with the `OpenAIProvider`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIModel(
    'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free',  # model library available at https://www.together.ai/models
    provider=OpenAIProvider(
        base_url='https://api.together.xyz/v1',
        api_key='your-together-api-key',
    ),
)
agent = Agent(model)
...

```
# Graphs

# Graphs

Don't use a nail gun unless you need a nail gun

If PydanticAI [agents](../agents/) are a hammer, and [multi-agent workflows](../multi-agent-applications/) are a sledgehammer, then graphs are a nail gun:

- sure, nail guns look cooler than hammers
- but nail guns take a lot more setup than hammers
- and nail guns don't make you a better builder, they make you a builder with a nail gun
- Lastly, (and at the risk of torturing this metaphor), if you're a fan of medieval tools like mallets and untyped Python, you probably won't like nail guns or our approach to graphs. (But then again, if you're not a fan of type hints in Python, you've probably already bounced off PydanticAI to use one of the toy agent frameworks â€” good luck, and feel free to borrow my sledgehammer when you realize you need it)

In short, graphs are a powerful tool, but they're not the right tool for every job. Please consider other [multi-agent approaches](../multi-agent-applications/) before proceeding.

If you're not confident a graph-based approach is a good idea, it might be unnecessary.

Graphs and finite state machines (FSMs) are a powerful abstraction to model, execute, control and visualize complex workflows.

Alongside PydanticAI, we've developed `pydantic-graph` â€” an async graph and state machine library for Python where nodes and edges are defined using type hints.

While this library is developed as part of PydanticAI; it has no dependency on `pydantic-ai` and can be considered as a pure graph-based state machine library. You may find it useful whether or not you're using PydanticAI or even building with GenAI.

`pydantic-graph` is designed for advanced users and makes heavy use of Python generics and type hints. It is not designed to be as beginner-friendly as PydanticAI.

## Installation

`pydantic-graph` is a required dependency of `pydantic-ai`, and an optional dependency of `pydantic-ai-slim`, see [installation instructions](../install/#slim-install) for more information. You can also install it directly:

```bash
pip install pydantic-graph

```

```bash
uv add pydantic-graph

```

## Graph Types

`pydantic-graph` is made up of a few key components:

### GraphRunContext

GraphRunContext â€” The context for the graph run, similar to PydanticAI's RunContext. This holds the state of the graph and dependencies and is passed to nodes when they're run.

`GraphRunContext` is generic in the state type of the graph it's used in, StateT.

### End

End â€” return value to indicate the graph run should end.

`End` is generic in the graph return type of the graph it's used in, RunEndT.

### Nodes

Subclasses of BaseNode define nodes for execution in the graph.

Nodes, which are generally dataclasses, generally consist of:

- fields containing any parameters required/optional when calling the node
- the business logic to execute the node, in the run method
- return annotations of the run method, which are read by `pydantic-graph` to determine the outgoing edges of the node

Nodes are generic in:

- **state**, which must have the same type as the state of graphs they're included in, StateT has a default of `None`, so if you're not using state you can omit this generic parameter, see [stateful graphs](#stateful-graphs) for more information
- **deps**, which must have the same type as the deps of the graph they're included in, DepsT has a default of `None`, so if you're not using deps you can omit this generic parameter, see [dependency injection](#dependency-injection) for more information
- **graph return type** â€” this only applies if the node returns End. RunEndT has a default of Never so this generic parameter can be omitted if the node doesn't return `End`, but must be included if it does.

Here's an example of a start or intermediate node in a graph â€” it can't end the run as it doesn't return End:

intermediate_node.py

```py
from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext


@dataclass
class MyNode(BaseNode[MyState]):  # (1)!
    foo: int  # (2)!

    async def run(
        self,
        ctx: GraphRunContext[MyState],  # (3)!
    ) -> AnotherNode:  # (4)!
        ...
        return AnotherNode()

```

1. State in this example is `MyState` (not shown), hence `BaseNode` is parameterized with `MyState`. This node can't end the run, so the `RunEndT` generic parameter is omitted and defaults to `Never`.
1. `MyNode` is a dataclass and has a single field `foo`, an `int`.
1. The `run` method takes a `GraphRunContext` parameter, again parameterized with state `MyState`.
1. The return type of the `run` method is `AnotherNode` (not shown), this is used to determine the outgoing edges of the node.

We could extend `MyNode` to optionally end the run if `foo` is divisible by 5:

intermediate_or_end_node.py

```py
from dataclasses import dataclass

from pydantic_graph import BaseNode, End, GraphRunContext


@dataclass
class MyNode(BaseNode[MyState, None, int]):  # (1)!
    foo: int

    async def run(
        self,
        ctx: GraphRunContext[MyState],
    ) -> AnotherNode | End[int]:  # (2)!
        if self.foo % 5 == 0:
            return End(self.foo)
        else:
            return AnotherNode()

```

1. We parameterize the node with the return type (`int` in this case) as well as state. Because generic parameters are positional-only, we have to include `None` as the second parameter representing deps.
1. The return type of the `run` method is now a union of `AnotherNode` and `End[int]`, this allows the node to end the run if `foo` is divisible by 5.

### Graph

Graph â€” this is the execution graph itself, made up of a set of [node classes](#nodes) (i.e., `BaseNode` subclasses).

`Graph` is generic in:

- **state** the state type of the graph, StateT
- **deps** the deps type of the graph, DepsT
- **graph return type** the return type of the graph run, RunEndT

Here's an example of a simple graph:

graph_example.py

```py
from __future__ import annotations

from dataclasses import dataclass

from pydantic_graph import BaseNode, End, Graph, GraphRunContext


@dataclass
class DivisibleBy5(BaseNode[None, None, int]):  # (1)!
    foo: int

    async def run(
        self,
        ctx: GraphRunContext,
    ) -> Increment | End[int]:
        if self.foo % 5 == 0:
            return End(self.foo)
        else:
            return Increment(self.foo)


@dataclass
class Increment(BaseNode):  # (2)!
    foo: int

    async def run(self, ctx: GraphRunContext) -> DivisibleBy5:
        return DivisibleBy5(self.foo + 1)


fives_graph = Graph(nodes=[DivisibleBy5, Increment])  # (3)!
result = fives_graph.run_sync(DivisibleBy5(4))  # (4)!
print(result.output)
#> 5

```

1. The `DivisibleBy5` node is parameterized with `None` for the state param and `None` for the deps param as this graph doesn't use state or deps, and `int` as it can end the run.
1. The `Increment` node doesn't return `End`, so the `RunEndT` generic parameter is omitted, state can also be omitted as the graph doesn't use state.
1. The graph is created with a sequence of nodes.
1. The graph is run synchronously with run_sync. The initial node is `DivisibleBy5(4)`. Because the graph doesn't use external state or deps, we don't pass `state` or `deps`.

*(This example is complete, it can be run "as is" with Python 3.10+)*

A [mermaid diagram](#mermaid-diagrams) for this graph can be generated with the following code:

graph_example_diagram.py

```py
from graph_example import DivisibleBy5, fives_graph

fives_graph.mermaid_code(start_node=DivisibleBy5)

```

```
---
title: fives_graph
---
stateDiagram-v2
  [*] --> DivisibleBy5
  DivisibleBy5 --> Increment
  DivisibleBy5 --> [*]
  Increment --> DivisibleBy5
```

In order to visualize a graph within a `jupyter-notebook`, `IPython.display` needs to be used:

jupyter_display_mermaid.py

```python
from graph_example import DivisibleBy5, fives_graph
from IPython.display import Image, display

display(Image(fives_graph.mermaid_image(start_node=DivisibleBy5)))

```

## Stateful Graphs

The "state" concept in `pydantic-graph` provides an optional way to access and mutate an object (often a `dataclass` or Pydantic model) as nodes run in a graph. If you think of Graphs as a production line, then your state is the engine being passed along the line and built up by each node as the graph is run.

`pydantic-graph` provides state persistence, with the state recorded after each node is run. (See [State Persistence](#state-persistence).)

Here's an example of a graph which represents a vending machine where the user may insert coins and select a product to purchase.

vending_machine.py

```python
from __future__ import annotations

from dataclasses import dataclass

from rich.prompt import Prompt

from pydantic_graph import BaseNode, End, Graph, GraphRunContext


@dataclass
class MachineState:  # (1)!
    user_balance: float = 0.0
    product: str | None = None


@dataclass
class InsertCoin(BaseNode[MachineState]):  # (3)!
    async def run(self, ctx: GraphRunContext[MachineState]) -> CoinsInserted:  # (16)!
        return CoinsInserted(float(Prompt.ask('Insert coins')))  # (4)!


@dataclass
class CoinsInserted(BaseNode[MachineState]):
    amount: float  # (5)!

    async def run(
        self, ctx: GraphRunContext[MachineState]
    ) -> SelectProduct | Purchase:  # (17)!
        ctx.state.user_balance += self.amount  # (6)!
        if ctx.state.product is not None:  # (7)!
            return Purchase(ctx.state.product)
        else:
            return SelectProduct()


@dataclass
class SelectProduct(BaseNode[MachineState]):
    async def run(self, ctx: GraphRunContext[MachineState]) -> Purchase:
        return Purchase(Prompt.ask('Select product'))


PRODUCT_PRICES = {  # (2)!
    'water': 1.25,
    'soda': 1.50,
    'crisps': 1.75,
    'chocolate': 2.00,
}


@dataclass
class Purchase(BaseNode[MachineState, None, None]):  # (18)!
    product: str

    async def run(
        self, ctx: GraphRunContext[MachineState]
    ) -> End | InsertCoin | SelectProduct:
        if price := PRODUCT_PRICES.get(self.product):  # (8)!
            ctx.state.product = self.product  # (9)!
            if ctx.state.user_balance >= price:  # (10)!
                ctx.state.user_balance -= price
                return End(None)
            else:
                diff = price - ctx.state.user_balance
                print(f'Not enough money for {self.product}, need {diff:0.2f} more')
                #> Not enough money for crisps, need 0.75 more
                return InsertCoin()  # (11)!
        else:
            print(f'No such product: {self.product}, try again')
            return SelectProduct()  # (12)!


vending_machine_graph = Graph(  # (13)!
    nodes=[InsertCoin, CoinsInserted, SelectProduct, Purchase]
)


async def main():
    state = MachineState()  # (14)!
    await vending_machine_graph.run(InsertCoin(), state=state)  # (15)!
    print(f'purchase successful item={state.product} change={state.user_balance:0.2f}')
    #> purchase successful item=crisps change=0.25

```

1. The state of the vending machine is defined as a dataclass with the user's balance and the product they've selected, if any.
1. A dictionary of products mapped to prices.
1. The `InsertCoin` node, BaseNode is parameterized with `MachineState` as that's the state used in this graph.
1. The `InsertCoin` node prompts the user to insert coins. We keep things simple by just entering a monetary amount as a float. Before you start thinking this is a toy too since it's using rich's Prompt.ask within nodes, see [below](#example-human-in-the-loop) for how control flow can be managed when nodes require external input.
1. The `CoinsInserted` node; again this is a dataclass with one field `amount`.
1. Update the user's balance with the amount inserted.
1. If the user has already selected a product, go to `Purchase`, otherwise go to `SelectProduct`.
1. In the `Purchase` node, look up the price of the product if the user entered a valid product.
1. If the user did enter a valid product, set the product in the state so we don't revisit `SelectProduct`.
1. If the balance is enough to purchase the product, adjust the balance to reflect the purchase and return End to end the graph. We're not using the run return type, so we call `End` with `None`.
1. If the balance is insufficient, go to `InsertCoin` to prompt the user to insert more coins.
1. If the product is invalid, go to `SelectProduct` to prompt the user to select a product again.
1. The graph is created by passing a list of nodes to Graph. Order of nodes is not important, but it can affect how [diagrams](#mermaid-diagrams) are displayed.
1. Initialize the state. This will be passed to the graph run and mutated as the graph runs.
1. Run the graph with the initial state. Since the graph can be run from any node, we must pass the start node â€” in this case, `InsertCoin`. Graph.run returns a GraphRunResult that provides the final data and a history of the run.
1. The return type of the node's run method is important as it is used to determine the outgoing edges of the node. This information in turn is used to render [mermaid diagrams](#mermaid-diagrams) and is enforced at runtime to detect misbehavior as soon as possible.
1. The return type of `CoinsInserted`'s run method is a union, meaning multiple outgoing edges are possible.
1. Unlike other nodes, `Purchase` can end the run, so the RunEndT generic parameter must be set. In this case it's `None` since the graph run return type is `None`.

*(This example is complete, it can be run "as is" with Python 3.10+ â€” you'll need to add `asyncio.run(main())` to run `main`)*

A [mermaid diagram](#mermaid-diagrams) for this graph can be generated with the following code:

vending_machine_diagram.py

```py
from vending_machine import InsertCoin, vending_machine_graph

vending_machine_graph.mermaid_code(start_node=InsertCoin)

```

The diagram generated by the above code is:

```
---
title: vending_machine_graph
---
stateDiagram-v2
  [*] --> InsertCoin
  InsertCoin --> CoinsInserted
  CoinsInserted --> SelectProduct
  CoinsInserted --> Purchase
  SelectProduct --> Purchase
  Purchase --> InsertCoin
  Purchase --> SelectProduct
  Purchase --> [*]
```

See [below](#mermaid-diagrams) for more information on generating diagrams.

## GenAI Example

So far we haven't shown an example of a Graph that actually uses PydanticAI or GenAI at all.

In this example, one agent generates a welcome email to a user and the other agent provides feedback on the email.

This graph has a very simple structure:

```
---
title: feedback_graph
---
stateDiagram-v2
  [*] --> WriteEmail
  WriteEmail --> Feedback
  Feedback --> WriteEmail
  Feedback --> [*]
```

genai_email_feedback.py

```python
from __future__ import annotations as _annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, EmailStr

from pydantic_ai import Agent, format_as_xml
from pydantic_ai.messages import ModelMessage
from pydantic_graph import BaseNode, End, Graph, GraphRunContext


@dataclass
class User:
    name: str
    email: EmailStr
    interests: list[str]


@dataclass
class Email:
    subject: str
    body: str


@dataclass
class State:
    user: User
    write_agent_messages: list[ModelMessage] = field(default_factory=list)


email_writer_agent = Agent(
    'google-vertex:gemini-1.5-pro',
    output_type=Email,
    system_prompt='Write a welcome email to our tech blog.',
)


@dataclass
class WriteEmail(BaseNode[State]):
    email_feedback: str | None = None

    async def run(self, ctx: GraphRunContext[State]) -> Feedback:
        if self.email_feedback:
            prompt = (
                f'Rewrite the email for the user:\n'
                f'{format_as_xml(ctx.state.user)}\n'
                f'Feedback: {self.email_feedback}'
            )
        else:
            prompt = (
                f'Write a welcome email for the user:\n'
                f'{format_as_xml(ctx.state.user)}'
            )

        result = await email_writer_agent.run(
            prompt,
            message_history=ctx.state.write_agent_messages,
        )
        ctx.state.write_agent_messages += result.new_messages()
        return Feedback(result.output)


class EmailRequiresWrite(BaseModel):
    feedback: str


class EmailOk(BaseModel):
    pass


feedback_agent = Agent[None, EmailRequiresWrite | EmailOk](
    'openai:gpt-4o',
    output_type=EmailRequiresWrite | EmailOk,  # type: ignore
    system_prompt=(
        'Review the email and provide feedback, email must reference the users specific interests.'
    ),
)


@dataclass
class Feedback(BaseNode[State, None, Email]):
    email: Email

    async def run(
        self,
        ctx: GraphRunContext[State],
    ) -> WriteEmail | End[Email]:
        prompt = format_as_xml({'user': ctx.state.user, 'email': self.email})
        result = await feedback_agent.run(prompt)
        if isinstance(result.output, EmailRequiresWrite):
            return WriteEmail(email_feedback=result.output.feedback)
        else:
            return End(self.email)


async def main():
    user = User(
        name='John Doe',
        email='john.joe@example.com',
        interests=['Haskel', 'Lisp', 'Fortran'],
    )
    state = State(user)
    feedback_graph = Graph(nodes=(WriteEmail, Feedback))
    result = await feedback_graph.run(WriteEmail(), state=state)
    print(result.output)
    """
    Email(
        subject='Welcome to our tech blog!',
        body='Hello John, Welcome to our tech blog! ...',
    )
    """

```

*(This example is complete, it can be run "as is" with Python 3.10+ â€” you'll need to add `asyncio.run(main())` to run `main`)*

## Iterating Over a Graph

### Using `Graph.iter` for `async for` iteration

Sometimes you want direct control or insight into each node as the graph executes. The easiest way to do that is with the Graph.iter method, which returns a **context manager** that yields a GraphRun object. The `GraphRun` is an async-iterable over the nodes of your graph, allowing you to record or modify them as they execute.

Here's an example:

count_down.py

```python
from __future__ import annotations as _annotations

from dataclasses import dataclass
from pydantic_graph import Graph, BaseNode, End, GraphRunContext


@dataclass
class CountDownState:
    counter: int


@dataclass
class CountDown(BaseNode[CountDownState, None, int]):
    async def run(self, ctx: GraphRunContext[CountDownState]) -> CountDown | End[int]:
        if ctx.state.counter <= 0:
            return End(ctx.state.counter)
        ctx.state.counter -= 1
        return CountDown()


count_down_graph = Graph(nodes=[CountDown])


async def main():
    state = CountDownState(counter=3)
    async with count_down_graph.iter(CountDown(), state=state) as run:  # (1)!
        async for node in run:  # (2)!
            print('Node:', node)
            #> Node: CountDown()
            #> Node: CountDown()
            #> Node: CountDown()
            #> Node: CountDown()
            #> Node: End(data=0)
    print('Final output:', run.result.output)  # (3)!
    #> Final output: 0

```

1. `Graph.iter(...)` returns a GraphRun.
1. Here, we step through each node as it is executed.
1. Once the graph returns an End, the loop ends, and `run.result` becomes a GraphRunResult containing the final outcome (`0` here).

### Using `GraphRun.next(node)` manually

Alternatively, you can drive iteration manually with the GraphRun.next method, which allows you to pass in whichever node you want to run next. You can modify or selectively skip nodes this way.

Below is a contrived example that stops whenever the counter is at 2, ignoring any node runs beyond that:

count_down_next.py

```python
from pydantic_graph import End, FullStatePersistence
from count_down import CountDown, CountDownState, count_down_graph


async def main():
    state = CountDownState(counter=5)
    persistence = FullStatePersistence()  # (7)!
    async with count_down_graph.iter(
        CountDown(), state=state, persistence=persistence
    ) as run:
        node = run.next_node  # (1)!
        while not isinstance(node, End):  # (2)!
            print('Node:', node)
            #> Node: CountDown()
            #> Node: CountDown()
            #> Node: CountDown()
            #> Node: CountDown()
            if state.counter == 2:
                break  # (3)!
            node = await run.next(node)  # (4)!

        print(run.result)  # (5)!
        #> None

        for step in persistence.history:  # (6)!
            print('History Step:', step.state, step.state)
            #> History Step: CountDownState(counter=5) CountDownState(counter=5)
            #> History Step: CountDownState(counter=4) CountDownState(counter=4)
            #> History Step: CountDownState(counter=3) CountDownState(counter=3)
            #> History Step: CountDownState(counter=2) CountDownState(counter=2)

```

1. We start by grabbing the first node that will be run in the agent's graph.
1. The agent run is finished once an `End` node has been produced; instances of `End` cannot be passed to `next`.
1. If the user decides to stop early, we break out of the loop. The graph run won't have a real final result in that case (`run.result` remains `None`).
1. At each step, we call `await run.next(node)` to run it and get the next node (or an `End`).
1. Because we did not continue the run until it finished, the `result` is not set.
1. The run's history is still populated with the steps we executed so far.
1. Use FullStatePersistence so we can show the history of the run, see [State Persistence](#state-persistence) below for more information.

## State Persistence

One of the biggest benefits of finite state machine (FSM) graphs is how they simplify the handling of interrupted execution. This might happen for a variety of reasons:

- the state machine logic might fundamentally need to be paused â€” e.g. the returns workflow for an e-commerce order needs to wait for the item to be posted to the returns center or because execution of the next node needs input from a user so needs to wait for a new http request,
- the execution takes so long that the entire graph can't reliably be executed in a single continuous run â€” e.g. a deep research agent that might take hours to run,
- you want to run multiple graph nodes in parallel in different processes / hardware instances (note: parallel node execution is not yet supported in `pydantic-graph`, see [#704](https://github.com/pydantic/pydantic-ai/issues/704)).

Trying to make a conventional control flow (i.e., boolean logic and nested function calls) implementation compatible with these usage scenarios generally results in brittle and over-complicated spaghetti code, with the logic required to interrupt and resume execution dominating the implementation.

To allow graph runs to be interrupted and resumed, `pydantic-graph` provides state persistence â€” a system for snapshotting the state of a graph run before and after each node is run, allowing a graph run to be resumed from any point in the graph.

`pydantic-graph` includes three state persistence implementations:

- SimpleStatePersistence â€” Simple in memory state persistence that just hold the latest snapshot. If no state persistence implementation is provided when running a graph, this is used by default.
- FullStatePersistence â€” In memory state persistence that hold a list of snapshots.
- FileStatePersistence â€” File-based state persistence that saves snapshots to a JSON file.

In production applications, developers should implement their own state persistence by subclassing BaseStatePersistence abstract base class, which might persist runs in a relational database like PostgresQL.

At a high level the role of `StatePersistence` implementations is to store and retrieve NodeSnapshot and EndSnapshot objects.

graph.iter_from_persistence() may be used to run the graph based on the state stored in persistence.

We can run the `count_down_graph` from [above](#iterating-over-a-graph), using graph.iter_from_persistence() and FileStatePersistence.

As you can see in this code, `run_node` requires no external application state (apart from state persistence) to be run, meaning graphs can easily be executed by distributed execution and queueing systems.

count_down_from_persistence.py

```python
from pathlib import Path

from pydantic_graph import End
from pydantic_graph.persistence.file import FileStatePersistence

from count_down import CountDown, CountDownState, count_down_graph


async def main():
    run_id = 'run_abc123'
    persistence = FileStatePersistence(Path(f'count_down_{run_id}.json'))  # (1)!
    state = CountDownState(counter=5)
    await count_down_graph.initialize(  # (2)!
        CountDown(), state=state, persistence=persistence
    )

    done = False
    while not done:
        done = await run_node(run_id)


async def run_node(run_id: str) -> bool:  # (3)!
    persistence = FileStatePersistence(Path(f'count_down_{run_id}.json'))
    async with count_down_graph.iter_from_persistence(persistence) as run:  # (4)!
        node_or_end = await run.next()  # (5)!

    print('Node:', node_or_end)
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: CountDown()
    #> Node: End(data=0)
    return isinstance(node_or_end, End)  # (6)!

```

1. Create a FileStatePersistence to use to start the graph.
1. Call graph.initialize() to set the initial graph state in the persistence object.
1. `run_node` is a pure function that doesn't need access to any other process state to run the next node of the graph, except the ID of the run.
1. Call graph.iter_from_persistence() create a GraphRun object that will run the next node of the graph from the state stored in persistence. This will return either a node or an `End` object.
1. graph.run() will return either a node or an End object.
1. Check if the node is an End object, if it is, the graph run is complete.

*(This example is complete, it can be run "as is" with Python 3.10+ â€” you'll need to add `asyncio.run(main())` to run `main`)*

### Example: Human in the loop.

As noted above, state persistence allows graphs to be interrupted and resumed. One use case of this is to allow user input to continue.

In this example, an AI asks the user a question, the user provides an answer, the AI evaluates the answer and ends if the user got it right or asks another question if they got it wrong.

Instead of running the entire graph in a single process invocation, we run the graph by running the process repeatedly, optionally providing an answer to the question as a command line argument.

`ai_q_and_a_graph.py` â€” `question_graph` definition ai_q_and_a_graph.py

```python
from __future__ import annotations as _annotations

from dataclasses import dataclass, field

from groq import BaseModel
from pydantic_graph import (
    BaseNode,
    End,
    Graph,
    GraphRunContext,
)

from pydantic_ai import Agent, format_as_xml
from pydantic_ai.messages import ModelMessage

ask_agent = Agent('openai:gpt-4o', output_type=str, instrument=True)


@dataclass
class QuestionState:
    question: str | None = None
    ask_agent_messages: list[ModelMessage] = field(default_factory=list)
    evaluate_agent_messages: list[ModelMessage] = field(default_factory=list)


@dataclass
class Ask(BaseNode[QuestionState]):
    async def run(self, ctx: GraphRunContext[QuestionState]) -> Answer:
        result = await ask_agent.run(
            'Ask a simple question with a single correct answer.',
            message_history=ctx.state.ask_agent_messages,
        )
        ctx.state.ask_agent_messages += result.new_messages()
        ctx.state.question = result.output
        return Answer(result.output)


@dataclass
class Answer(BaseNode[QuestionState]):
    question: str

    async def run(self, ctx: GraphRunContext[QuestionState]) -> Evaluate:
        answer = input(f'{self.question}: ')
        return Evaluate(answer)


class EvaluationResult(BaseModel, use_attribute_docstrings=True):
    correct: bool
    """Whether the answer is correct."""
    comment: str
    """Comment on the answer, reprimand the user if the answer is wrong."""


evaluate_agent = Agent(
    'openai:gpt-4o',
    output_type=EvaluationResult,
    system_prompt='Given a question and answer, evaluate if the answer is correct.',
)


@dataclass
class Evaluate(BaseNode[QuestionState, None, str]):
    answer: str

    async def run(
        self,
        ctx: GraphRunContext[QuestionState],
    ) -> End[str] | Reprimand:
        assert ctx.state.question is not None
        result = await evaluate_agent.run(
            format_as_xml({'question': ctx.state.question, 'answer': self.answer}),
            message_history=ctx.state.evaluate_agent_messages,
        )
        ctx.state.evaluate_agent_messages += result.new_messages()
        if result.output.correct:
            return End(result.output.comment)
        else:
            return Reprimand(result.output.comment)


@dataclass
class Reprimand(BaseNode[QuestionState]):
    comment: str

    async def run(self, ctx: GraphRunContext[QuestionState]) -> Ask:
        print(f'Comment: {self.comment}')
        ctx.state.question = None
        return Ask()


question_graph = Graph(
    nodes=(Ask, Answer, Evaluate, Reprimand), state_type=QuestionState
)

```

*(This example is complete, it can be run "as is" with Python 3.10+)*

ai_q_and_a_run.py

```python
import sys
from pathlib import Path

from pydantic_graph import End
from pydantic_graph.persistence.file import FileStatePersistence
from pydantic_ai.messages import ModelMessage  # noqa: F401

from ai_q_and_a_graph import Ask, question_graph, Evaluate, QuestionState, Answer


async def main():
    answer: str | None = sys.argv[1] if len(sys.argv) > 1 else None  # (1)!
    persistence = FileStatePersistence(Path('question_graph.json'))  # (2)!
    persistence.set_graph_types(question_graph)  # (3)!

    if snapshot := await persistence.load_next():  # (4)!
        state = snapshot.state
        assert answer is not None
        node = Evaluate(answer)
    else:
        state = QuestionState()
        node = Ask()  # (5)!

    async with question_graph.iter(node, state=state, persistence=persistence) as run:
        while True:
            node = await run.next()  # (6)!
            if isinstance(node, End):  # (7)!
                print('END:', node.data)
                history = await persistence.load_all()  # (8)!
                print([e.node for e in history])
                break
            elif isinstance(node, Answer):  # (9)!
                print(node.question)
                #> What is the capital of France?
                break
            # otherwise just continue

```

1. Get the user's answer from the command line, if provided. See [question graph example](../examples/question-graph/) for a complete example.
1. Create a state persistence instance the `'question_graph.json'` file may or may not already exist.
1. Since we're using the persistence interface outside a graph, we need to call set_graph_types to set the graph generic types `StateT` and `RunEndT` for the persistence instance. This is necessary to allow the persistence instance to know how to serialize and deserialize graph nodes.
1. If we're run the graph before, load_next will return a snapshot of the next node to run, here we use `state` from that snapshot, and create a new `Evaluate` node with the answer provided on the command line.
1. If the graph hasn't been run before, we create a new `QuestionState` and start with the `Ask` node.
1. Call GraphRun.next() to run the node. This will return either a node or an `End` object.
1. If the node is an `End` object, the graph run is complete. The `data` field of the `End` object contains the comment returned by the `evaluate_agent` about the correct answer.
1. To demonstrate the state persistence, we call load_all to get all the snapshots from the persistence instance. This will return a list of Snapshot objects.
1. If the node is an `Answer` object, we print the question and break out of the loop to end the process and wait for user input.

*(This example is complete, it can be run "as is" with Python 3.10+ â€” you'll need to add `asyncio.run(main())` to run `main`)*

For a complete example of this graph, see the [question graph example](../examples/question-graph/).

## Dependency Injection

As with PydanticAI, `pydantic-graph` supports dependency injection via a generic parameter on Graph and BaseNode, and the GraphRunContext.deps field.

As an example of dependency injection, let's modify the `DivisibleBy5` example [above](#graph) to use a ProcessPoolExecutor to run the compute load in a separate process (this is a contrived example, `ProcessPoolExecutor` wouldn't actually improve performance in this example):

deps_example.py

```py
from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from pydantic_graph import BaseNode, End, FullStatePersistence, Graph, GraphRunContext


@dataclass
class GraphDeps:
    executor: ProcessPoolExecutor


@dataclass
class DivisibleBy5(BaseNode[None, GraphDeps, int]):
    foo: int

    async def run(
        self,
        ctx: GraphRunContext[None, GraphDeps],
    ) -> Increment | End[int]:
        if self.foo % 5 == 0:
            return End(self.foo)
        else:
            return Increment(self.foo)


@dataclass
class Increment(BaseNode[None, GraphDeps]):
    foo: int

    async def run(self, ctx: GraphRunContext[None, GraphDeps]) -> DivisibleBy5:
        loop = asyncio.get_running_loop()
        compute_result = await loop.run_in_executor(
            ctx.deps.executor,
            self.compute,
        )
        return DivisibleBy5(compute_result)

    def compute(self) -> int:
        return self.foo + 1


fives_graph = Graph(nodes=[DivisibleBy5, Increment])


async def main():
    with ProcessPoolExecutor() as executor:
        deps = GraphDeps(executor)
        result = await fives_graph.run(DivisibleBy5(3), deps=deps, persistence=FullStatePersistence())
    print(result.output)
    #> 5
    # the full history is quite verbose (see below), so we'll just print the summary
    print([item.node for item in result.persistence.history])
    """
    [
        DivisibleBy5(foo=3),
        Increment(foo=3),
        DivisibleBy5(foo=4),
        Increment(foo=4),
        DivisibleBy5(foo=5),
        End(data=5),
    ]
    """

```

*(This example is complete, it can be run "as is" with Python 3.10+ â€” you'll need to add `asyncio.run(main())` to run `main`)*

## Mermaid Diagrams

Pydantic Graph can generate [mermaid](https://mermaid.js.org/) [`stateDiagram-v2`](https://mermaid.js.org/syntax/stateDiagram.html) diagrams for graphs, as shown above.

These diagrams can be generated with:

- Graph.mermaid_code to generate the mermaid code for a graph
- Graph.mermaid_image to generate an image of the graph using [mermaid.ink](https://mermaid.ink/)
- Graph.mermaid_save to generate an image of the graph using [mermaid.ink](https://mermaid.ink/) and save it to a file

Beyond the diagrams shown above, you can also customize mermaid diagrams with the following options:

- Edge allows you to apply a label to an edge
- BaseNode.docstring_notes and BaseNode.get_note allows you to add notes to nodes
- The highlighted_nodes parameter allows you to highlight specific node(s) in the diagram

Putting that together, we can edit the last [`ai_q_and_a_graph.py`](#example-human-in-the-loop) example to:

- add labels to some edges
- add a note to the `Ask` node
- highlight the `Answer` node
- save the diagram as a `PNG` image to file

ai_q_and_a_graph_extra.py

```python
...
from typing import Annotated

from pydantic_graph import BaseNode, End, Graph, GraphRunContext, Edge

...

@dataclass
class Ask(BaseNode[QuestionState]):
    """Generate question using GPT-4o."""
    docstring_notes = True
    async def run(
        self, ctx: GraphRunContext[QuestionState]
    ) -> Annotated[Answer, Edge(label='Ask the question')]:
        ...

...

@dataclass
class Evaluate(BaseNode[QuestionState]):
    answer: str

    async def run(
            self,
            ctx: GraphRunContext[QuestionState],
    ) -> Annotated[End[str], Edge(label='success')] | Reprimand:
        ...

...

question_graph.mermaid_save('image.png', highlighted_nodes=[Answer])

```

*(This example is not complete and cannot be run directly)*

This would generate an image that looks like this:

```
---
title: question_graph
---
stateDiagram-v2
  Ask --> Answer: Ask the question
  note right of Ask
    Judge the answer.
    Decide on next step.
  end note
  Answer --> Evaluate
  Evaluate --> Reprimand
  Evaluate --> [*]: success
  Reprimand --> Ask

classDef highlighted fill:#fdff32
class Answer highlighted
```

### Setting Direction of the State Diagram

You can specify the direction of the state diagram using one of the following values:

- `'TB'`: Top to bottom, the diagram flows vertically from top to bottom.
- `'LR'`: Left to right, the diagram flows horizontally from left to right.
- `'RL'`: Right to left, the diagram flows horizontally from right to left.
- `'BT'`: Bottom to top, the diagram flows vertically from bottom to top.

Here is an example of how to do this using 'Left to Right' (LR) instead of the default 'Top to Bottom' (TB): vending_machine_diagram.py

```py
from vending_machine import InsertCoin, vending_machine_graph

vending_machine_graph.mermaid_code(start_node=InsertCoin, direction='LR')

```

```
---
title: vending_machine_graph
---
stateDiagram-v2
  direction LR
  [*] --> InsertCoin
  InsertCoin --> CoinsInserted
  CoinsInserted --> SelectProduct
  CoinsInserted --> Purchase
  SelectProduct --> Purchase
  Purchase --> InsertCoin
  Purchase --> SelectProduct
  Purchase --> [*]
```
# Evals

# Evals

"Evals" refers to evaluating a model's performance for a specific application.

Warning

Unlike unit tests, evals are an emerging art/science; anyone who claims to know for sure exactly how your evals should be defined can safely be ignored.

Pydantic Evals is a powerful evaluation framework designed to help you systematically test and evaluate the performance and accuracy of the systems you build, especially when working with LLMs.

We've designed Pydantic Evals to be useful while not being too opinionated since we (along with everyone else) are still figuring out best practices. We'd love your [feedback](../help/) on the package and how we can improve it.

In Beta

Pydantic Evals support was [introduced](https://github.com/pydantic/pydantic-ai/pull/935) in v0.0.47 and is currently in beta. The API is subject to change and the documentation is incomplete.

## Installation

To install the Pydantic Evals package, run:

```bash
pip install pydantic-evals

```

```bash
uv add pydantic-evals

```

`pydantic-evals` does not depend on `pydantic-ai`, but has an optional dependency on `logfire` if you'd like to use OpenTelemetry traces in your evals, or send evaluation results to [logfire](https://pydantic.dev/logfire).

```bash
pip install 'pydantic-evals[logfire]'

```

```bash
uv add 'pydantic-evals[logfire]'

```

## Datasets and Cases

In Pydantic Evals, everything begins with `Dataset`s and `Case`s:

- Case: A single test scenario corresponding to "task" inputs. Can also optionally have a name, expected outputs, metadata, and evaluators.
- Dataset: A collection of test cases designed for the evaluation of a specific task or function.

simple_eval_dataset.py

```python
from pydantic_evals import Case, Dataset

case1 = Case(
    name='simple_case',
    inputs='What is the capital of France?',
    expected_output='Paris',
    metadata={'difficulty': 'easy'},
)

dataset = Dataset(cases=[case1])

```

*(This example is complete, it can be run "as is")*

## Evaluators

Evaluators are the components that analyze and score the results of your task when tested against a case.

Pydantic Evals includes several built-in evaluators and allows you to create custom evaluators:

simple_eval_evaluator.py

```python
from dataclasses import dataclass

from simple_eval_dataset import dataset

from pydantic_evals.evaluators import Evaluator, EvaluatorContext
from pydantic_evals.evaluators.common import IsInstance

dataset.add_evaluator(IsInstance(type_name='str'))  # (1)!


@dataclass
class MyEvaluator(Evaluator):
    async def evaluate(self, ctx: EvaluatorContext[str, str]) -> float:  # (2)!
        if ctx.output == ctx.expected_output:
            return 1.0
        elif (
            isinstance(ctx.output, str)
            and ctx.expected_output.lower() in ctx.output.lower()
        ):
            return 0.8
        else:
            return 0.0


dataset.add_evaluator(MyEvaluator())

```

1. You can add built-in evaluators to a dataset using the add_evaluator method.
1. This custom evaluator returns a simple score based on whether the output matches the expected output.

*(This example is complete, it can be run "as is")*

## Evaluation Process

The evaluation process involves running a task against all cases in a dataset:

Putting the above two examples together and using the more declarative `evaluators` kwarg to Dataset:

simple_eval_complete.py

```python
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator, EvaluatorContext, IsInstance

case1 = Case(  # (1)!
    name='simple_case',
    inputs='What is the capital of France?',
    expected_output='Paris',
    metadata={'difficulty': 'easy'},
)


class MyEvaluator(Evaluator[str, str]):
    def evaluate(self, ctx: EvaluatorContext[str, str]) -> float:
        if ctx.output == ctx.expected_output:
            return 1.0
        elif (
            isinstance(ctx.output, str)
            and ctx.expected_output.lower() in ctx.output.lower()
        ):
            return 0.8
        else:
            return 0.0


dataset = Dataset(
    cases=[case1],
    evaluators=[IsInstance(type_name='str'), MyEvaluator()],  # (3)!
)


async def guess_city(question: str) -> str:  # (4)!
    return 'Paris'


report = dataset.evaluate_sync(guess_city)  # (5)!
report.print(include_input=True, include_output=True, include_durations=False)  # (6)!
"""
                              Evaluation Summary: guess_city
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”“
â”ƒ Case ID     â”ƒ Inputs                         â”ƒ Outputs â”ƒ Scores            â”ƒ Assertions â”ƒ
â”¡â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”©
â”‚ simple_case â”‚ What is the capital of France? â”‚ Paris   â”‚ MyEvaluator: 1.00 â”‚ âœ”          â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Averages    â”‚                                â”‚         â”‚ MyEvaluator: 1.00 â”‚ 100.0% âœ”   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
"""

```

1. Create a test case as above
1. Also create a custom evaluator function as above
1. Create a Dataset with test cases, also set the evaluators when creating the dataset
1. Our function to evaluate.
1. Run the evaluation with evaluate_sync, which runs the function against all test cases in the dataset, and returns an EvaluationReport object.
1. Print the report with print, which shows the results of the evaluation, including input and output. We have omitted duration here just to keep the printed output from changing from run to run.

*(This example is complete, it can be run "as is")*

## Evaluation with `LLMJudge`

In this example we evaluate a method for generating recipes based on customer orders.

judge_recipes.py

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pydantic_ai import Agent, format_as_xml
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import IsInstance, LLMJudge


class CustomerOrder(BaseModel):  # (1)!
    dish_name: str
    dietary_restriction: str | None = None


class Recipe(BaseModel):
    ingredients: list[str]
    steps: list[str]


recipe_agent = Agent(
    'groq:llama-3.3-70b-versatile',
    output_type=Recipe,
    system_prompt=(
        'Generate a recipe to cook the dish that meets the dietary restrictions.'
    ),
)


async def transform_recipe(customer_order: CustomerOrder) -> Recipe:  # (2)!
    r = await recipe_agent.run(format_as_xml(customer_order))
    return r.output


recipe_dataset = Dataset[CustomerOrder, Recipe, Any](  # (3)!
    cases=[
        Case(
            name='vegetarian_recipe',
            inputs=CustomerOrder(
                dish_name='Spaghetti Bolognese', dietary_restriction='vegetarian'
            ),
            expected_output=None,  # (4)
            metadata={'focus': 'vegetarian'},
            evaluators=(
                LLMJudge(  # (5)!
                    rubric='Recipe should not contain meat or animal products',
                ),
            ),
        ),
        Case(
            name='gluten_free_recipe',
            inputs=CustomerOrder(
                dish_name='Chocolate Cake', dietary_restriction='gluten-free'
            ),
            expected_output=None,
            metadata={'focus': 'gluten-free'},
            # Case-specific evaluator with a focused rubric
            evaluators=(
                LLMJudge(
                    rubric='Recipe should not contain gluten or wheat products',
                ),
            ),
        ),
    ],
    evaluators=[  # (6)!
        IsInstance(type_name='Recipe'),
        LLMJudge(
            rubric='Recipe should have clear steps and relevant ingredients',
            include_input=True,
            model='anthropic:claude-3-7-sonnet-latest',  # (7)!
        ),
    ],
)


report = recipe_dataset.evaluate_sync(transform_recipe)
print(report)
"""
     Evaluation Summary: transform_recipe
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”“
â”ƒ Case ID            â”ƒ Assertions â”ƒ Duration â”ƒ
â”¡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”©
â”‚ vegetarian_recipe  â”‚ âœ”âœ”âœ”        â”‚     10ms â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ gluten_free_recipe â”‚ âœ”âœ”âœ”        â”‚     10ms â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Averages           â”‚ 100.0% âœ”   â”‚     10ms â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
"""

```

1. Define models for our task â€” Input for recipe generation task and output of the task.
1. Define our recipe generation function - this is the task we want to evaluate.
1. Create a dataset with different test cases and different rubrics.
1. No expected output, we'll let the LLM judge the quality.
1. Case-specific evaluator with a focused rubric using LLMJudge.
1. Dataset-level evaluators that apply to all cases, including a general quality rubric for all recipes
1. By default `LLMJudge` uses `openai:gpt-4o`, here we use a specific Anthropic model.

*(This example is complete, it can be run "as is")*

## Saving and Loading Datasets

Datasets can be saved to and loaded from YAML or JSON files.

save_load_dataset_example.py

```python
from pathlib import Path

from judge_recipes import CustomerOrder, Recipe, recipe_dataset

from pydantic_evals import Dataset

recipe_transforms_file = Path('recipe_transform_tests.yaml')
recipe_dataset.to_file(recipe_transforms_file)  # (1)!
print(recipe_transforms_file.read_text())
"""
# yaml-language-server: $schema=recipe_transform_tests_schema.json
cases:
- name: vegetarian_recipe
  inputs:
    dish_name: Spaghetti Bolognese
    dietary_restriction: vegetarian
  metadata:
    focus: vegetarian
  evaluators:
  - LLMJudge: Recipe should not contain meat or animal products
- name: gluten_free_recipe
  inputs:
    dish_name: Chocolate Cake
    dietary_restriction: gluten-free
  metadata:
    focus: gluten-free
  evaluators:
  - LLMJudge: Recipe should not contain gluten or wheat products
evaluators:
- IsInstance: Recipe
- LLMJudge:
    rubric: Recipe should have clear steps and relevant ingredients
    model: anthropic:claude-3-7-sonnet-latest
    include_input: true
"""

# Load dataset from file
loaded_dataset = Dataset[CustomerOrder, Recipe, dict].from_file(recipe_transforms_file)

print(f'Loaded dataset with {len(loaded_dataset.cases)} cases')
#> Loaded dataset with 2 cases

```

*(This example is complete, it can be run "as is")*

## Parallel Evaluation

You can control concurrency during evaluation (this might be useful to prevent exceeding a rate limit):

parallel_evaluation_example.py

```python
import asyncio
import time

from pydantic_evals import Case, Dataset

# Create a dataset with multiple test cases
dataset = Dataset(
    cases=[
        Case(
            name=f'case_{i}',
            inputs=i,
            expected_output=i * 2,
        )
        for i in range(5)
    ]
)


async def double_number(input_value: int) -> int:
    """Function that simulates work by sleeping for a second before returning double the input."""
    await asyncio.sleep(0.1)  # Simulate work
    return input_value * 2


# Run evaluation with unlimited concurrency
t0 = time.time()
report_default = dataset.evaluate_sync(double_number)
print(f'Evaluation took less than 0.3s: {time.time() - t0 < 0.3}')
#> Evaluation took less than 0.3s: True

report_default.print(include_input=True, include_output=True, include_durations=False)  # (1)!
"""
      Evaluation Summary:
         double_number
â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”“
â”ƒ Case ID  â”ƒ Inputs â”ƒ Outputs â”ƒ
â”¡â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”©
â”‚ case_0   â”‚ 0      â”‚ 0       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_1   â”‚ 1      â”‚ 2       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_2   â”‚ 2      â”‚ 4       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_3   â”‚ 3      â”‚ 6       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_4   â”‚ 4      â”‚ 8       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Averages â”‚        â”‚         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
"""

# Run evaluation with limited concurrency
t0 = time.time()
report_limited = dataset.evaluate_sync(double_number, max_concurrency=1)
print(f'Evaluation took more than 0.5s: {time.time() - t0 > 0.5}')
#> Evaluation took more than 0.5s: True

report_limited.print(include_input=True, include_output=True, include_durations=False)  # (2)!
"""
      Evaluation Summary:
         double_number
â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”“
â”ƒ Case ID  â”ƒ Inputs â”ƒ Outputs â”ƒ
â”¡â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”©
â”‚ case_0   â”‚ 0      â”‚ 0       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_1   â”‚ 1      â”‚ 2       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_2   â”‚ 2      â”‚ 4       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_3   â”‚ 3      â”‚ 6       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ case_4   â”‚ 4      â”‚ 8       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Averages â”‚        â”‚         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
"""

```

1. We have omitted duration here just to keep the printed output from changing from run to run.
1. We have omitted duration here just to keep the printed output from changing from run to run.

*(This example is complete, it can be run "as is")*

## OpenTelemetry Integration

Pydantic Evals integrates with OpenTelemetry for tracing.

The EvaluatorContext includes a property called `span_tree` which returns a SpanTree. The `SpanTree` provides a way to query and analyze the spans generated during function execution. This provides a way to access the results of instrumentation during evaluation.

Note

If you just want to write unit tests that ensure that specific spans are produced during calls to your evaluation task, it's usually better to just use the `logfire.testing.capfire` fixture directly.

There are two main ways this is useful.

opentelemetry_example.py

```python
import asyncio
from typing import Any

import logfire

from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import Evaluator
from pydantic_evals.evaluators.context import EvaluatorContext
from pydantic_evals.otel.span_tree import SpanQuery

logfire.configure(  # ensure that an OpenTelemetry tracer is configured
    send_to_logfire='if-token-present'
)


class SpanTracingEvaluator(Evaluator[str, str]):
    """Evaluator that analyzes the span tree generated during function execution."""

    def evaluate(self, ctx: EvaluatorContext[str, str]) -> dict[str, Any]:
        # Get the span tree from the context
        span_tree = ctx.span_tree
        if span_tree is None:
            return {'has_spans': False, 'performance_score': 0.0}

        # Find all spans with "processing" in the name
        processing_spans = span_tree.find(lambda node: 'processing' in node.name)

        # Calculate total processing time
        total_processing_time = sum(
            (span.duration.total_seconds() for span in processing_spans), 0.0
        )

        # Check for error spans
        error_query: SpanQuery = {'name_contains': 'error'}
        has_errors = span_tree.any(error_query)

        # Calculate a performance score (lower is better)
        performance_score = 1.0 if total_processing_time < 0.5 else 0.5

        return {
            'has_spans': True,
            'has_errors': has_errors,
            'performance_score': 0 if has_errors else performance_score,
        }


async def process_text(text: str) -> str:
    """Function that processes text with OpenTelemetry instrumentation."""
    with logfire.span('process_text'):
        # Simulate initial processing
        with logfire.span('text_processing'):
            await asyncio.sleep(0.1)
            processed = text.strip().lower()

        # Simulate additional processing
        with logfire.span('additional_processing'):
            if 'error' in processed:
                with logfire.span('error_handling'):
                    logfire.error(f'Error detected in text: {text}')
                    return f'Error processing: {text}'
            await asyncio.sleep(0.2)
            processed = processed.replace(' ', '_')

        return f'Processed: {processed}'


# Create test cases
dataset = Dataset(
    cases=[
        Case(
            name='normal_text',
            inputs='Hello World',
            expected_output='Processed: hello_world',
        ),
        Case(
            name='text_with_error',
            inputs='Contains error marker',
            expected_output='Error processing: Contains error marker',
        ),
    ],
    evaluators=[SpanTracingEvaluator()],
)

# Run evaluation - spans are automatically captured since logfire is configured
report = dataset.evaluate_sync(process_text)

# Print the report
report.print(include_input=True, include_output=True, include_durations=False)  # (1)!
"""
                                              Evaluation Summary: process_text
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”³â”â”â”â”â”â”â”â”â”â”â”â”â”“
â”ƒ Case ID         â”ƒ Inputs                â”ƒ Outputs                                 â”ƒ Scores                   â”ƒ Assertions â”ƒ
â”¡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â•‡â”â”â”â”â”â”â”â”â”â”â”â”â”©
â”‚ normal_text     â”‚ Hello World           â”‚ Processed: hello_world                  â”‚ performance_score: 1.00  â”‚ âœ”âœ—         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ text_with_error â”‚ Contains error marker â”‚ Error processing: Contains error marker â”‚ performance_score: 0     â”‚ âœ”âœ”         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ Averages        â”‚                       â”‚                                         â”‚ performance_score: 0.500 â”‚ 75.0% âœ”    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
"""

```

1. We have omitted duration here just to keep the printed output from changing from run to run.

*(This example is complete, it can be run "as is")*

## Generating Test Datasets

Pydantic Evals allows you to generate test datasets using LLMs with generate_dataset.

Datasets can be generated in either JSON or YAML format, in both cases a JSON schema file is generated alongside the dataset and referenced in the dataset, so you should get type checking and auto-completion in your editor.

generate_dataset_example.py

```python
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from pydantic_evals import Dataset
from pydantic_evals.generation import generate_dataset


class QuestionInputs(BaseModel, use_attribute_docstrings=True):  # (1)!
    """Model for question inputs."""

    question: str
    """A question to answer"""
    context: str | None = None
    """Optional context for the question"""


class AnswerOutput(BaseModel, use_attribute_docstrings=True):  # (2)!
    """Model for expected answer outputs."""

    answer: str
    """The answer to the question"""
    confidence: float = Field(ge=0, le=1)
    """Confidence level (0-1)"""


class MetadataType(BaseModel, use_attribute_docstrings=True):  # (3)!
    """Metadata model for test cases."""

    difficulty: str
    """Difficulty level (easy, medium, hard)"""
    category: str
    """Question category"""


async def main():
    dataset = await generate_dataset(  # (4)!
        dataset_type=Dataset[QuestionInputs, AnswerOutput, MetadataType],
        n_examples=2,
        extra_instructions="""
        Generate question-answer pairs about world capitals and landmarks.
        Make sure to include both easy and challenging questions.
        """,
    )
    output_file = Path('questions_cases.yaml')
    dataset.to_file(output_file)  # (5)!
    print(output_file.read_text())
    """
    # yaml-language-server: $schema=questions_cases_schema.json
    cases:
    - name: Easy Capital Question
      inputs:
        question: What is the capital of France?
      metadata:
        difficulty: easy
        category: Geography
      expected_output:
        answer: Paris
        confidence: 0.95
      evaluators:
      - EqualsExpected
    - name: Challenging Landmark Question
      inputs:
        question: Which world-famous landmark is located on the banks of the Seine River?
      metadata:
        difficulty: hard
        category: Landmarks
      expected_output:
        answer: Eiffel Tower
        confidence: 0.9
      evaluators:
      - EqualsExpected
    """

```

1. Define the schema for the inputs to the task.
1. Define the schema for the expected outputs of the task.
1. Define the schema for the metadata of the test cases.
1. Call generate_dataset to create a Dataset with 2 cases confirming to the schema.
1. Save the dataset to a YAML file, this will also write `questions_cases_schema.json` with the schema JSON schema for `questions_cases.yaml` to make editing easier. The magic `yaml-language-server` comment is supported by at least vscode, jetbrains/pycharm (more details [here](https://github.com/redhat-developer/yaml-language-server#using-inlined-schema)).

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main(answer))` to run `main`)*

You can also write datasets as JSON files:

generate_dataset_example_json.py

```python
from pathlib import Path

from generate_dataset_example import AnswerOutput, MetadataType, QuestionInputs

from pydantic_evals import Dataset
from pydantic_evals.generation import generate_dataset


async def main():
    dataset = await generate_dataset(  # (1)!
        dataset_type=Dataset[QuestionInputs, AnswerOutput, MetadataType],
        n_examples=2,
        extra_instructions="""
        Generate question-answer pairs about world capitals and landmarks.
        Make sure to include both easy and challenging questions.
        """,
    )
    output_file = Path('questions_cases.json')
    dataset.to_file(output_file)  # (2)!
    print(output_file.read_text())
    """
    {
      "$schema": "questions_cases_schema.json",
      "cases": [
        {
          "name": "Easy Capital Question",
          "inputs": {
            "question": "What is the capital of France?"
          },
          "metadata": {
            "difficulty": "easy",
            "category": "Geography"
          },
          "expected_output": {
            "answer": "Paris",
            "confidence": 0.95
          },
          "evaluators": [
            "EqualsExpected"
          ]
        },
        {
          "name": "Challenging Landmark Question",
          "inputs": {
            "question": "Which world-famous landmark is located on the banks of the Seine River?"
          },
          "metadata": {
            "difficulty": "hard",
            "category": "Landmarks"
          },
          "expected_output": {
            "answer": "Eiffel Tower",
            "confidence": 0.9
          },
          "evaluators": [
            "EqualsExpected"
          ]
        }
      ]
    }
    """

```

1. Generate the Dataset exactly as above.
1. Save the dataset to a JSON file, this will also write `questions_cases_schema.json` with th JSON schema for `questions_cases.json`. This time the `$schema` key is included in the JSON file to define the schema for IDEs to use while you edit the file, there's no formal spec for this, but it works in vscode and pycharm and is discussed at length in [json-schema-org/json-schema-spec#828](https://github.com/json-schema-org/json-schema-spec/issues/828).

*(This example is complete, it can be run "as is" â€” you'll need to add `asyncio.run(main(answer))` to run `main`)*

## Integration with Logfire

Pydantic Evals is implemented using OpenTelemetry to record traces of the evaluation process. These traces contain all the information included in the terminal output as attributes, but also include full tracing from the executions of the evaluation task function.

You can send these traces to any OpenTelemetry-compatible backend, including [Pydantic Logfire](https://logfire.pydantic.dev/docs).

All you need to do is configure Logfire via `logfire.configure`:

logfire_integration.py

```python
import logfire
from judge_recipes import recipe_dataset, transform_recipe

logfire.configure(
    send_to_logfire='if-token-present',  # (1)!
    environment='development',  # (2)!
    service_name='evals',  # (3)!
)

recipe_dataset.evaluate_sync(transform_recipe)

```

1. The `send_to_logfire` argument controls when traces are sent to Logfire. You can set it to `'if-token-present'` to send data to Logfire only if the `LOGFIRE_TOKEN` environment variable is set. See the [Logfire configuration docs](https://logfire.pydantic.dev/docs/reference/configuration/) for more details.
1. The `environment` argument sets the environment for the traces. It's a good idea to set this to `'development'` when running tests or evaluations and sending data to a project with production data, to make it easier to filter these traces out while reviewing data from your production environment(s).
1. The `service_name` argument sets the service name for the traces. This is displayed in the Logfire UI to help you identify the source of the associated spans.

Logfire has some special integration with Pydantic Evals traces, including a table view of the evaluation results on the evaluation root span (which is generated in each call to Dataset.evaluate):

and a detailed view of the inputs and outputs for the execution of each case:

In addition, any OpenTelemetry spans generated during the evaluation process will be sent to Logfire, allowing you to visualize the full execution of the code called during the evaluation process:

This can be especially helpful when attempting to write evaluators that make use of the `span_tree` property of the EvaluatorContext, as described in the [OpenTelemetry Integration](#opentelemetry-integration) section above.

This allows you to write evaluations that depend on information about which code paths were executed during the call to the task function without needing to manually instrument the code being evaluated, as long as the code being evaluated is already adequately instrumented with OpenTelemetry. In the case of PydanticAI agents, for example, this can be used to ensure specific tools are (or are not) called during the execution of specific cases.

Using OpenTelemetry in this way also means that all data used to evaluate the task executions will be accessible in the traces produced by production runs of the code, making it straightforward to perform the same evaluations on production data.
# MCP

# Model Context Protocol (MCP)

PydanticAI supports [Model Context Protocol (MCP)](https://modelcontextprotocol.io) in three ways:

1. [Agents](../agents/) act as an MCP Client, connecting to MCP servers to use their tools, [learn more â€¦](client/)
1. Agents can be used within MCP servers, [learn more â€¦](server/)
1. As part of PydanticAI, we're building a number of MCP servers, [see below](#mcp-servers)

## What is MCP?

The Model Context Protocol is a standardized protocol that allow AI applications (including programmatic agents like PydanticAI, coding agents like [cursor](https://www.cursor.com/), and desktop applications like [Claude Desktop](https://claude.ai/download)) to connect to external tools and services using a common interface.

As with other protocols, the dream of MCP is that a wide range of applications can speak to each other without the need for specific integrations.

There is a great list of MCP servers at [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers).

Some examples of what this means:

- PydanticAI could use a web search service implemented as an MCP server to implement a deep research agent
- Cursor could connect to the [Pydantic Logfire](https://github.com/pydantic/logfire-mcp) MCP server to search logs, traces and metrics to gain context while fixing a bug
- PydanticAI, or any other MCP client could connect to our [Run Python](run-python/) MCP server to run arbitrary Python code in a sandboxed environment

## MCP Servers

To add functionality to PydanticAI while making it as widely usable as possible, we're implementing some functionality as MCP servers.

So far, we've only implemented one MCP server as part of PydanticAI:

- [Run Python](run-python/): A sandboxed Python interpreter that can run arbitrary code, with a focus on security and safety.

# Client

PydanticAI can act as an [MCP client](https://modelcontextprotocol.io/quickstart/client), connecting to MCP servers to use their tools.

## Install

You need to either install [`pydantic-ai`](../../install/), or[`pydantic-ai-slim`](../../install/#slim-install) with the `mcp` optional group:

```bash
pip install "pydantic-ai-slim[mcp]"

```

```bash
uv add "pydantic-ai-slim[mcp]"

```

Note

MCP integration requires Python 3.10 or higher.

## Usage

PydanticAI comes with two ways to connect to MCP servers:

- MCPServerHTTP which connects to an MCP server using the [HTTP SSE](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#http-with-sse) transport
- MCPServerStdio which runs the server as a subprocess and connects to it using the [stdio](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#stdio) transport

Examples of both are shown below; [mcp-run-python](../run-python/) is used as the MCP server in both examples.

### SSE Client

MCPServerHTTP connects over HTTP using the [HTTP + Server Sent Events transport](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#http-with-sse) to a server.

Note

MCPServerHTTP requires an MCP server to be running and accepting HTTP connections before calling agent.run_mcp_servers(). Running the server is not managed by PydanticAI.

The name "HTTP" is used since this implemented will be adapted in future to use the new [Streamable HTTP](https://github.com/modelcontextprotocol/specification/pull/206) currently in development.

Before creating the SSE client, we need to run the server (docs [here](../run-python/)):

terminal (run sse server)

```bash
deno run \
  -N -R=node_modules -W=node_modules --node-modules-dir=auto \
  jsr:@pydantic/mcp-run-python sse

```

mcp_sse_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

server = MCPServerHTTP(url='http://localhost:3001/sse')  # (1)!
agent = Agent('openai:gpt-4o', mcp_servers=[server])  # (2)!


async def main():
    async with agent.run_mcp_servers():  # (3)!
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    #> There are 9,208 days between January 1, 2000, and March 18, 2025.

```

1. Define the MCP server with the URL used to connect.
1. Create an agent with the MCP server attached.
1. Create a client session to connect to the server.

*(This example is complete, it can be run "as is" with Python 3.10+ â€” you'll need to add `asyncio.run(main())` to run `main`)*

**What's happening here?**

- The model is receiving the prompt "how many days between 2000-01-01 and 2025-03-18?"
- The model decides "Oh, I've got this `run_python_code` tool, that will be a good way to answer this question", and writes some python code to calculate the answer.
- The model returns a tool call
- PydanticAI sends the tool call to the MCP server using the SSE transport
- The model is called again with the return value of running the code
- The model returns the final answer

You can visualise this clearly, and even see the code that's run by adding three lines of code to instrument the example with [logfire](https://logfire.pydantic.dev/docs):

mcp_sse_client_logfire.py

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

```

Will display as follows:

### MCP "stdio" Server

The other transport offered by MCP is the [stdio transport](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#stdio) where the server is run as a subprocess and communicates with the client over `stdin` and `stdout`. In this case, you'd use the MCPServerStdio class.

Note

When using MCPServerStdio servers, the agent.run_mcp_servers() context manager is responsible for starting and stopping the server.

mcp_stdio_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

server = MCPServerStdio(  # (1)!
    'deno',
    args=[
        'run',
        '-N',
        '-R=node_modules',
        '-W=node_modules',
        '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio',
    ]
)
agent = Agent('openai:gpt-4o', mcp_servers=[server])


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    #> There are 9,208 days between January 1, 2000, and March 18, 2025.

```

1. See [MCP Run Python](../run-python/) for more information.

# MCP Run Python

The **MCP Run Python** package is an MCP server that allows agents to execute Python code in a secure, sandboxed environment. It uses [Pyodide](https://pyodide.org/) to run Python code in a JavaScript environment with [Deno](https://deno.com/), isolating execution from the host system.

## Features

- **Secure Execution**: Run Python code in a sandboxed WebAssembly environment
- **Package Management**: Automatically detects and installs required dependencies
- **Complete Results**: Captures standard output, standard error, and return values
- **Asynchronous Support**: Runs async code properly
- **Error Handling**: Provides detailed error reports for debugging

## Installation

Switch from npx to deno

We previously distributed `mcp-run-python` as an `npm` package to use via `npx`. We now recommend using `deno` instead as it provides better sandboxing and security.

The MCP Run Python server is distributed as a [JSR package](https://jsr.io/@pydantic/mcp-run-python) and can be run directly using [`deno run`](https://deno.com/):

terminal

```bash
deno run \
  -N -R=node_modules -W=node_modules --node-modules-dir=auto \
  jsr:@pydantic/mcp-run-python [stdio|sse|warmup]

```

where:

- `-N -R=node_modules -W=node_modules` (alias of `--allow-net --allow-read=node_modules --allow-write=node_modules`) allows network access and read+write access to `./node_modules`. These are required so Pyodide can download and cache the Python standard library and packages
- `--node-modules-dir=auto` tells deno to use a local `node_modules` directory
- `stdio` runs the server with the [Stdio MCP transport](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#stdio) â€” suitable for running the process as a subprocess locally
- `sse` runs the server with the [SSE MCP transport](https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#http-with-sse) â€” running the server as an HTTP server to connect locally or remotely
- `warmup` will run a minimal Python script to download and cache the Python standard library. This is also useful to check the server is running correctly.

Usage of `jsr:@pydantic/mcp-run-python` with PydanticAI is described in the [client](../client/#mcp-stdio-server) documentation.

## Direct Usage

As well as using this server with PydanticAI, it can be connected to other MCP clients. For clarity, in this example we connect directly using the [Python MCP client](https://github.com/modelcontextprotocol/python-sdk).

mcp_run_python.py

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

code = """
import numpy
a = numpy.array([1, 2, 3])
print(a)
a
"""
server_params = StdioServerParameters(
    command='deno',
    args=[
        'run',
        '-N',
        '-R=node_modules',
        '-W=node_modules',
        '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio',
    ],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(len(tools.tools))
            #> 1
            print(repr(tools.tools[0].name))
            #> 'run_python_code'
            print(repr(tools.tools[0].inputSchema))
            """
            {'type': 'object', 'properties': {'python_code': {'type': 'string', 'description': 'Python code to run'}}, 'required': ['python_code'], 'additionalProperties': False, '$schema': 'http://json-schema.org/draft-07/schema#'}
            """
            result = await session.call_tool('run_python_code', {'python_code': code})
            print(result.content[0].text)
            """
            <status>success</status>
            <dependencies>["numpy"]</dependencies>
            <output>
            [1 2 3]
            </output>
            <return_value>
            [
              1,
              2,
              3
            ]
            </return_value>
            """

```

If an exception occurs, `status` will be `install-error` or `run-error` and `return_value` will be replaced by `error` which will include the traceback and exception message.

## Dependencies

Dependencies are installed when code is run.

Dependencies can be defined in one of two ways:

### Inferred from imports

If there's no metadata, dependencies are inferred from imports in the code, as shown in the example [above](#direct-usage).

### Inline script metadata

As introduced in PEP 723, explained [here](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata), and popularized by [uv](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) â€” dependencies can be defined in a comment at the top of the file.

This allows use of dependencies that aren't imported in the code, and is more explicit.

inline_script_metadata.py

```py
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# using `server_params` from the above example.
from mcp_run_python import server_params

code = """\
# /// script
# dependencies = ["pydantic", "email-validator"]
# ///
import pydantic

class Model(pydantic.BaseModel):
    email: pydantic.EmailStr

print(Model(email='hello@pydantic.dev'))
"""


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool('run_python_code', {'python_code': code})
            print(result.content[0].text)
            """
            <status>success</status>
            <dependencies>["pydantic","email-validator"]</dependencies>
            <output>
            email='hello@pydantic.dev'
            </output>
            """

```

It also allows versions to be pinned for non-binary packages (Pyodide only supports a single version for the binary packages it supports, like `pydantic` and `numpy`).

E.g. you could set the dependencies to

```python
# /// script
# dependencies = ["rich<13"]
# ///

```

## Logging

MCP Run Python supports emitting stdout and stderr from the python execution as [MCP logging messages](https://github.com/modelcontextprotocol/specification/blob/eb4abdf2bb91e0d5afd94510741eadd416982350/docs/specification/draft/server/utilities/logging.md?plain=1).

For logs to be emitted you must set the logging level when connecting to the server. By default, the log level is set to the highest level, `emergency`.

Currently, it's not possible to demonstrate this due to a bug in the Python MCP Client, see [modelcontextprotocol/python-sdk#201](https://github.com/modelcontextprotocol/python-sdk/issues/201#issuecomment-2727663121).

# Server

PydanticAI models can also be used within MCP Servers.

Here's a simple example of a [Python MCP server](https://github.com/modelcontextprotocol/python-sdk) using PydanticAI within a tool call:

mcp_server.py

```py
from mcp.server.fastmcp import FastMCP

from pydantic_ai import Agent

server = FastMCP('PydanticAI Server')
server_agent = Agent(
    'anthropic:claude-3-5-haiku-latest', system_prompt='always reply in rhyme'
)


@server.tool()
async def poet(theme: str) -> str:
    """Poem generator"""
    r = await server_agent.run(f'write a poem about {theme}')
    return r.output


if __name__ == '__main__':
    server.run()

```

This server can be queried with any MCP client. Here is an example using a direct Python client:

mcp_client.py

```py
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def client():
    server_params = StdioServerParameters(
        command='uv', args=['run', 'mcp_server.py', 'server'], env=os.environ
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool('poet', {'theme': 'socks'})
            print(result.content[0].text)
            """
            Oh, socks, those garments soft and sweet,
            That nestle softly 'round our feet,
            From cotton, wool, or blended thread,
            They keep our toes from feeling dread.
            """


if __name__ == '__main__':
    asyncio.run(client())

```

Note: [sampling](https://modelcontextprotocol.io/docs/concepts/sampling#sampling), whereby servers may request LLM completions from the client, is not yet supported in PydanticAI.
# Optional

# Command Line Interface (CLI)

**PydanticAI** comes with a CLI, `clai` (pronounced "clay") which you can use to interact with various LLMs from the command line. It provides a convenient way to chat with language models and quickly get answers right in the terminal.

We originally developed this CLI for our own use, but found ourselves using it so frequently that we decided to share it as part of the PydanticAI package.

We plan to continue adding new features, such as interaction with MCP servers, access to tools, and more.

## Usage

You'll need to set an environment variable depending on the provider you intend to use.

E.g. if you're using OpenAI, set the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY='your-api-key-here'

```

Then with [`uvx`](https://docs.astral.sh/uv/guides/tools/), run:

```bash
uvx clai

```

Or to install `clai` globally [with `uv`](https://docs.astral.sh/uv/guides/tools/#installing-tools), run:

```bash
uv tool install clai
...
clai

```

Or with `pip`, run:

```bash
pip install clai
...
clai

```

Either way, running `clai` will start an interactive session where you can chat with the AI model. Special commands available in interactive mode:

- `/exit`: Exit the session
- `/markdown`: Show the last response in markdown format
- `/multiline`: Toggle multiline input mode (use Ctrl+D to submit)

### Help

To get help on the CLI, use the `--help` flag:

```bash
uvx clai --help

```

### Choose a model

You can specify which model to use with the `--model` flag:

```bash
uvx clai --model anthropic:claude-3-7-sonnet-latest

```

(a full list of models available can be printed with `uvx clai --list-models`)

### Custom Agents

You can specify a custom agent using the `--agent` flag with a module path and variable name:

custom_agent.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You always respond in Italian.')

```

Then run:

```bash
uvx clai --agent custom_agent:agent "What's the weather today?"

```

The format must be `module:variable` where:

- `module` is the importable Python module path
- `variable` is the name of the Agent instance in that module

Additionally, you can directly launch CLI mode from an `Agent` instance using `Agent.to_cli_sync()`:

agent_to_cli_sync.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You always respond in Italian.')
agent.to_cli_sync()

```

You can also use the async interface with `Agent.to_cli()`:

agent_to_cli.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o', instructions='You always respond in Italian.')

async def main():
    await agent.to_cli()

```

*(You'll need to add `asyncio.run(main())` to run `main`)*

# Debugging and Monitoring

Applications that use LLMs have some challenges that are well known and understood: LLMs are **slow**, **unreliable** and **expensive**.

These applications also have some challenges that most developers have encountered much less often: LLMs are **fickle** and **non-deterministic**. Subtle changes in a prompt can completely change a model's performance, and there's no `EXPLAIN` query you can run to understand why.

Warning

From a software engineers point of view, you can think of LLMs as the worst database you've ever heard of, but worse.

If LLMs weren't so bloody useful, we'd never touch them.

To build successful applications with LLMs, we need new tools to understand both model performance, and the behavior of applications that rely on them.

LLM Observability tools that just let you understand how your model is performing are useless: making API calls to an LLM is easy, it's building that into an application that's hard.

## Pydantic Logfire

[Pydantic Logfire](https://pydantic.dev/logfire) is an observability platform developed by the team who created and maintain Pydantic and PydanticAI. Logfire aims to let you understand your entire application: Gen AI, classic predictive AI, HTTP traffic, database queries and everything else a modern application needs, all using OpenTelemetry.

Pydantic Logfire is a commercial product

Logfire is a commercially supported, hosted platform with an extremely generous and perpetual [free tier](https://pydantic.dev/pricing/). You can sign up and start using Logfire in a couple of minutes.

PydanticAI has built-in (but optional) support for Logfire. That means if the `logfire` package is installed and configured and agent instrumentation is enabled then detailed information about agent runs is sent to Logfire. Otherwise there's virtually no overhead and nothing is sent.

Here's an example showing details of running the [Weather Agent](../examples/weather-agent/) in Logfire:

A trace is generated for the agent run, and spans are emitted for each model request and tool call.

## Using Logfire

To use Logfire, you'll need a Logfire [account](https://logfire.pydantic.dev), and the Logfire Python SDK installed:

```bash
pip install "pydantic-ai[logfire]"

```

```bash
uv add "pydantic-ai[logfire]"

```

Then authenticate your local environment with Logfire:

```bash
 logfire auth

```

```bash
uv run logfire auth

```

And configure a project to send data to:

```bash
 logfire projects new

```

```bash
uv run logfire projects new

```

(Or use an existing project with `logfire projects use`)

This will write to a `.logfire` directory in the current working directory, which the Logfire SDK will use for configuration at run time.

With that, you can start using Logfire to instrument PydanticAI code:

instrument_pydantic_ai.py

```python
import logfire

from pydantic_ai import Agent

logfire.configure()  # (1)!
logfire.instrument_pydantic_ai()  # (2)!

agent = Agent('openai:gpt-4o', instructions='Be concise, reply with one sentence.')
result = agent.run_sync('Where does "hello world" come from?')  # (3)!
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""

```

1. logfire.configure() configures the SDK, by default it will find the write token from the `.logfire` directory, but you can also pass a token directly.
1. logfire.instrument_pydantic_ai() enables instrumentation of PydanticAI.
1. Since we've enabled instrumentation, a trace will be generated for each run, with spans emitted for models calls and tool function execution

*(This example is complete, it can be run "as is")*

Which will display in Logfire thus:

The [logfire documentation](https://logfire.pydantic.dev/docs/) has more details on how to use Logfire, including how to instrument other libraries like [HTTPX](https://logfire.pydantic.dev/docs/integrations/http-clients/httpx/) and [FastAPI](https://logfire.pydantic.dev/docs/integrations/web-frameworks/fastapi/).

Since Logfire is built on [OpenTelemetry](https://opentelemetry.io/), you can use the Logfire Python SDK to send data to any OpenTelemetry collector, see [below](#using-opentelemetry).

### Debugging

To demonstrate how Logfire can let you visualise the flow of a PydanticAI run, here's the view you get from Logfire while running the [chat app examples](../examples/chat-app/):

### Monitoring Performance

We can also query data with SQL in Logfire to monitor the performance of an application. Here's a real world example of using Logfire to monitor PydanticAI runs inside Logfire itself:

### Monitoring HTTP Requests

"F\*\*k you, show me the prompt."

As per Hamel Husain's influential 2024 blog post ["Fuck You, Show Me The Prompt."](https://hamel.dev/blog/posts/prompt/) (bear with the capitalization, the point is valid), it's often useful to be able to view the raw HTTP requests and responses made to model providers.

To observe raw HTTP requests made to model providers, you can use `logfire`'s [HTTPX instrumentation](https://logfire.pydantic.dev/docs/integrations/http-clients/httpx/) since all provider SDKs use the [HTTPX](https://www.python-httpx.org/) library internally.

with_logfire_instrument_httpx.py

```py
import logfire

from pydantic_ai import Agent

logfire.configure()
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)  # (1)!
agent = Agent('openai:gpt-4o')
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris

```

1. See the logfire.instrument_httpx docs more details, `capture_all=True` means both headers and body are captured for both the request and response.

without_logfire_instrument_httpx.py

```py
import logfire

from pydantic_ai import Agent

logfire.configure()
logfire.instrument_pydantic_ai()

agent = Agent('openai:gpt-4o')
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris

```

## Using OpenTelemetry

PydanticAI's instrumentation uses [OpenTelemetry](https://opentelemetry.io/) (OTel), which Logfire is based on.

This means you can debug and monitor PydanticAI with any OpenTelemetry backend.

PydanticAI follows the [OpenTelemetry Semantic Conventions for Generative AI systems](https://opentelemetry.io/docs/specs/semconv/gen-ai/), so while we think you'll have the best experience using the Logfire platform , you should be able to use any OTel service with GenAI support.

### Logfire with an alternative OTel backend

You can use the Logfire SDK completely freely and send the data to any OpenTelemetry backend.

Here's an example of configuring the Logfire library to send data to the excellent [otel-tui](https://github.com/ymtdzzz/otel-tui) â€” an open source terminal based OTel backend and viewer (no association with Pydantic).

Run `otel-tui` with docker (see [the otel-tui readme](https://github.com/ymtdzzz/otel-tui) for more instructions):

Terminal

```text
docker run --rm -it -p 4318:4318 --name otel-tui ymtdzzz/otel-tui:latest

```

then run,

otel_tui.py

```python
import os

import logfire

from pydantic_ai import Agent

os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4318'  # (1)!
logfire.configure(send_to_logfire=False)  # (2)!
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)

agent = Agent('openai:gpt-4o')
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris

```

1. Set the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable to the URL of your OpenTelemetry backend. If you're using a backend that requires authentication, you may need to set [other environment variables](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/). Of course, these can also be set outside the process, e.g. with `export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318`.
1. We configure Logfire to disable sending data to the Logfire OTel backend itself. If you removed `send_to_logfire=False`, data would be sent to both Logfire and your OpenTelemetry backend.

Running the above code will send tracing data to `otel-tui`, which will display like this:

Running the [weather agent](../examples/weather-agent/) example connected to `otel-tui` shows how it can be used to visualise a more complex trace:

For more information on using the Logfire SDK to send data to alternative backends, see [the Logfire documentation](https://logfire.pydantic.dev/docs/how-to-guides/alternative-backends/).

### OTel without Logfire

You can also emit OpenTelemetry data from PydanticAI without using Logfire at all.

To do this, you'll need to install and configure the OpenTelemetry packages you need. To run the following examples, use

Terminal

```text
uv run \
  --with 'pydantic-ai-slim[openai]' \
  --with opentelemetry-sdk \
  --with opentelemetry-exporter-otlp \
  raw_otel.py

```

raw_otel.py

```python
import os

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider

from pydantic_ai.agent import Agent

os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4318'
exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(exporter)
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(span_processor)

set_tracer_provider(tracer_provider)

Agent.instrument_all()
agent = Agent('openai:gpt-4o')
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris

```

## Data format

PydanticAI follows the [OpenTelemetry Semantic Conventions for Generative AI systems](https://opentelemetry.io/docs/specs/semconv/gen-ai/), with one caveat. The semantic conventions specify that messages should be captured as individual events (logs) that are children of the request span. By default, PydanticAI instead collects these events into a JSON array which is set as a single large attribute called `events` on the request span. To change this, use InstrumentationSettings(event_mode='logs').

instrumentation_settings_event_mode.py

```python
import logfire

from pydantic_ai import Agent

logfire.configure()
logfire.instrument_pydantic_ai(event_mode='logs')
agent = Agent('openai:gpt-4o')
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> Paris

```

For now, this won't look as good in the Logfire UI, but we're working on it.

If you have very long conversations, the `events` span attribute may be truncated. Using `event_mode='logs'` will help avoid this issue.

Note that the OpenTelemetry Semantic Conventions are still experimental and are likely to change.

## Setting OpenTelemetry SDK providers

By default, the global `TracerProvider` and `EventLoggerProvider` are used. These are set automatically by `logfire.configure()`. They can also be set by the `set_tracer_provider` and `set_event_logger_provider` functions in the OpenTelemetry Python SDK. You can set custom providers with InstrumentationSettings.

instrumentation_settings_providers.py

```python
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.sdk.trace import TracerProvider

from pydantic_ai.agent import InstrumentationSettings

instrumentation_settings = InstrumentationSettings(
    tracer_provider=TracerProvider(),
    event_logger_provider=EventLoggerProvider(),
)

```

## Instrumenting a specific `Model`

instrumented_model_example.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings, InstrumentedModel

settings = InstrumentationSettings()
model = InstrumentedModel('gpt-4o', settings)
agent = Agent(model)

```

# Unit testing

Writing unit tests for PydanticAI code is just like unit tests for any other Python code.

Because for the most part they're nothing new, we have pretty well established tools and patterns for writing and running these kinds of tests.

Unless you're really sure you know better, you'll probably want to follow roughly this strategy:

- Use [`pytest`](https://docs.pytest.org/en/stable/) as your test harness
- If you find yourself typing out long assertions, use [inline-snapshot](https://15r10nk.github.io/inline-snapshot/latest/)
- Similarly, [dirty-equals](https://dirty-equals.helpmanual.io/latest/) can be useful for comparing large data structures
- Use TestModel or FunctionModel in place of your actual model to avoid the usage, latency and variability of real LLM calls
- Use Agent.override to replace your model inside your application logic
- Set ALLOW_MODEL_REQUESTS=False globally to block any requests from being made to non-test models accidentally

### Unit testing with `TestModel`

The simplest and fastest way to exercise most of your application code is using TestModel, this will (by default) call all tools in the agent, then return either plain text or a structured response depending on the return type of the agent.

`TestModel` is not magic

The "clever" (but not too clever) part of `TestModel` is that it will attempt to generate valid structured data for [function tools](../tools/) and [output types](../output/#structured-output) based on the schema of the registered tools.

There's no ML or AI in `TestModel`, it's just plain old procedural Python code that tries to generate data that satisfies the JSON schema of a tool.

The resulting data won't look pretty or relevant, but it should pass Pydantic's validation in most cases. If you want something more sophisticated, use FunctionModel and write your own data generation logic.

Let's write unit tests for the following application code:

weather_app.py

```python
import asyncio
from datetime import date

from pydantic_ai import Agent, RunContext

from fake_database import DatabaseConn  # (1)!
from weather_service import WeatherService  # (2)!

weather_agent = Agent(
    'openai:gpt-4o',
    deps_type=WeatherService,
    system_prompt='Providing a weather forecast at the locations the user provides.',
)


@weather_agent.tool
def weather_forecast(
    ctx: RunContext[WeatherService], location: str, forecast_date: date
) -> str:
    if forecast_date < date.today():  # (3)!
        return ctx.deps.get_historic_weather(location, forecast_date)
    else:
        return ctx.deps.get_forecast(location, forecast_date)


async def run_weather_forecast(  # (4)!
    user_prompts: list[tuple[str, int]], conn: DatabaseConn
):
    """Run weather forecast for a list of user prompts and save."""
    async with WeatherService() as weather_service:

        async def run_forecast(prompt: str, user_id: int):
            result = await weather_agent.run(prompt, deps=weather_service)
            await conn.store_forecast(user_id, result.output)

        # run all prompts in parallel
        await asyncio.gather(
            *(run_forecast(prompt, user_id) for (prompt, user_id) in user_prompts)
        )

```

1. `DatabaseConn` is a class that holds a database connection
1. `WeatherService` has methods to get weather forecasts and historic data about the weather
1. We need to call a different endpoint depending on whether the date is in the past or the future, you'll see why this nuance is important below
1. This function is the code we want to test, together with the agent it uses

Here we have a function that takes a list of `(user_prompt, user_id)` tuples, gets a weather forecast for each prompt, and stores the result in the database.

**We want to test this code without having to mock certain objects or modify our code so we can pass test objects in.**

Here's how we would write tests using TestModel:

test_weather_app.py

```python
from datetime import timezone
import pytest

from dirty_equals import IsNow, IsStr

from pydantic_ai import models, capture_run_messages
from pydantic_ai.models.test import TestModel
from pydantic_ai.messages import (
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
    ModelRequest,
)
from pydantic_ai.usage import Usage

from fake_database import DatabaseConn
from weather_app import run_weather_forecast, weather_agent

pytestmark = pytest.mark.anyio  # (1)!
models.ALLOW_MODEL_REQUESTS = False  # (2)!


async def test_forecast():
    conn = DatabaseConn()
    user_id = 1
    with capture_run_messages() as messages:
        with weather_agent.override(model=TestModel()):  # (3)!
            prompt = 'What will the weather be like in London on 2024-11-28?'
            await run_weather_forecast([(prompt, user_id)], conn)  # (4)!

    forecast = await conn.get_forecast(user_id)
    assert forecast == '{"weather_forecast":"Sunny with a chance of rain"}'  # (5)!

    assert messages == [  # (6)!
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content='Providing a weather forecast at the locations the user provides.',
                    timestamp=IsNow(tz=timezone.utc),
                ),
                UserPromptPart(
                    content='What will the weather be like in London on 2024-11-28?',
                    timestamp=IsNow(tz=timezone.utc),  # (7)!
                ),
            ]
        ),
        ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name='weather_forecast',
                    args={
                        'location': 'a',
                        'forecast_date': '2024-01-01',  # (8)!
                    },
                    tool_call_id=IsStr(),
                )
            ],
            usage=Usage(
                requests=1,
                request_tokens=71,
                response_tokens=7,
                total_tokens=78,
                details=None,
            ),
            model_name='test',
            timestamp=IsNow(tz=timezone.utc),
        ),
        ModelRequest(
            parts=[
                ToolReturnPart(
                    tool_name='weather_forecast',
                    content='Sunny with a chance of rain',
                    tool_call_id=IsStr(),
                    timestamp=IsNow(tz=timezone.utc),
                ),
            ],
        ),
        ModelResponse(
            parts=[
                TextPart(
                    content='{"weather_forecast":"Sunny with a chance of rain"}',
                )
            ],
            usage=Usage(
                requests=1,
                request_tokens=77,
                response_tokens=16,
                total_tokens=93,
                details=None,
            ),
            model_name='test',
            timestamp=IsNow(tz=timezone.utc),
        ),
    ]

```

1. We're using [anyio](https://anyio.readthedocs.io/en/stable/) to run async tests.
1. This is a safety measure to make sure we don't accidentally make real requests to the LLM while testing, see ALLOW_MODEL_REQUESTS for more details.
1. We're using Agent.override to replace the agent's model with TestModel, the nice thing about `override` is that we can replace the model inside agent without needing access to the agent `run*` methods call site.
1. Now we call the function we want to test inside the `override` context manager.
1. But default, `TestModel` will return a JSON string summarising the tools calls made, and what was returned. If you wanted to customise the response to something more closely aligned with the domain, you could add custom_output_text='Sunny' when defining `TestModel`.
1. So far we don't actually know which tools were called and with which values, we can use capture_run_messages to inspect messages from the most recent run and assert the exchange between the agent and the model occurred as expected.
1. The IsNow helper allows us to use declarative asserts even with data which will contain timestamps that change over time.
1. `TestModel` isn't doing anything clever to extract values from the prompt, so these values are hardcoded.

### Unit testing with `FunctionModel`

The above tests are a great start, but careful readers will notice that the `WeatherService.get_forecast` is never called since `TestModel` calls `weather_forecast` with a date in the past.

To fully exercise `weather_forecast`, we need to use FunctionModel to customise how the tools is called.

Here's an example of using `FunctionModel` to test the `weather_forecast` tool with custom inputs

test_weather_app2.py

```python
import re

import pytest

from pydantic_ai import models
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    TextPart,
    ToolCallPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

from fake_database import DatabaseConn
from weather_app import run_weather_forecast, weather_agent

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


def call_weather_forecast(  # (1)!
    messages: list[ModelMessage], info: AgentInfo
) -> ModelResponse:
    if len(messages) == 1:
        # first call, call the weather forecast tool
        user_prompt = messages[0].parts[-1]
        m = re.search(r'\d{4}-\d{2}-\d{2}', user_prompt.content)
        assert m is not None
        args = {'location': 'London', 'forecast_date': m.group()}  # (2)!
        return ModelResponse(parts=[ToolCallPart('weather_forecast', args)])
    else:
        # second call, return the forecast
        msg = messages[-1].parts[0]
        assert msg.part_kind == 'tool-return'
        return ModelResponse(parts=[TextPart(f'The forecast is: {msg.content}')])


async def test_forecast_future():
    conn = DatabaseConn()
    user_id = 1
    with weather_agent.override(model=FunctionModel(call_weather_forecast)):  # (3)!
        prompt = 'What will the weather be like in London on 2032-01-01?'
        await run_weather_forecast([(prompt, user_id)], conn)

    forecast = await conn.get_forecast(user_id)
    assert forecast == 'The forecast is: Rainy with a chance of sun'

```

1. We define a function `call_weather_forecast` that will be called by `FunctionModel` in place of the LLM, this function has access to the list of ModelMessages that make up the run, and AgentInfo which contains information about the agent and the function tools and return tools.
1. Our function is slightly intelligent in that it tries to extract a date from the prompt, but just hard codes the location.
1. We use FunctionModel to replace the agent's model with our custom function.

### Overriding model via pytest fixtures

If you're writing lots of tests that all require model to be overridden, you can use [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) to override the model with TestModel or FunctionModel in a reusable way.

Here's an example of a fixture that overrides the model with `TestModel`:

tests.py

```python
import pytest
from weather_app import weather_agent

from pydantic_ai.models.test import TestModel


@pytest.fixture
def override_weather_agent():
    with weather_agent.override(model=TestModel()):
        yield


async def test_forecast(override_weather_agent: None):
    ...
    # test code here

```

# Examples

Examples of how to use PydanticAI and what it can do.

## Usage

These examples are distributed with `pydantic-ai` so you can run them either by cloning the [pydantic-ai repo](https://github.com/pydantic/pydantic-ai) or by simply installing `pydantic-ai` from PyPI with `pip` or `uv`.

### Installing required dependencies

Either way you'll need to install extra dependencies to run some examples, you just need to install the `examples` optional dependency group.

If you've installed `pydantic-ai` via pip/uv, you can install the extra dependencies with:

```bash
pip install "pydantic-ai[examples]"

```

```bash
uv add "pydantic-ai[examples]"

```

If you clone the repo, you should instead use `uv sync --extra examples` to install extra dependencies.

### Setting model environment variables

These examples will need you to set up authentication with one or more of the LLMs, see the [model configuration](../models/) docs for details on how to do this.

TL;DR: in most cases you'll need to set one of the following environment variables:

```bash
export OPENAI_API_KEY=your-api-key

```

```bash
export GEMINI_API_KEY=your-api-key

```

### Running Examples

To run the examples (this will work whether you installed `pydantic_ai`, or cloned the repo), run:

```bash
python -m pydantic_ai_examples.<example_module_name>

```

```bash
uv run -m pydantic_ai_examples.<example_module_name>

```

For examples, to run the very simple [`pydantic_model`](pydantic-model/) example:

```bash
python -m pydantic_ai_examples.pydantic_model

```

```bash
uv run -m pydantic_ai_examples.pydantic_model

```

If you like one-liners and you're using uv, you can run a pydantic-ai example with zero setup:

```bash
OPENAI_API_KEY='your-api-key' \
  uv run --with "pydantic-ai[examples]" \
  -m pydantic_ai_examples.pydantic_model

```

______________________________________________________________________

You'll probably want to edit examples in addition to just running them. You can copy the examples to a new directory with:

```bash
python -m pydantic_ai_examples --copy-to examples/

```

```bash
uv run -m pydantic_ai_examples --copy-to examples/

```

Small but complete example of using PydanticAI to build a support agent for a bank.

Demonstrates:

- [dynamic system prompt](../../agents/#system-prompts)
- [structured `output_type`](../../output/#structured-output)
- [tools](../../tools/)

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.bank_support

```

```bash
uv run -m pydantic_ai_examples.bank_support

```

(or `PYDANTIC_AI_MODEL=gemini-1.5-flash ...`)

## Example Code

bank_support.py

```python
from dataclasses import dataclass

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext


class DatabaseConn:
    """This is a fake database for example purposes.

    In reality, you'd be connecting to an external database
    (e.g. PostgreSQL) to get information about customers.
    """

    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return 'John'

    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        if id == 123 and include_pending:
            return 123.45
        else:
            raise ValueError('Customer not found')


@dataclass
class SupportDependencies:
    customer_id: int
    db: DatabaseConn


class SupportOutput(BaseModel):
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description='Whether to block their card or not')
    risk: int = Field(description='Risk level of query', ge=0, le=10)


support_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    system_prompt=(
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query. '
        "Reply using the customer's name."
    ),
)


@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"The customer's name is {customer_name!r}"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> str:
    """Returns the customer's current account balance."""
    balance = await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )
    return f'${balance:.2f}'


if __name__ == '__main__':
    deps = SupportDependencies(customer_id=123, db=DatabaseConn())
    result = support_agent.run_sync('What is my balance?', deps=deps)
    print(result.output)
    """
    support_advice='Hello John, your current account balance, including pending transactions, is $123.45.' block_card=False risk=1
    """

    result = support_agent.run_sync('I just lost my card!', deps=deps)
    print(result.output)
    """
    support_advice="I'm sorry to hear that, John. We are temporarily blocking your card to prevent unauthorized transactions." block_card=True risk=8
    """

```

# Chat App with FastAPI

Simple chat app example build with FastAPI.

Demonstrates:

- [reusing chat history](../../message-history/)
- [serializing messages](../../message-history/#accessing-messages-from-results)
- [streaming responses](../../output/#streamed-results)

This demonstrates storing chat history between requests and using it to give the model context for new responses.

Most of the complex logic here is between `chat_app.py` which streams the response to the browser, and `chat_app.ts` which renders messages in the browser.

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.chat_app

```

```bash
uv run -m pydantic_ai_examples.chat_app

```

Then open the app at [localhost:8000](http://localhost:8000).

## Example Code

Python code that runs the chat app:

chat_app.py

```python
from __future__ import annotations as _annotations

import asyncio
import json
import sqlite3
from collections.abc import AsyncIterator
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, TypeVar

import fastapi
import logfire
from fastapi import Depends, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from typing_extensions import LiteralString, ParamSpec, TypedDict

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelMessage,
    ModelMessagesTypeAdapter,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()

agent = Agent('openai:gpt-4o')
THIS_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
    async with Database.connect() as db:
        yield {'db': db}


app = fastapi.FastAPI(lifespan=lifespan)
logfire.instrument_fastapi(app)


@app.get('/')
async def index() -> FileResponse:
    return FileResponse((THIS_DIR / 'chat_app.html'), media_type='text/html')


@app.get('/chat_app.ts')
async def main_ts() -> FileResponse:
    """Get the raw typescript code, it's compiled in the browser, forgive me."""
    return FileResponse((THIS_DIR / 'chat_app.ts'), media_type='text/plain')


async def get_db(request: Request) -> Database:
    return request.state.db


@app.get('/chat/')
async def get_chat(database: Database = Depends(get_db)) -> Response:
    msgs = await database.get_messages()
    return Response(
        b'\n'.join(json.dumps(to_chat_message(m)).encode('utf-8') for m in msgs),
        media_type='text/plain',
    )


class ChatMessage(TypedDict):
    """Format of messages sent to the browser."""

    role: Literal['user', 'model']
    timestamp: str
    content: str


def to_chat_message(m: ModelMessage) -> ChatMessage:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            assert isinstance(first_part.content, str)
            return {
                'role': 'user',
                'timestamp': first_part.timestamp.isoformat(),
                'content': first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                'role': 'model',
                'timestamp': m.timestamp.isoformat(),
                'content': first_part.content,
            }
    raise UnexpectedModelBehavior(f'Unexpected message type for chat app: {m}')


@app.post('/chat/')
async def post_chat(
    prompt: Annotated[str, fastapi.Form()], database: Database = Depends(get_db)
) -> StreamingResponse:
    async def stream_messages():
        """Streams new line delimited JSON `Message`s to the client."""
        # stream the user prompt so that can be displayed straight away
        yield (
            json.dumps(
                {
                    'role': 'user',
                    'timestamp': datetime.now(tz=timezone.utc).isoformat(),
                    'content': prompt,
                }
            ).encode('utf-8')
            + b'\n'
        )
        # get the chat history so far to pass as context to the agent
        messages = await database.get_messages()
        # run the agent with the user prompt and the chat history
        async with agent.run_stream(prompt, message_history=messages) as result:
            async for text in result.stream(debounce_by=0.01):
                # text here is a `str` and the frontend wants
                # JSON encoded ModelResponse, so we create one
                m = ModelResponse(parts=[TextPart(text)], timestamp=result.timestamp())
                yield json.dumps(to_chat_message(m)).encode('utf-8') + b'\n'

        # add new messages (e.g. the user prompt and the agent response in this case) to the database
        await database.add_messages(result.new_messages_json())

    return StreamingResponse(stream_messages(), media_type='text/plain')


P = ParamSpec('P')
R = TypeVar('R')


@dataclass
class Database:
    """Rudimentary database to store chat messages in SQLite.

    The SQLite standard library package is synchronous, so we
    use a thread pool executor to run queries asynchronously.
    """

    con: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor

    @classmethod
    @asynccontextmanager
    async def connect(
        cls, file: Path = THIS_DIR / '.chat_app_messages.sqlite'
    ) -> AsyncIterator[Database]:
        with logfire.span('connect to DB'):
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            con = await loop.run_in_executor(executor, cls._connect, file)
            slf = cls(con, loop, executor)
        try:
            yield slf
        finally:
            await slf._asyncify(con.close)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        con = sqlite3.connect(str(file))
        con = logfire.instrument_sqlite3(con)
        cur = con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS messages (id INT PRIMARY KEY, message_list TEXT);'
        )
        con.commit()
        return con

    async def add_messages(self, messages: bytes):
        await self._asyncify(
            self._execute,
            'INSERT INTO messages (message_list) VALUES (?);',
            messages,
            commit=True,
        )
        await self._asyncify(self.con.commit)

    async def get_messages(self) -> list[ModelMessage]:
        c = await self._asyncify(
            self._execute, 'SELECT message_list FROM messages order by id'
        )
        rows = await self._asyncify(c.fetchall)
        messages: list[ModelMessage] = []
        for row in rows:
            messages.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
        return messages

    def _execute(
        self, sql: LiteralString, *args: Any, commit: bool = False
    ) -> sqlite3.Cursor:
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def _asyncify(
        self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        return await self._loop.run_in_executor(  # type: ignore
            self._executor,
            partial(func, **kwargs),
            *args,  # type: ignore
        )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'pydantic_ai_examples.chat_app:app', reload=True, reload_dirs=[str(THIS_DIR)]
    )

```

Simple HTML page to render the app:

chat_app.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat App</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    main {
      max-width: 700px;
    }
    #conversation .user::before {
      content: 'You asked: ';
      font-weight: bold;
      display: block;
    }
    #conversation .model::before {
      content: 'AI Response: ';
      font-weight: bold;
      display: block;
    }
    #spinner {
      opacity: 0;
      transition: opacity 500ms ease-in;
      width: 30px;
      height: 30px;
      border: 3px solid #222;
      border-bottom-color: transparent;
      border-radius: 50%;
      animation: rotation 1s linear infinite;
    }
    @keyframes rotation {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    #spinner.active {
      opacity: 1;
    }
  </style>
</head>
<body>
  <main class="border rounded mx-auto my-5 p-4">
    <h1>Chat App</h1>
    <p>Ask me anything...</p>
    <div id="conversation" class="px-2"></div>
    <div class="d-flex justify-content-center mb-3">
      <div id="spinner"></div>
    </div>
    <form method="post">
      <input id="prompt-input" name="prompt" class="form-control"/>
      <div class="d-flex justify-content-end">
        <button class="btn btn-primary mt-2">Send</button>
      </div>
    </form>
    <div id="error" class="d-none text-danger">
      Error occurred, check the browser developer console for more information.
    </div>
  </main>
</body>
</html>
<script src="https://cdnjs.cloudflare.com/ajax/libs/typescript/5.6.3/typescript.min.js" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script type="module">
  // to let me write TypeScript, without adding the burden of npm we do a dirty, non-production-ready hack
  // and transpile the TypeScript code in the browser
  // this is (arguably) A neat demo trick, but not suitable for production!
  async function loadTs() {
    const response = await fetch('/chat_app.ts');
    const tsCode = await response.text();
    const jsCode = window.ts.transpile(tsCode, { target: "es2015" });
    let script = document.createElement('script');
    script.type = 'module';
    script.text = jsCode;
    document.body.appendChild(script);
  }

  loadTs().catch((e) => {
    console.error(e);
    document.getElementById('error').classList.remove('d-none');
    document.getElementById('spinner').classList.remove('active');
  });
</script>

```

TypeScript to handle rendering the messages, to keep this simple (and at the risk of offending frontend developers) the typescript code is passed to the browser as plain text and transpiled in the browser.

chat_app.ts

```ts
// BIG FAT WARNING: to avoid the complexity of npm, this typescript is compiled in the browser
// there's currently no static type checking

import { marked } from 'https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.0/lib/marked.esm.js'
const convElement = document.getElementById('conversation')

const promptInput = document.getElementById('prompt-input') as HTMLInputElement
const spinner = document.getElementById('spinner')

// stream the response and render messages as each chunk is received
// data is sent as newline-delimited JSON
async function onFetchResponse(response: Response): Promise<void> {
  let text = ''
  let decoder = new TextDecoder()
  if (response.ok) {
    const reader = response.body.getReader()
    while (true) {
      const {done, value} = await reader.read()
      if (done) {
        break
      }
      text += decoder.decode(value)
      addMessages(text)
      spinner.classList.remove('active')
    }
    addMessages(text)
    promptInput.disabled = false
    promptInput.focus()
  } else {
    const text = await response.text()
    console.error(`Unexpected response: ${response.status}`, {response, text})
    throw new Error(`Unexpected response: ${response.status}`)
  }
}

// The format of messages, this matches pydantic-ai both for brevity and understanding
// in production, you might not want to keep this format all the way to the frontend
interface Message {
  role: string
  content: string
  timestamp: string
}

// take raw response text and render messages into the `#conversation` element
// Message timestamp is assumed to be a unique identifier of a message, and is used to deduplicate
// hence you can send data about the same message multiple times, and it will be updated
// instead of creating a new message elements
function addMessages(responseText: string) {
  const lines = responseText.split('\n')
  const messages: Message[] = lines.filter(line => line.length > 1).map(j => JSON.parse(j))
  for (const message of messages) {
    // we use the timestamp as a crude element id
    const {timestamp, role, content} = message
    const id = `msg-${timestamp}`
    let msgDiv = document.getElementById(id)
    if (!msgDiv) {
      msgDiv = document.createElement('div')
      msgDiv.id = id
      msgDiv.title = `${role} at ${timestamp}`
      msgDiv.classList.add('border-top', 'pt-2', role)
      convElement.appendChild(msgDiv)
    }
    msgDiv.innerHTML = marked.parse(content)
  }
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

function onError(error: any) {
  console.error(error)
  document.getElementById('error').classList.remove('d-none')
  document.getElementById('spinner').classList.remove('active')
}

async function onSubmit(e: SubmitEvent): Promise<void> {
  e.preventDefault()
  spinner.classList.add('active')
  const body = new FormData(e.target as HTMLFormElement)

  promptInput.value = ''
  promptInput.disabled = true

  const response = await fetch('/chat/', {method: 'POST', body})
  await onFetchResponse(response)
}

// call onSubmit when the form is submitted (e.g. user clicks the send button or hits Enter)
document.querySelector('form').addEventListener('submit', (e) => onSubmit(e).catch(onError))

// load messages on page load
fetch('/chat/').then(onFetchResponse).catch(onError)

```

Example of a multi-agent flow where one agent delegates work to another, then hands off control to a third agent.

Demonstrates:

- [agent delegation](../../multi-agent-applications/#agent-delegation)
- [programmatic agent hand-off](../../multi-agent-applications/#programmatic-agent-hand-off)
- [usage limits](../../agents/#usage-limits)

In this scenario, a group of agents work together to find the best flight for a user.

The control flow for this example can be summarised as follows:

```
graph TD
  START --> search_agent("search agent")
  search_agent --> extraction_agent("extraction agent")
  extraction_agent --> search_agent
  search_agent --> human_confirm("human confirm")
  human_confirm --> search_agent
  search_agent --> FAILED
  human_confirm --> find_seat_function("find seat function")
  find_seat_function --> human_seat_choice("human seat choice")
  human_seat_choice --> find_seat_agent("find seat agent")
  find_seat_agent --> find_seat_function
  find_seat_function --> buy_flights("buy flights")
  buy_flights --> SUCCESS
```

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.flight_booking

```

```bash
uv run -m pydantic_ai_examples.flight_booking

```

## Example Code

flight_booking.py

```python
import datetime
from dataclasses import dataclass
from typing import Literal

import logfire
from pydantic import BaseModel, Field
from rich.prompt import Prompt

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.usage import Usage, UsageLimits

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()


class FlightDetails(BaseModel):
    """Details of the most suitable flight."""

    flight_number: str
    price: int
    origin: str = Field(description='Three-letter airport code')
    destination: str = Field(description='Three-letter airport code')
    date: datetime.date


class NoFlightFound(BaseModel):
    """When no valid flight is found."""


@dataclass
class Deps:
    web_page_text: str
    req_origin: str
    req_destination: str
    req_date: datetime.date


# This agent is responsible for controlling the flow of the conversation.
search_agent = Agent[Deps, FlightDetails | NoFlightFound](
    'openai:gpt-4o',
    output_type=FlightDetails | NoFlightFound,  # type: ignore
    retries=4,
    system_prompt=(
        'Your job is to find the cheapest flight for the user on the given date. '
    ),
)


# This agent is responsible for extracting flight details from web page text.
extraction_agent = Agent(
    'openai:gpt-4o',
    output_type=list[FlightDetails],
    system_prompt='Extract all the flight details from the given text.',
)


@search_agent.tool
async def extract_flights(ctx: RunContext[Deps]) -> list[FlightDetails]:
    """Get details of all flights."""
    # we pass the usage to the search agent so requests within this agent are counted
    result = await extraction_agent.run(ctx.deps.web_page_text, usage=ctx.usage)
    logfire.info('found {flight_count} flights', flight_count=len(result.output))
    return result.output


@search_agent.output_validator
async def validate_output(
    ctx: RunContext[Deps], output: FlightDetails | NoFlightFound
) -> FlightDetails | NoFlightFound:
    """Procedural validation that the flight meets the constraints."""
    if isinstance(output, NoFlightFound):
        return output

    errors: list[str] = []
    if output.origin != ctx.deps.req_origin:
        errors.append(
            f'Flight should have origin {ctx.deps.req_origin}, not {output.origin}'
        )
    if output.destination != ctx.deps.req_destination:
        errors.append(
            f'Flight should have destination {ctx.deps.req_destination}, not {output.destination}'
        )
    if output.date != ctx.deps.req_date:
        errors.append(f'Flight should be on {ctx.deps.req_date}, not {output.date}')

    if errors:
        raise ModelRetry('\n'.join(errors))
    else:
        return output


class SeatPreference(BaseModel):
    row: int = Field(ge=1, le=30)
    seat: Literal['A', 'B', 'C', 'D', 'E', 'F']


class Failed(BaseModel):
    """Unable to extract a seat selection."""


# This agent is responsible for extracting the user's seat selection
seat_preference_agent = Agent[None, SeatPreference | Failed](
    'openai:gpt-4o',
    output_type=SeatPreference | Failed,  # type: ignore
    system_prompt=(
        "Extract the user's seat preference. "
        'Seats A and F are window seats. '
        'Row 1 is the front row and has extra leg room. '
        'Rows 14, and 20 also have extra leg room. '
    ),
)


# in reality this would be downloaded from a booking site,
# potentially using another agent to navigate the site
flights_web_page = """
1. Flight SFO-AK123
- Price: $350
- Origin: San Francisco International Airport (SFO)
- Destination: Ted Stevens Anchorage International Airport (ANC)
- Date: January 10, 2025

2. Flight SFO-AK456
- Price: $370
- Origin: San Francisco International Airport (SFO)
- Destination: Fairbanks International Airport (FAI)
- Date: January 10, 2025

3. Flight SFO-AK789
- Price: $400
- Origin: San Francisco International Airport (SFO)
- Destination: Juneau International Airport (JNU)
- Date: January 20, 2025

4. Flight NYC-LA101
- Price: $250
- Origin: San Francisco International Airport (SFO)
- Destination: Ted Stevens Anchorage International Airport (ANC)
- Date: January 10, 2025

5. Flight CHI-MIA202
- Price: $200
- Origin: Chicago O'Hare International Airport (ORD)
- Destination: Miami International Airport (MIA)
- Date: January 12, 2025

6. Flight BOS-SEA303
- Price: $120
- Origin: Boston Logan International Airport (BOS)
- Destination: Ted Stevens Anchorage International Airport (ANC)
- Date: January 12, 2025

7. Flight DFW-DEN404
- Price: $150
- Origin: Dallas/Fort Worth International Airport (DFW)
- Destination: Denver International Airport (DEN)
- Date: January 10, 2025

8. Flight ATL-HOU505
- Price: $180
- Origin: Hartsfield-Jackson Atlanta International Airport (ATL)
- Destination: George Bush Intercontinental Airport (IAH)
- Date: January 10, 2025
"""

# restrict how many requests this app can make to the LLM
usage_limits = UsageLimits(request_limit=15)


async def main():
    deps = Deps(
        web_page_text=flights_web_page,
        req_origin='SFO',
        req_destination='ANC',
        req_date=datetime.date(2025, 1, 10),
    )
    message_history: list[ModelMessage] | None = None
    usage: Usage = Usage()
    # run the agent until a satisfactory flight is found
    while True:
        result = await search_agent.run(
            f'Find me a flight from {deps.req_origin} to {deps.req_destination} on {deps.req_date}',
            deps=deps,
            usage=usage,
            message_history=message_history,
            usage_limits=usage_limits,
        )
        if isinstance(result.output, NoFlightFound):
            print('No flight found')
            break
        else:
            flight = result.output
            print(f'Flight found: {flight}')
            answer = Prompt.ask(
                'Do you want to buy this flight, or keep searching? (buy/*search)',
                choices=['buy', 'search', ''],
                show_choices=False,
            )
            if answer == 'buy':
                seat = await find_seat(usage)
                await buy_tickets(flight, seat)
                break
            else:
                message_history = result.all_messages(
                    output_tool_return_content='Please suggest another flight'
                )


async def find_seat(usage: Usage) -> SeatPreference:
    message_history: list[ModelMessage] | None = None
    while True:
        answer = Prompt.ask('What seat would you like?')

        result = await seat_preference_agent.run(
            answer,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.output, SeatPreference):
            return result.output
        else:
            print('Could not understand seat preference. Please try again.')
            message_history = result.all_messages()


async def buy_tickets(flight_details: FlightDetails, seat: SeatPreference):
    print(f'Purchasing flight {flight_details=!r} {seat=!r}...')


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())

```

# Pydantic Model

Simple example of using PydanticAI to construct a Pydantic model from a text input.

Demonstrates:

- [structured `output_type`](../../output/#structured-output)

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.pydantic_model

```

```bash
uv run -m pydantic_ai_examples.pydantic_model

```

This examples uses `openai:gpt-4o` by default, but it works well with other models, e.g. you can run it with Gemini using:

```bash
PYDANTIC_AI_MODEL=gemini-1.5-pro python -m pydantic_ai_examples.pydantic_model

```

```bash
PYDANTIC_AI_MODEL=gemini-1.5-pro uv run -m pydantic_ai_examples.pydantic_model

```

(or `PYDANTIC_AI_MODEL=gemini-1.5-flash ...`)

## Example Code

pydantic_model.py

```python
import os

import logfire
from pydantic import BaseModel

from pydantic_ai import Agent

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()


class MyModel(BaseModel):
    city: str
    country: str


model = os.getenv('PYDANTIC_AI_MODEL', 'openai:gpt-4o')
print(f'Using model: {model}')
agent = Agent(model, output_type=MyModel)

if __name__ == '__main__':
    result = agent.run_sync('The windy city in the US of A.')
    print(result.output)
    print(result.usage())

```

# Question Graph

Example of a graph for asking and evaluating questions.

Demonstrates:

- [`pydantic_graph`](../../graph/)

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.question_graph

```

```bash
uv run -m pydantic_ai_examples.question_graph

```

## Example Code

question_graph.py

```python
from __future__ import annotations as _annotations

from dataclasses import dataclass, field
from pathlib import Path

import logfire
from groq import BaseModel
from pydantic_graph import (
    BaseNode,
    End,
    Graph,
    GraphRunContext,
)
from pydantic_graph.persistence.file import FileStatePersistence

from pydantic_ai import Agent, format_as_xml
from pydantic_ai.messages import ModelMessage

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()

ask_agent = Agent('openai:gpt-4o', output_type=str)


@dataclass
class QuestionState:
    question: str | None = None
    ask_agent_messages: list[ModelMessage] = field(default_factory=list)
    evaluate_agent_messages: list[ModelMessage] = field(default_factory=list)


@dataclass
class Ask(BaseNode[QuestionState]):
    async def run(self, ctx: GraphRunContext[QuestionState]) -> Answer:
        result = await ask_agent.run(
            'Ask a simple question with a single correct answer.',
            message_history=ctx.state.ask_agent_messages,
        )
        ctx.state.ask_agent_messages += result.all_messages()
        ctx.state.question = result.output
        return Answer(result.output)


@dataclass
class Answer(BaseNode[QuestionState]):
    question: str

    async def run(self, ctx: GraphRunContext[QuestionState]) -> Evaluate:
        answer = input(f'{self.question}: ')
        return Evaluate(answer)


class EvaluationOutput(BaseModel, use_attribute_docstrings=True):
    correct: bool
    """Whether the answer is correct."""
    comment: str
    """Comment on the answer, reprimand the user if the answer is wrong."""


evaluate_agent = Agent(
    'openai:gpt-4o',
    output_type=EvaluationOutput,
    system_prompt='Given a question and answer, evaluate if the answer is correct.',
)


@dataclass
class Evaluate(BaseNode[QuestionState, None, str]):
    answer: str

    async def run(
        self,
        ctx: GraphRunContext[QuestionState],
    ) -> End[str] | Reprimand:
        assert ctx.state.question is not None
        result = await evaluate_agent.run(
            format_as_xml({'question': ctx.state.question, 'answer': self.answer}),
            message_history=ctx.state.evaluate_agent_messages,
        )
        ctx.state.evaluate_agent_messages += result.all_messages()
        if result.output.correct:
            return End(result.output.comment)
        else:
            return Reprimand(result.output.comment)


@dataclass
class Reprimand(BaseNode[QuestionState]):
    comment: str

    async def run(self, ctx: GraphRunContext[QuestionState]) -> Ask:
        print(f'Comment: {self.comment}')
        ctx.state.question = None
        return Ask()


question_graph = Graph(
    nodes=(Ask, Answer, Evaluate, Reprimand), state_type=QuestionState
)


async def run_as_continuous():
    state = QuestionState()
    node = Ask()
    end = await question_graph.run(node, state=state)
    print('END:', end.output)


async def run_as_cli(answer: str | None):
    persistence = FileStatePersistence(Path('question_graph.json'))
    persistence.set_graph_types(question_graph)

    if snapshot := await persistence.load_next():
        state = snapshot.state
        assert answer is not None, (
            'answer required, usage "uv run -m pydantic_ai_examples.question_graph cli <answer>"'
        )
        node = Evaluate(answer)
    else:
        state = QuestionState()
        node = Ask()
    # debug(state, node)

    async with question_graph.iter(node, state=state, persistence=persistence) as run:
        while True:
            node = await run.next()
            if isinstance(node, End):
                print('END:', node.data)
                history = await persistence.load_all()
                print('history:', '\n'.join(str(e.node) for e in history), sep='\n')
                print('Finished!')
                break
            elif isinstance(node, Answer):
                print(node.question)
                break
            # otherwise just continue


if __name__ == '__main__':
    import asyncio
    import sys

    try:
        sub_command = sys.argv[1]
        assert sub_command in ('continuous', 'cli', 'mermaid')
    except (IndexError, AssertionError):
        print(
            'Usage:\n'
            '  uv run -m pydantic_ai_examples.question_graph mermaid\n'
            'or:\n'
            '  uv run -m pydantic_ai_examples.question_graph continuous\n'
            'or:\n'
            '  uv run -m pydantic_ai_examples.question_graph cli [answer]',
            file=sys.stderr,
        )
        sys.exit(1)

    if sub_command == 'mermaid':
        print(question_graph.mermaid_code(start_node=Ask))
    elif sub_command == 'continuous':
        asyncio.run(run_as_continuous())
    else:
        a = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(run_as_cli(a))

```

The mermaid diagram generated in this example looks like this:

```
---
title: question_graph
---
stateDiagram-v2
  [*] --> Ask
  Ask --> Answer: ask the question
  Answer --> Evaluate: answer the question
  Evaluate --> Congratulate
  Evaluate --> Castigate
  Congratulate --> [*]: success
  Castigate --> Ask: try again
```

# RAG

RAG search example. This demo allows you to ask question of the [logfire](https://pydantic.dev/logfire) documentation.

Demonstrates:

- [tools](../../tools/)
- [agent dependencies](../../dependencies/)
- RAG search

This is done by creating a database containing each section of the markdown documentation, then registering the search tool with the PydanticAI agent.

Logic for extracting sections from markdown files and a JSON file with that data is available in [this gist](https://gist.github.com/samuelcolvin/4b5bb9bb163b1122ff17e29e48c10992).

[PostgreSQL with pgvector](https://github.com/pgvector/pgvector) is used as the search database, the easiest way to download and run pgvector is using Docker:

```bash
mkdir postgres-data
docker run --rm \
  -e POSTGRES_PASSWORD=postgres \
  -p 54320:5432 \
  -v `pwd`/postgres-data:/var/lib/postgresql/data \
  pgvector/pgvector:pg17

```

As with the [SQL gen](../sql-gen/) example, we run postgres on port `54320` to avoid conflicts with any other postgres instances you may have running. We also mount the PostgreSQL `data` directory locally to persist the data if you need to stop and restart the container.

With that running and [dependencies installed and environment variables set](../#usage), we can build the search database with (**WARNING**: this requires the `OPENAI_API_KEY` env variable and will calling the OpenAI embedding API around 300 times to generate embeddings for each section of the documentation):

```bash
python -m pydantic_ai_examples.rag build

```

```bash
uv run -m pydantic_ai_examples.rag build

```

(Note building the database doesn't use PydanticAI right now, instead it uses the OpenAI SDK directly.)

You can then ask the agent a question with:

```bash
python -m pydantic_ai_examples.rag search "How do I configure logfire to work with FastAPI?"

```

```bash
uv run -m pydantic_ai_examples.rag search "How do I configure logfire to work with FastAPI?"

```

## Example Code

rag.py

```python
from __future__ import annotations as _annotations

import asyncio
import re
import sys
import unicodedata
from contextlib import asynccontextmanager
from dataclasses import dataclass

import asyncpg
import httpx
import logfire
import pydantic_core
from openai import AsyncOpenAI
from pydantic import TypeAdapter
from typing_extensions import AsyncGenerator

from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_asyncpg()
logfire.instrument_pydantic_ai()


@dataclass
class Deps:
    openai: AsyncOpenAI
    pool: asyncpg.Pool


agent = Agent('openai:gpt-4o', deps_type=Deps)


@agent.tool
async def retrieve(context: RunContext[Deps], search_query: str) -> str:
    """Retrieve documentation sections based on a search query.

    Args:
        context: The call context.
        search_query: The search query.
    """
    with logfire.span(
        'create embedding for {search_query=}', search_query=search_query
    ):
        embedding = await context.deps.openai.embeddings.create(
            input=search_query,
            model='text-embedding-3-small',
        )

    assert len(embedding.data) == 1, (
        f'Expected 1 embedding, got {len(embedding.data)}, doc query: {search_query!r}'
    )
    embedding = embedding.data[0].embedding
    embedding_json = pydantic_core.to_json(embedding).decode()
    rows = await context.deps.pool.fetch(
        'SELECT url, title, content FROM doc_sections ORDER BY embedding <-> $1 LIMIT 8',
        embedding_json,
    )
    return '\n\n'.join(
        f'# {row["title"]}\nDocumentation URL:{row["url"]}\n\n{row["content"]}\n'
        for row in rows
    )


async def run_agent(question: str):
    """Entry point to run the agent and perform RAG based question answering."""
    openai = AsyncOpenAI()
    logfire.instrument_openai(openai)

    logfire.info('Asking "{question}"', question=question)

    async with database_connect(False) as pool:
        deps = Deps(openai=openai, pool=pool)
        answer = await agent.run(question, deps=deps)
    print(answer.output)


#######################################################
# The rest of this file is dedicated to preparing the #
# search database, and some utilities.                #
#######################################################

# JSON document from
# https://gist.github.com/samuelcolvin/4b5bb9bb163b1122ff17e29e48c10992
DOCS_JSON = (
    'https://gist.githubusercontent.com/'
    'samuelcolvin/4b5bb9bb163b1122ff17e29e48c10992/raw/'
    '80c5925c42f1442c24963aaf5eb1a324d47afe95/logfire_docs.json'
)


async def build_search_db():
    """Build the search database."""
    async with httpx.AsyncClient() as client:
        response = await client.get(DOCS_JSON)
        response.raise_for_status()
    sections = sessions_ta.validate_json(response.content)

    openai = AsyncOpenAI()
    logfire.instrument_openai(openai)

    async with database_connect(True) as pool:
        with logfire.span('create schema'):
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(DB_SCHEMA)

        sem = asyncio.Semaphore(10)
        async with asyncio.TaskGroup() as tg:
            for section in sections:
                tg.create_task(insert_doc_section(sem, openai, pool, section))


async def insert_doc_section(
    sem: asyncio.Semaphore,
    openai: AsyncOpenAI,
    pool: asyncpg.Pool,
    section: DocsSection,
) -> None:
    async with sem:
        url = section.url()
        exists = await pool.fetchval('SELECT 1 FROM doc_sections WHERE url = $1', url)
        if exists:
            logfire.info('Skipping {url=}', url=url)
            return

        with logfire.span('create embedding for {url=}', url=url):
            embedding = await openai.embeddings.create(
                input=section.embedding_content(),
                model='text-embedding-3-small',
            )
        assert len(embedding.data) == 1, (
            f'Expected 1 embedding, got {len(embedding.data)}, doc section: {section}'
        )
        embedding = embedding.data[0].embedding
        embedding_json = pydantic_core.to_json(embedding).decode()
        await pool.execute(
            'INSERT INTO doc_sections (url, title, content, embedding) VALUES ($1, $2, $3, $4)',
            url,
            section.title,
            section.content,
            embedding_json,
        )


@dataclass
class DocsSection:
    id: int
    parent: int | None
    path: str
    level: int
    title: str
    content: str

    def url(self) -> str:
        url_path = re.sub(r'\.md$', '', self.path)
        return (
            f'https://logfire.pydantic.dev/docs/{url_path}/#{slugify(self.title, "-")}'
        )

    def embedding_content(self) -> str:
        return '\n\n'.join((f'path: {self.path}', f'title: {self.title}', self.content))


sessions_ta = TypeAdapter(list[DocsSection])


# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
@asynccontextmanager
async def database_connect(
    create_db: bool = False,
) -> AsyncGenerator[asyncpg.Pool, None]:
    server_dsn, database = (
        'postgresql://postgres:postgres@localhost:54320',
        'pydantic_ai_rag',
    )
    if create_db:
        with logfire.span('check and create DB'):
            conn = await asyncpg.connect(server_dsn)
            try:
                db_exists = await conn.fetchval(
                    'SELECT 1 FROM pg_database WHERE datname = $1', database
                )
                if not db_exists:
                    await conn.execute(f'CREATE DATABASE {database}')
            finally:
                await conn.close()

    pool = await asyncpg.create_pool(f'{server_dsn}/{database}')
    try:
        yield pool
    finally:
        await pool.close()


DB_SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS doc_sections (
    id serial PRIMARY KEY,
    url text NOT NULL UNIQUE,
    title text NOT NULL,
    content text NOT NULL,
    -- text-embedding-3-small returns a vector of 1536 floats
    embedding vector(1536) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_doc_sections_embedding ON doc_sections USING hnsw (embedding vector_l2_ops);
"""


def slugify(value: str, separator: str, unicode: bool = False) -> str:
    """Slugify a string, to make it URL friendly."""
    # Taken unchanged from https://github.com/Python-Markdown/markdown/blob/3.7/markdown/extensions/toc.py#L38
    if not unicode:
        # Replace Extended Latin characters with ASCII, i.e. `Å¾lutÃ½` => `zluty`
        value = unicodedata.normalize('NFKD', value)
        value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(rf'[{separator}\s]+', separator, value)


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else None
    if action == 'build':
        asyncio.run(build_search_db())
    elif action == 'search':
        if len(sys.argv) == 3:
            q = sys.argv[2]
        else:
            q = 'How do I configure logfire to work with FastAPI?'
        asyncio.run(run_agent(q))
    else:
        print(
            'uv run --extra examples -m pydantic_ai_examples.rag build|search',
            file=sys.stderr,
        )
        sys.exit(1)

```

# SQL Generation

Example demonstrating how to use PydanticAI to generate SQL queries based on user input.

Demonstrates:

- [dynamic system prompt](../../agents/#system-prompts)
- [structured `output_type`](../../output/#structured-output)
- [output validation](../../output/#output-validator-functions)
- [agent dependencies](../../dependencies/)

## Running the Example

The resulting SQL is validated by running it as an `EXPLAIN` query on PostgreSQL. To run the example, you first need to run PostgreSQL, e.g. via Docker:

```bash
docker run --rm -e POSTGRES_PASSWORD=postgres -p 54320:5432 postgres

```

*(we run postgres on port `54320` to avoid conflicts with any other postgres instances you may have running)*

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.sql_gen

```

```bash
uv run -m pydantic_ai_examples.sql_gen

```

or to use a custom prompt:

```bash
python -m pydantic_ai_examples.sql_gen "find me errors"

```

```bash
uv run -m pydantic_ai_examples.sql_gen "find me errors"

```

This model uses `gemini-1.5-flash` by default since Gemini is good at single shot queries of this kind.

## Example Code

sql_gen.py

```python
import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Union

import asyncpg
import logfire
from annotated_types import MinLen
from devtools import debug
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

from pydantic_ai import Agent, ModelRetry, RunContext, format_as_xml

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_asyncpg()
logfire.instrument_pydantic_ai()

DB_SCHEMA = """
CREATE TABLE records (
    created_at timestamptz,
    start_timestamp timestamptz,
    end_timestamp timestamptz,
    trace_id text,
    span_id text,
    parent_span_id text,
    level log_level,
    span_name text,
    message text,
    attributes_json_schema text,
    attributes jsonb,
    tags text[],
    is_exception boolean,
    otel_status_message text,
    service_name text
);
"""
SQL_EXAMPLES = [
    {
        'request': 'show me records where foobar is false',
        'response': "SELECT * FROM records WHERE attributes->>'foobar' = false",
    },
    {
        'request': 'show me records where attributes include the key "foobar"',
        'response': "SELECT * FROM records WHERE attributes ? 'foobar'",
    },
    {
        'request': 'show me records from yesterday',
        'response': "SELECT * FROM records WHERE start_timestamp::date > CURRENT_TIMESTAMP - INTERVAL '1 day'",
    },
    {
        'request': 'show me error records with the tag "foobar"',
        'response': "SELECT * FROM records WHERE level = 'error' and 'foobar' = ANY(tags)",
    },
]


@dataclass
class Deps:
    conn: asyncpg.Connection


class Success(BaseModel):
    """Response when SQL could be successfully generated."""

    sql_query: Annotated[str, MinLen(1)]
    explanation: str = Field(
        '', description='Explanation of the SQL query, as markdown'
    )


class InvalidRequest(BaseModel):
    """Response the user input didn't include enough information to generate SQL."""

    error_message: str


Response: TypeAlias = Union[Success, InvalidRequest]
agent: Agent[Deps, Response] = Agent(
    'google-gla:gemini-1.5-flash',
    # Type ignore while we wait for PEP-0747, nonetheless unions will work fine everywhere else
    output_type=Response,  # type: ignore
    deps_type=Deps,
)


@agent.system_prompt
async def system_prompt() -> str:
    return f"""\
Given the following PostgreSQL table of records, your job is to
write a SQL query that suits the user's request.

Database schema:

{DB_SCHEMA}

today's date = {date.today()}

{format_as_xml(SQL_EXAMPLES)}
"""


@agent.output_validator
async def validate_output(ctx: RunContext[Deps], output: Response) -> Response:
    if isinstance(output, InvalidRequest):
        return output

    # gemini often adds extraneous backslashes to SQL
    output.sql_query = output.sql_query.replace('\\', '')
    if not output.sql_query.upper().startswith('SELECT'):
        raise ModelRetry('Please create a SELECT query')

    try:
        await ctx.deps.conn.execute(f'EXPLAIN {output.sql_query}')
    except asyncpg.exceptions.PostgresError as e:
        raise ModelRetry(f'Invalid query: {e}') from e
    else:
        return output


async def main():
    if len(sys.argv) == 1:
        prompt = 'show me logs from yesterday, with level "error"'
    else:
        prompt = sys.argv[1]

    async with database_connect(
        'postgresql://postgres:postgres@localhost:54320', 'pydantic_ai_sql_gen'
    ) as conn:
        deps = Deps(conn)
        result = await agent.run(prompt, deps=deps)
    debug(result.output)


# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
@asynccontextmanager
async def database_connect(server_dsn: str, database: str) -> AsyncGenerator[Any, None]:
    with logfire.span('check and create DB'):
        conn = await asyncpg.connect(server_dsn)
        try:
            db_exists = await conn.fetchval(
                'SELECT 1 FROM pg_database WHERE datname = $1', database
            )
            if not db_exists:
                await conn.execute(f'CREATE DATABASE {database}')
        finally:
            await conn.close()

    conn = await asyncpg.connect(f'{server_dsn}/{database}')
    try:
        with logfire.span('create schema'):
            async with conn.transaction():
                if not db_exists:
                    await conn.execute(
                        "CREATE TYPE log_level AS ENUM ('debug', 'info', 'warning', 'error', 'critical')"
                    )
                    await conn.execute(DB_SCHEMA)
        yield conn
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())

```

This example shows how to stream markdown from an agent, using the [`rich`](https://github.com/Textualize/rich) library to highlight the output in the terminal.

It'll run the example with both OpenAI and Google Gemini models if the required environment variables are set.

Demonstrates:

- [streaming text responses](../../output/#streaming-text)

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.stream_markdown

```

```bash
uv run -m pydantic_ai_examples.stream_markdown

```

## Example Code

```python
import asyncio
import os

import logfire
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.markdown import CodeBlock, Markdown
from rich.syntax import Syntax
from rich.text import Text

from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()

agent = Agent()

# models to try, and the appropriate env var
models: list[tuple[KnownModelName, str]] = [
    ('google-gla:gemini-1.5-flash', 'GEMINI_API_KEY'),
    ('openai:gpt-4o-mini', 'OPENAI_API_KEY'),
    ('groq:llama-3.3-70b-versatile', 'GROQ_API_KEY'),
]


async def main():
    prettier_code_blocks()
    console = Console()
    prompt = 'Show me a short example of using Pydantic.'
    console.log(f'Asking: {prompt}...', style='cyan')
    for model, env_var in models:
        if env_var in os.environ:
            console.log(f'Using model: {model}')
            with Live('', console=console, vertical_overflow='visible') as live:
                async with agent.run_stream(prompt, model=model) as result:
                    async for message in result.stream():
                        live.update(Markdown(message))
            console.log(result.usage())
        else:
            console.log(f'{model} requires {env_var} to be set.')


def prettier_code_blocks():
    """Make rich code blocks prettier and easier to copy.

    From https://github.com/samuelcolvin/aicli/blob/v0.8.0/samuelcolvin_aicli.py#L22
    """

    class SimpleCodeBlock(CodeBlock):
        def __rich_console__(
            self, console: Console, options: ConsoleOptions
        ) -> RenderResult:
            code = str(self.text).rstrip()
            yield Text(self.lexer_name, style='dim')
            yield Syntax(
                code,
                self.lexer_name,
                theme=self.theme,
                background_color='default',
                word_wrap=True,
            )
            yield Text(f'/{self.lexer_name}', style='dim')

    Markdown.elements['fence'] = SimpleCodeBlock


if __name__ == '__main__':
    asyncio.run(main())

```

Information about whales â€” an example of streamed structured response validation.

Demonstrates:

- [streaming structured output](../../output/#streaming-structured-output)

This script streams structured responses from GPT-4 about whales, validates the data and displays it as a dynamic table using [`rich`](https://github.com/Textualize/rich) as the data is received.

## Running the Example

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.stream_whales

```

```bash
uv run -m pydantic_ai_examples.stream_whales

```

Should give an output like this:

## Example Code

stream_whales.py

```python
from typing import Annotated

import logfire
from pydantic import Field, ValidationError
from rich.console import Console
from rich.live import Live
from rich.table import Table
from typing_extensions import NotRequired, TypedDict

from pydantic_ai import Agent

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()


class Whale(TypedDict):
    name: str
    length: Annotated[
        float, Field(description='Average length of an adult whale in meters.')
    ]
    weight: NotRequired[
        Annotated[
            float,
            Field(description='Average weight of an adult whale in kilograms.', ge=50),
        ]
    ]
    ocean: NotRequired[str]
    description: NotRequired[Annotated[str, Field(description='Short Description')]]


agent = Agent('openai:gpt-4', output_type=list[Whale])


async def main():
    console = Console()
    with Live('\n' * 36, console=console) as live:
        console.print('Requesting data...', style='cyan')
        async with agent.run_stream(
            'Generate me details of 5 species of Whale.'
        ) as result:
            console.print('Response:', style='green')

            async for message, last in result.stream_structured(debounce_by=0.01):
                try:
                    whales = await result.validate_structured_output(
                        message, allow_partial=not last
                    )
                except ValidationError as exc:
                    if all(
                        e['type'] == 'missing' and e['loc'] == ('response',)
                        for e in exc.errors()
                    ):
                        continue
                    else:
                        raise

                table = Table(
                    title='Species of Whale',
                    caption='Streaming Structured responses from GPT-4',
                    width=120,
                )
                table.add_column('ID', justify='right')
                table.add_column('Name')
                table.add_column('Avg. Length (m)', justify='right')
                table.add_column('Avg. Weight (kg)', justify='right')
                table.add_column('Ocean')
                table.add_column('Description', justify='right')

                for wid, whale in enumerate(whales, start=1):
                    table.add_row(
                        str(wid),
                        whale['name'],
                        f'{whale["length"]:0.0f}',
                        f'{w:0.0f}' if (w := whale.get('weight')) else 'â€¦',
                        whale.get('ocean') or 'â€¦',
                        whale.get('description') or 'â€¦',
                    )
                live.update(table)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())

```

Example of PydanticAI with multiple tools which the LLM needs to call in turn to answer a question.

Demonstrates:

- [tools](../../tools/)
- [agent dependencies](../../dependencies/)
- [streaming text responses](../../output/#streaming-text)
- Building a [Gradio](https://www.gradio.app/) UI for the agent

In this case the idea is a "weather" agent â€” the user can ask for the weather in multiple locations, the agent will use the `get_lat_lng` tool to get the latitude and longitude of the locations, then use the `get_weather` tool to get the weather for those locations.

## Running the Example

To run this example properly, you might want to add two extra API keys **(Note if either key is missing, the code will fall back to dummy data, so they're not required)**:

- A weather API key from [tomorrow.io](https://www.tomorrow.io/weather-api/) set via `WEATHER_API_KEY`
- A geocoding API key from [geocode.maps.co](https://geocode.maps.co/) set via `GEO_API_KEY`

With [dependencies installed and environment variables set](../#usage), run:

```bash
python -m pydantic_ai_examples.weather_agent

```

```bash
uv run -m pydantic_ai_examples.weather_agent

```

## Example Code

pydantic_ai_examples/weather_agent.py

```python
from __future__ import annotations as _annotations

import asyncio
import os
import urllib.parse
from dataclasses import dataclass
from typing import Any

import logfire
from devtools import debug
from httpx import AsyncClient

from pydantic_ai import Agent, ModelRetry, RunContext

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_pydantic_ai()


@dataclass
class Deps:
    client: AsyncClient
    weather_api_key: str | None
    geo_api_key: str | None


weather_agent = Agent(
    'openai:gpt-4o',
    # 'Be concise, reply with one sentence.' is enough for some models (like openai) to use
    # the below tools appropriately, but others like anthropic and gemini require a bit more direction.
    instructions=(
        'Be concise, reply with one sentence.'
        'Use the `get_lat_lng` tool to get the latitude and longitude of the locations, '
        'then use the `get_weather` tool to get the weather.'
    ),
    deps_type=Deps,
    retries=2,
)


@weather_agent.tool
async def get_lat_lng(
    ctx: RunContext[Deps], location_description: str
) -> dict[str, float]:
    """Get the latitude and longitude of a location.

    Args:
        ctx: The context.
        location_description: A description of a location.
    """
    if ctx.deps.geo_api_key is None:
        # if no API key is provided, return a dummy response (London)
        return {'lat': 51.1, 'lng': -0.1}

    params = {'access_token': ctx.deps.geo_api_key}
    loc = urllib.parse.quote(location_description)
    r = await ctx.deps.client.get(
        f'https://api.mapbox.com/geocoding/v5/mapbox.places/{loc}.json', params=params
    )
    r.raise_for_status()
    data = r.json()

    if features := data['features']:
        lat, lng = features[0]['center']
        return {'lat': lat, 'lng': lng}
    else:
        raise ModelRetry('Could not find the location')


@weather_agent.tool
async def get_weather(ctx: RunContext[Deps], lat: float, lng: float) -> dict[str, Any]:
    """Get the weather at a location.

    Args:
        ctx: The context.
        lat: Latitude of the location.
        lng: Longitude of the location.
    """
    if ctx.deps.weather_api_key is None:
        # if no API key is provided, return a dummy response
        return {'temperature': '21 Â°C', 'description': 'Sunny'}

    params = {
        'apikey': ctx.deps.weather_api_key,
        'location': f'{lat},{lng}',
        'units': 'metric',
    }
    with logfire.span('calling weather API', params=params) as span:
        r = await ctx.deps.client.get(
            'https://api.tomorrow.io/v4/weather/realtime', params=params
        )
        r.raise_for_status()
        data = r.json()
        span.set_attribute('response', data)

    values = data['data']['values']
    # https://docs.tomorrow.io/reference/data-layers-weather-codes
    code_lookup = {
        1000: 'Clear, Sunny',
        1100: 'Mostly Clear',
        1101: 'Partly Cloudy',
        1102: 'Mostly Cloudy',
        1001: 'Cloudy',
        2000: 'Fog',
        2100: 'Light Fog',
        4000: 'Drizzle',
        4001: 'Rain',
        4200: 'Light Rain',
        4201: 'Heavy Rain',
        5000: 'Snow',
        5001: 'Flurries',
        5100: 'Light Snow',
        5101: 'Heavy Snow',
        6000: 'Freezing Drizzle',
        6001: 'Freezing Rain',
        6200: 'Light Freezing Rain',
        6201: 'Heavy Freezing Rain',
        7000: 'Ice Pellets',
        7101: 'Heavy Ice Pellets',
        7102: 'Light Ice Pellets',
        8000: 'Thunderstorm',
    }
    return {
        'temperature': f'{values["temperatureApparent"]:0.0f}Â°C',
        'description': code_lookup.get(values['weatherCode'], 'Unknown'),
    }


async def main():
    async with AsyncClient() as client:
        logfire.instrument_httpx(client, capture_all=True)
        # create a free API key at https://www.tomorrow.io/weather-api/
        weather_api_key = os.getenv('WEATHER_API_KEY')
        # create a free API key at https://www.mapbox.com/
        geo_api_key = os.getenv('GEO_API_KEY')
        deps = Deps(
            client=client, weather_api_key=weather_api_key, geo_api_key=geo_api_key
        )
        result = await weather_agent.run(
            'What is the weather like in London and in Wiltshire?', deps=deps
        )
        debug(result)
        print('Response:', result.output)


if __name__ == '__main__':
    asyncio.run(main())

```

## Running the UI

You can build multi-turn chat applications for your agent with [Gradio](https://www.gradio.app/), a framework for building AI web applications entirely in python. Gradio comes with built-in chat components and agent support so the entire UI will be implemented in a single python file!

Here's what the UI looks like for the weather agent:

Note, to run the UI, you'll need Python 3.10+.

```bash
pip install gradio>=5.9.0
python/uv-run -m pydantic_ai_examples.weather_agent_gradio

```

## UI Code

pydantic_ai_examples/weather_agent_gradio.py

```python
from __future__ import annotations as _annotations

import json
import os

from httpx import AsyncClient

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai_examples.weather_agent import Deps, weather_agent

try:
    import gradio as gr
except ImportError as e:
    raise ImportError(
        'Please install gradio with `pip install gradio`. You must use python>=3.10.'
    ) from e

TOOL_TO_DISPLAY_NAME = {'get_lat_lng': 'Geocoding API', 'get_weather': 'Weather API'}

client = AsyncClient()
weather_api_key = os.getenv('WEATHER_API_KEY')
# create a free API key at https://geocode.maps.co/
geo_api_key = os.getenv('GEO_API_KEY')
deps = Deps(client=client, weather_api_key=weather_api_key, geo_api_key=geo_api_key)


async def stream_from_agent(prompt: str, chatbot: list[dict], past_messages: list):
    chatbot.append({'role': 'user', 'content': prompt})
    yield gr.Textbox(interactive=False, value=''), chatbot, gr.skip()
    async with weather_agent.run_stream(
        prompt, deps=deps, message_history=past_messages
    ) as result:
        for message in result.new_messages():
            for call in message.parts:
                if isinstance(call, ToolCallPart):
                    call_args = (
                        call.args.args_json
                        if hasattr(call.args, 'args_json')
                        else json.dumps(call.args.args_dict)
                    )
                    metadata = {
                        'title': f'ðŸ› ï¸ Using {TOOL_TO_DISPLAY_NAME[call.tool_name]}',
                    }
                    if call.tool_call_id is not None:
                        metadata['id'] = {call.tool_call_id}

                    gr_message = {
                        'role': 'assistant',
                        'content': 'Parameters: ' + call_args,
                        'metadata': metadata,
                    }
                    chatbot.append(gr_message)
                if isinstance(call, ToolReturnPart):
                    for gr_message in chatbot:
                        if (
                            gr_message.get('metadata', {}).get('id', '')
                            == call.tool_call_id
                        ):
                            gr_message['content'] += (
                                f'\nOutput: {json.dumps(call.content)}'
                            )
                yield gr.skip(), chatbot, gr.skip()
        chatbot.append({'role': 'assistant', 'content': ''})
        async for message in result.stream_text():
            chatbot[-1]['content'] = message
            yield gr.skip(), chatbot, gr.skip()
        past_messages = result.all_messages()

        yield gr.Textbox(interactive=True), gr.skip(), past_messages


async def handle_retry(chatbot, past_messages: list, retry_data: gr.RetryData):
    new_history = chatbot[: retry_data.index]
    previous_prompt = chatbot[retry_data.index]['content']
    past_messages = past_messages[: retry_data.index]
    async for update in stream_from_agent(previous_prompt, new_history, past_messages):
        yield update


def undo(chatbot, past_messages: list, undo_data: gr.UndoData):
    new_history = chatbot[: undo_data.index]
    past_messages = past_messages[: undo_data.index]
    return chatbot[undo_data.index]['content'], new_history, past_messages


def select_data(message: gr.SelectData) -> str:
    return message.value['text']


with gr.Blocks() as demo:
    gr.HTML(
        """
<div style="display: flex; justify-content: center; align-items: center; gap: 2rem; padding: 1rem; width: 100%">
    <img src="https://ai.pydantic.dev/img/logo-white.svg" style="max-width: 200px; height: auto">
    <div>
        <h1 style="margin: 0 0 1rem 0">Weather Assistant</h1>
        <h3 style="margin: 0 0 0.5rem 0">
            This assistant answer your weather questions.
        </h3>
    </div>
</div>
"""
    )
    past_messages = gr.State([])
    chatbot = gr.Chatbot(
        label='Packing Assistant',
        type='messages',
        avatar_images=(None, 'https://ai.pydantic.dev/img/logo-white.svg'),
        examples=[
            {'text': 'What is the weather like in Miami?'},
            {'text': 'What is the weather like in London?'},
        ],
    )
    with gr.Row():
        prompt = gr.Textbox(
            lines=1,
            show_label=False,
            placeholder='What is the weather like in New York City?',
        )
    generation = prompt.submit(
        stream_from_agent,
        inputs=[prompt, chatbot, past_messages],
        outputs=[prompt, chatbot, past_messages],
    )
    chatbot.example_select(select_data, None, [prompt])
    chatbot.retry(
        handle_retry, [chatbot, past_messages], [prompt, chatbot, past_messages]
    )
    chatbot.undo(undo, [chatbot, past_messages], [prompt, chatbot, past_messages])


if __name__ == '__main__':
    demo.launch()

```