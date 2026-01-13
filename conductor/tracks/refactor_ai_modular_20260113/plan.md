# Plan: Modular AI Provider Support

## Phase 1: Infrastructure & Interface Definition [checkpoint: 3147367]
- [x] Task: Create `src/interfaces.py` (or update `src/providers.py`) to define the `LLMProvider` abstract base class. (243518f)
    - [x] Sub-task: Write tests for the interface contract.
    - [x] Sub-task: Implement the `LLMProvider` ABC.
- [x] Task: Implement a `MockProvider` for testing. (243518f)
    - [x] Sub-task: Write tests for `MockProvider`.
    - [x] Sub-task: Implement `MockProvider`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Infrastructure & Interface Definition' (Protocol in workflow.md)

## Phase 2: Refactor Ollama Integration [checkpoint: f88c66a]
- [x] Task: Extract Ollama logic into `OllamaProvider`. (609f8a6)
    - [x] Sub-task: Write unit tests for `OllamaProvider` (mocking the API).
    - [x] Sub-task: Implement `OllamaProvider` in `src/providers.py`.
- [x] Task: Update `GamingAIAssistant` to use dependency injection. (609f8a6)
    - [x] Sub-task: Update `GamingAIAssistant` tests to use `MockProvider`.
    - [x] Sub-task: Refactor `GamingAIAssistant` to accept an `LLMProvider` and use its methods.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Refactor Ollama Integration' (Protocol in workflow.md)

## Phase 3: Implement OpenAI-Compatible Provider [checkpoint: ea455c6]
- [x] Task: Implement `OpenAIProvider`. (cc0bc8e)
    - [x] Sub-task: Write unit tests for `OpenAIProvider` (mocking the HTTP calls).
    - [x] Sub-task: Implement `OpenAIProvider` to support generic `/v1/chat/completions`.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Implement OpenAI-Compatible Provider' (Protocol in workflow.md)

## Phase 4: Configuration & Factory Logic
- [ ] Task: Implement Provider Factory.
    - [ ] Sub-task: Write tests for `get_provider(config)`.
    - [ ] Sub-task: Implement the factory function to return the correct provider based on env vars.
- [ ] Task: Update App Entry Point.
    - [ ] Sub-task: Modify `main.py` or the configuration manager to instantiate the correct provider.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Configuration & Factory Logic' (Protocol in workflow.md)
