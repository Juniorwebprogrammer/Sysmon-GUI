# Contributor Style Guide

## Language and Environment

- **Python 3.10+** — the project requires Python 3.10 or higher.
- **Type hints** are used on every function and method.

## Code Style

- The project uses **ruff** as both linter and formatter.
- Configuration is in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 120
target-version = "py310"
```

Before committing, run:

```bash
ruff check .
ruff format .
```

- Maximum line length: **120 characters**.
- Use **4 spaces** for indentation (no tabs).
- Variable, function, and method names in `snake_case`.
- Class names in `PascalCase`.
- Constants in `UPPER_SNAKE_CASE`.

## Architecture: Clean Architecture

**Dependency rule**: Dependencies always point inward.

```
presentation -> application/services -> application/ports -> domain
infrastructure -> application/ports
```

- **Never** import from an outer layer in an inner layer.
  - :x: `app/domain/` must not import anything from `app/infrastructure/`
  - :x: `app/application/services/` must not import anything from `app/presentation/`
  - :heavy_check_mark: `app/infrastructure/` may import from `app/application/ports/` and `app/domain/`

### Layer conventions

#### Domain (`app/domain/`)
- Pure Python dataclasses only.
- No external dependencies (neither PyGObject, psutil, nor anything else).
- Immutable: use `@dataclass(frozen=True)` when possible.

#### Application — Ports (`app/application/ports/`)
- Abstract classes inheriting from `ABC` (standard library `abc` module).
- Methods decorated with `@abstractmethod`.
- Clear input/output types using type hints.

#### Application — Services (`app/application/services/`)
- Pure business logic, no framework side-effects.
- Receive dependencies via constructor (dependency injection).
- Do not instantiate concrete implementations directly.
- Use `Protocol` or `ABC` to type dependencies.

#### Infrastructure (`app/infrastructure/`)
- Implement the interfaces defined in `ports/`.
- Handle all communication with the operating system and external libraries.
- One class per adapter, one responsibility per class.

#### Presentation (`app/presentation/`)
- UI logic only. Business logic is delegated to services.
- Do not import directly from `app/infrastructure/`.
- Custom widgets go in `app/presentation/widgets/`.

## File Naming

- Python files in `snake_case.py`.
- Names must reflect content: `clipboard_service.py`, `donut_chart.py`.
- Tests follow the pattern `test_<name>.py`.

## Tests

- Framework: **pytest** + **pytest-mock**.
- Tests must be in `tests/`.
- Name test files as `test_<module>.py`.
- Name test functions as `test_<functionality>`.
- Use mocks to isolate the layer under test:
  - Test services by mocking ports.
  - Do not test concrete infrastructure implementations (or write scoped integration tests).
- Each test must be independent and not rely on global state.

### Coverage

The project requires a minimum of **90% coverage**. It is configured in `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 90
```

If a change drops coverage below 90%, tests will automatically fail.

### Commands

```bash
# Run all tests
pytest -v

# Run a specific file
pytest tests/test_clipboard_service.py -v

# With coverage
pytest -v --cov=app

# Detailed coverage (missing lines)
pytest -v --cov=app --cov-report=term-missing
```

## Commits and Pull Requests

- Use descriptive commit messages in English or Spanish.
- Recommended prefixes:
  - `feat:` — new feature
  - `fix:` — bug fix
  - `refactor:` — refactoring
  - `test:` — test changes
  - `docs:` — documentation
  - `style:` — formatting/linting
- Do not include binary files or `.deb` in the repository.
- Do not include `__pycache__/`, `.ruff_cache/`, `.pytest_cache/` (already in `.gitignore`).

## Import Management

- Use absolute imports within the `app` package.
- Group imports in this order:
  1. Standard library modules
  2. Third-party modules
  3. Project modules (`app.*`)
- Separate each group with a blank line.

## Error Handling

- Catch specific exceptions, not generic `Exception` unless necessary.
- In services, raise custom exceptions defined in `app/domain/` or `app/application/`.
- In infrastructure, catch system exceptions and convert them to application exceptions.

## Type Hints

- Use type hints on all parameters and return values.
- Prefer `list[X]`, `dict[K, V]` over `List[X]`, `Dict[K, V]` (Python 3.10+ style).
- Use `|` for union types: `str | None` instead of `Optional[str]`.
- Define `TypeAlias` when a type is repeated multiple times.
