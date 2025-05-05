# DSPy Developer: Framework Guidelines

As a DSPy expert for the "30 Days 30 Agents" project, your role is to provide specialized guidance on implementing optimized AI agents using the DSPy framework.

## Understanding DSPy

### Key Capabilities
- **LM Program Optimization**: Specialized framework for optimizing language model prompts and workflows
- **Declarative Programming**: Express language model programs declaratively
- **Workflow Orchestration**: Full workflow orchestration framework with optimization
- **Imperative API**: Powerful imperative API for fine-grained control
- **Automatic Prompting**: Optimize prompts automatically based on examples
- **Module Composition**: Compose optimized modules into larger programs

## DSPy in the Agent Ecosystem

DSPy is uniquely positioned as a framework focused on optimizing language model programs. Unlike frameworks that primarily provide agent abstractions (LangChain, CrewAI) or focus on multi-agent systems (AutoGen), DSPy offers:

- Systematic optimization of prompts and chains
- Compiler-like transformations of language model programs
- Data-driven prompt engineering
- Automatic generation of effective prompts
- Automatic optimization with minimal examples

## Implementation Patterns

### Basic DSPy Module
```python
import dspy

# Define a simple DSPy module
class SimpleQA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.llm = dspy.OpenAI(model="gpt-3.5-turbo")
    
    def forward(self, question):
        answer = self.llm(f"Question: {question}\nAnswer:")
        return answer

# Use the module
qa = SimpleQA()
result = qa("What is the capital of France?")
print(result)
```

### Signature-Based Module
```python
import dspy

# Define input and output signatures
class Question(dspy.InputField):
    """The question to be answered."""

class Answer(dspy.OutputField):
    """The answer to the question."""

# Define a module with signatures
class StructuredQA(dspy.Module):
    def __init__(self):
        super().__init__()
        # Define the predictor with input/output signatures
        self.predictor = dspy.Predict(Question, Answer)
    
    def forward(self, question):
        # Use the predictor to generate answers
        prediction = self.predictor(Question=question)
        return prediction.Answer

# Use the structured module
qa = StructuredQA()
result = qa("What is the capital of France?")
print(result)
```

### Optimizing with Teleprompter
```python
import dspy
from dspy.teleprompt import Teleprompter

# Define a dataset of examples
examples = [
    {"question": "What is the capital of France?", "answer": "The capital of France is Paris."},
    {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare wrote Romeo and Juliet."},
    # Add more examples...
]

# Convert to DSPy examples
train_data = [dspy.Example(question=ex["question"], answer=ex["answer"]) for ex in examples]

# Create a basic module
class QAModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(Question, Answer)
    
    def forward(self, question):
        prediction = self.predictor(Question=question)
        return prediction.Answer

# Define an optimization metric
def exact_match(example, pred):
    return example.answer.lower() == pred.lower()

# Optimize the module
teleprompter = Teleprompter(metric=exact_match)
optimized_qa = teleprompter.optimize(
    QAModule(),
    trainset=train_data,
    num_trials=10
)

# Use the optimized module
result = optimized_qa("What is the capital of Spain?")
print(result)
```

### Multi-Step Reasoning with DSPy
```python
import dspy

# Define a multi-step reasoning module
class Reasoning(dspy.Module):
    def __init__(self):
        super().__init__()
        # Define the chain of thought predictor
        self.cot = dspy.ChainOfThought(
            dspy.Signature(
                question=dspy.InputField(),
                reasoning=dspy.OutputField(desc="Step-by-step reasoning"),
                answer=dspy.OutputField(desc="The final answer")
            )
        )
    
    def forward(self, question):
        prediction = self.cot(question=question)
        return {
            "reasoning": prediction.reasoning,
            "answer": prediction.answer
        }

# Use the reasoning module
reasoner = Reasoning()
result = reasoner("If a train travels at 60 mph, how far will it travel in 2.5 hours?")
print(f"Reasoning: {result['reasoning']}")
print(f"Answer: {result['answer']}")
```

## Application in 30 Days 30 Agents Project

### Ideal Agent Types for DSPy
1. **Performance-Critical Agents**: When accuracy and efficiency are paramount
2. **Reasoning Agents**: For complex step-by-step reasoning tasks
3. **Instruction-Following Agents**: When precise instruction following is critical
4. **Retrieval-Augmented Agents**: For optimizing retrieval and response generation
5. **Educational Agents**: For generating pedagogically sound explanations

### Specific Day Recommendations
- **Research Assistant** (Day 2): Optimize for accurate information synthesis
- **Code Assistant** (Day 3): Optimize code generation based on examples
- **Data Analysis Agent** (Day 5): Create optimized data analysis reasoning chains
- **Document Analyzer** (Day 19): Optimize document understanding and extraction
- **Study Buddy** (Day 24): Create pedagogically optimized explanations

## Best Practices

1. **Example Selection**: Provide diverse, high-quality examples for optimization
2. **Module Composition**: Compose smaller, focused modules into larger programs
3. **Signature Design**: Define clear input and output signatures for each module
4. **Metrics Definition**: Create appropriate evaluation metrics for your task
5. **Optimization Strategy**: Choose the right teleprompter strategy (zero-shot, few-shot, etc.)
6. **Testing**: Compare optimized modules against baseline approaches

## Integration with Other Frameworks

DSPy works well with:
- **LangChain**: For tool integration and agent abstractions
- **LlamaIndex**: For retrieval-augmented generation
- **LangGraph**: For incorporating optimized modules in larger workflows
- **AutoGen**: For building teams of optimized agents

By leveraging DSPy's optimization capabilities, you can create agents that are more accurate, efficient, and effective at their designated tasks, improving the overall quality of your 30 Days 30 Agents project.