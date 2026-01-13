# Specification: Modular AI Provider Support

## 1. Overview
This feature refactors the existing `src/ai_assistant.py` and `src/providers.py` (or equivalent) to support a modular backend architecture for LLM inference. Currently, the system is primarily integrated with Ollama. The goal is to introduce an abstract base class for AI providers and implement concrete classes for:
1.  **Ollama** (Existing functionality preserved)
2.  **OpenAI-Compatible APIs** (New functionality to support LM Studio, AnythingLLM, vLLM, etc.)

## 2. Goals
-   Decouple `GamingAIAssistant` from specific Ollama implementation details.
-   Enable users to switch between AI providers via configuration (env vars).
-   Support any local LLM server that exposes an OpenAI-compatible `/v1/chat/completions` endpoint.
-   Maintain existing "context-aware" prompt injection mechanisms.

## 3. Architecture Design

### 3.1 Abstract Base Class (`LLMProvider`)
Located in `src/providers.py`, this abstract class defines the contract for all providers.

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verify connection to the provider."""
        pass
```

### 3.2 Concrete Implementations
-   `OllamaProvider`: Wraps the existing Ollama logic.
-   `OpenAIProvider`: Uses the `openai` python library (or generic `requests`) to hit a generic endpoint defined in config.

### 3.3 Configuration
New environment variables in `.env`:
-   `AI_PROVIDER`: "ollama" or "openai_compatible"
-   `AI_BASE_URL`: e.g., "http://localhost:11434" (Ollama) or "http://localhost:1234/v1" (LM Studio)
-   `AI_MODEL`: e.g., "llama3", "mistral-7b-instruct"

## 4. Migration Strategy
1.  Define the interface.
2.  Extract current Ollama logic into `OllamaProvider`.
3.  Inject `LLMProvider` into `GamingAIAssistant` instead of hardcoded calls.
4.  Implement `OpenAIProvider`.
5.  Update configuration loading logic.
