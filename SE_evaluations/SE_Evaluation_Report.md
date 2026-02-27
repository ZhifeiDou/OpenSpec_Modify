# Software Engineering Quality Evaluation Report

**Date:** 2026-02-25
**Evaluator:** Claude (Automated SE Quality Assessment)
**Scope:** Three quantitative trading system projects compared across five SE dimensions

---

## Projects Under Evaluation

| # | Project | Approach | Description |
|---|---------|----------|-------------|
| A | `testing_project_quant_noopenspec` | No OpenSpec (ad-hoc) | Quant system built without any specification framework; Flask web app with no tests, no docs, no design artifacts |
| B | `testing_project_quant_native_openspec` | Native OpenSpec (schema-driven) | Quant system built with native OpenSpec schema workflow; includes proposal/design/specs/tasks artifacts and test suite |
| C | `testing_project_quant` | OpenSpec-HW (OPSX skill-based) | Full-featured quant system built with OpenSpec-HW workflow; includes archived change artifacts, comprehensive specs, tests, and documentation |

---

## Project Metrics Overview

| Metric | Project A (No OpenSpec) | Project B (Native OpenSpec) | Project C (OpenSpec-HW) |
|--------|------------------------|---------------------------|------------------------|
| Source code files | 6 Python files | 28 Python files | 27 Python files |
| Source LOC | ~1,200 | ~1,430 | ~3,909 |
| Test files | 0 | 8 test files | 8 test files + conftest |
| Test LOC | 0 | ~440 | ~779 |
| Test cases | 0 | ~58 | ~56 |
| Spec/Design artifacts | 0 | 16 files (~600 LOC) | 24 files (~1,634 LOC) |
| README | No | No | Yes (132 lines) |
| Config management | Python dict (87 lines) | YAML (95 lines) | YAML (72 lines) |
| Total project LOC | ~1,727 | ~2,577 | ~6,870 |
| Modules/packages | 6 flat files | 8 packages under `src/` | 7 packages under `src/` |

---

## Dimension 1: Specifications and Requirements

### Scoring

| Project | Score | Rating |
|---------|-------|--------|
| A (No OpenSpec) | **1 / 5** | Poor |
| B (Native OpenSpec) | **4 / 5** | Very Good |
| C (OpenSpec-HW) | **5 / 5** | Excellent |

### Rationale

**Project A (1/5):**
- **Zero specification documents** of any kind.
- No requirements doc, no use cases, no feature list, no API spec.
- No README to describe what the system does or its capabilities.
- The only "specification" is implicit in the code itself.
- `requirements.txt` lists only 4 pip dependencies -- no functional requirements captured anywhere.

**Project B (4/5):**
- OpenSpec artifact chain: proposal -> design -> specs -> tasks (no use cases document).
- **8 specification documents** with 38 requirements and 56 testable scenarios using WHEN/THEN format.
- Well-structured proposal (40 lines) with Why/What/Capabilities/Impact sections.
- Schema-driven workflow with `openspec/schemas/native-openspec/schema.yaml` defining artifact templates and dependency chains.
- Slightly less detailed than Project C (missing use cases document; fewer total spec lines).

**Project C (5/5):**
- Complete OpenSpec artifact chain: proposal -> use cases -> design -> specs -> tasks, all archived in `openspec/changes/archive/`.
- **8 formal specification documents** using normative language (SHALL/MUST) covering data-pipeline, stock-universe, factor-engine, scoring-strategy, market-timing, risk-management, backtest-engine, and report-dashboard.
- **284-line use case document** with 8 fully-dressed use cases following Cockburn format (actor, scope, preconditions, postconditions, triggers, main scenario, extensions).
- Specs include **concrete testable scenarios** in WHEN/THEN format (e.g., "sell order of CNY 100,000 -> costs = stamp_tax(50) + commission(30) + slippage(150) = 230").
- **Traceability from specs to tests**: spec scenarios map directly to test cases in the codebase.
- 40-line proposal document with clear Why/What Changes/Capabilities/Impact structure.

---

## Dimension 2: Design

### Scoring

| Project | Score | Rating |
|---------|-------|--------|
| A (No OpenSpec) | **1 / 5** | Poor |
| B (Native OpenSpec) | **4 / 5** | Very Good |
| C (OpenSpec-HW) | **5 / 5** | Excellent |

### Rationale

**Project A (1/5):**
- **Zero design documents**. No architecture description, no decision records, no diagram.
- Architecture is purely implicit -- 6 flat Python modules with procedural functions.
- No OOP abstractions: zero class definitions across the entire project.
- No use of design patterns (no interfaces, no protocols, no dependency injection).
- Tight coupling between modules: `backtester.py` imports from every other module.
- `backtester.py` **re-implements** momentum/MACD/RSI calculations that already exist in `factor_engine.py`, indicating lack of architectural planning.
- `debug=True` hardcoded in Flask app -- a design-level security concern.

**Project B (4/5):**
- **93-line design document** with 6 architectural decisions, goals/non-goals, 4 risks with mitigations, and 3 open questions.
- Each decision explains "why X over Y" with concrete alternatives.
- Clean domain-driven modular architecture with 8 packages.
- Good use of design patterns:
  - Inversion of control via `rebalance_callback` parameter in backtest engine
  - Strategy pattern for data source failover with priority ordering
  - Cache-aside pattern for data fetching
  - `@dataclass` for `Position` and `Order`
- Slightly less detailed than Project C (6 decisions vs 8; shorter design doc; no Protocol/ABC abstractions).

**Project C (5/5):**
- **254-line design document** with context, explicit goals/non-goals, and 8 architectural decisions with rationale and alternatives considered.
- Risk analysis identifies 5 risks with mitigation strategies and 2 explicit trade-offs (e.g., "simplicity vs accuracy for slippage modeling").
- Open questions section identifies 4 unresolved decisions for future consideration.
- Clean **layered modular architecture**: `data -> universe -> factors -> strategy -> risk -> backtest -> report` with unidirectional dependencies.
- Uses modern Python design patterns:
  - `typing.Protocol` with `@runtime_checkable` for data source abstraction
  - `ABC` with `@register_factor` decorator for plugin-style factor registration
  - `@dataclass` for value objects (`OrderResult`, `TradeRecord`, `BacktestResult`, etc.)
  - Adapter pattern for AKShare/BaoStock source wrappers
  - Pipeline pattern for data orchestration

---

## Dimension 3: Implementation

### Scoring

| Project | Score | Rating |
|---------|-------|--------|
| A (No OpenSpec) | **2 / 5** | Below Average |
| B (Native OpenSpec) | **4 / 5** | Very Good |
| C (OpenSpec-HW) | **4 / 5** | Very Good |

### Rationale

**Project A (2/5):**
- **1,200 lines of functional but unrefined code** across 6 flat files.
- **No type hints** anywhere in the project.
- **No logging framework** -- uses `print()` and `traceback.print_exc()` throughout.
- Uses `print()` for warnings/errors in production web app code.
- **Duplicated logic**: backtester re-implements simplified factor calculations from `factor_engine.py`.
- Global mutable `_cache` dictionary for in-process caching -- not thread-safe.
- Row-by-row SQLite writes instead of vectorized `to_sql()`.
- Row-by-row backtest iteration instead of vectorized pandas operations.
- **Security issues**: `debug=True` hardcoded; raw exception messages returned to client.
- Flask web frontend (`index.html`) is actually well-crafted (523-line SPA with ECharts).
- Decent function-level docstrings for key functions.

**Project B (4/5):**
- **1,430 lines of clean source code** across 28 files in 8 packages.
- Modern Python type hints used consistently (`dict[str, float]`, `str | None`, `list[dict]`).
- Pure functions for calculations, classes for stateful components -- appropriate separation.
- Custom exception `DataSourceError` defined for data layer failures.
- Guard clauses against division by zero throughout (e.g., `if std == 0: return 0.0`).
- Resource cleanup via `close()` methods and `yield`-based fixtures.
- Minor weaknesses: broad `except Exception` in API wrappers; f-string SQL table names (injection risk); duplicated config loading logic.

**Project C (4/5):**
- **3,909 lines of well-structured source code** across 27 files in 7 packages.
- Consistent code style with docstrings on all public classes and functions.
- Type hints used throughout (`Protocol`, `dataclass`, `Optional`, `Dict`, etc.).
- Clean error handling: graceful degradation with NaN propagation for missing data, fallback chains for data sources, rejection results instead of exceptions for order failures.
- Configuration externalized to YAML with safe defaults via `config.get("key", default)`.
- Comprehensive CLI with 7 commands (fetch, backtest, report, etc.) via `argparse`.
- Minor weaknesses: generic `except Exception` in some places; no config schema validation; no custom exception hierarchy.

---

## Dimension 4: Verification and Validation

### Scoring

| Project | Score | Rating |
|---------|-------|--------|
| A (No OpenSpec) | **1 / 5** | Poor |
| B (Native OpenSpec) | **3 / 5** | Average |
| C (OpenSpec-HW) | **4 / 5** | Very Good |

### Rationale

**Project A (1/5):**
- **Zero tests**. No `tests/` directory, no `test_*.py` files, no test configuration.
- No `pytest.ini`, `tox.ini`, `setup.cfg`, or any testing infrastructure.
- No CI/CD configuration (no GitHub Actions, no Makefile, no Docker).
- No linting configuration (`flake8`, `pylint`, `ruff`, `mypy`).
- For a quantitative trading system where numerical correctness directly impacts financial decisions, the complete absence of tests is a critical deficiency.

**Project B (3/5):**
- **58 test cases** across 8 test modules, totaling ~440 lines.
- Tests organized in a flat `tests/` directory (not mirroring source structure).
- Tests verify specific numerical values (e.g., transaction costs = 180/230, drawdown percentages).
- Edge cases covered: insufficient data returns NaN, zero ATR returns 0 shares, suspended stocks defer orders.
- Proper use of `pytest` fixtures (`tmp_path` for cache database).
- Gaps: **no integration test** exercising the full pipeline; no mocking of external API calls; data API wrappers untested; report generation untested; main.py CLI untested.
- Task 10.2 ("integration test") marked complete in tasks.md but no corresponding test file exists.

**Project C (4/5):**
- **56 test cases** across 8 test modules + 1 integration test, totaling 779 lines.
- Test structure mirrors source structure: `tests/backtest/`, `tests/data/`, `tests/factors/`, `tests/report/`, `tests/risk/`, `tests/strategy/`, `tests/universe/`.
- **Integration test** creates a temporary SQLite database with synthetic data (5 stocks, 5 metals, 2 years of daily data) and exercises the full pipeline end-to-end.
- Shared fixtures in `conftest.py` for reusable test data.
- Edge case coverage: empty DataFrames, NaN handling, constant columns, insufficient cash, empty scores.
- Boundary testing: drawdown thresholds tested at "reduce" (15%) and "liquidate" (20%) levels.
- `pytest.ini` configured with markers and test discovery.
- Gaps: no tests for `broker.py`, `pipeline.py`, `signal.py`, or `alerts.py`; no mocking of external APIs; test-to-source ratio ~20%.

---

## Dimension 5: Maintenance and Evolution

### Scoring

| Project | Score | Rating |
|---------|-------|--------|
| A (No OpenSpec) | **1 / 5** | Poor |
| B (Native OpenSpec) | **4 / 5** | Very Good |
| C (OpenSpec-HW) | **5 / 5** | Excellent |

### Rationale

**Project A (1/5):**
- **No README** -- no setup instructions, no architecture overview, no contribution guide.
- **No design rationale documented** anywhere -- a future developer would have to reverse-engineer all decisions from the code.
- **No specifications** to understand intended behavior vs actual behavior.
- **No tests** -- any modification risks silent regression with no way to detect it.
- **No type hints** -- refactoring without static type analysis is error-prone.
- **No logging** -- debugging production issues requires adding `print()` statements.
- **No modular extension points** -- adding a new data source, factor, or strategy requires modifying existing modules rather than extending them.
- **Hardcoded configuration** in Python constants -- changing parameters requires code changes and redeployment.
- **Duplicated logic** between `factor_engine.py` and `backtester.py` creates a maintenance trap where updating one requires remembering to update the other.
- **No packaging** (`pyproject.toml`, `setup.py`) -- distribution and installation are not standardized.

**Project B (4/5):**
- **No README** -- a significant gap for maintenance and onboarding.
- OpenSpec change artifacts (`proposal.md`, `design.md`, `tasks.md`, 8 spec files) provide design rationale and system behavior documentation.
- Schema-driven workflow (`openspec/schemas/`) with reusable templates for future changes -- structural support for evolution.
- YAML configuration is comprehensive (95 lines) and well-commented.
- Module-level and function-level docstrings provide inline maintenance documentation.
- Good type hints support IDE-assisted refactoring.
- Inversion of control (`rebalance_callback`) makes the backtest engine extensible without modification.
- Change artifacts are not yet archived (still in `openspec/changes/`), suggesting the development cycle is not yet complete.

**Project C (5/5):**
- **README.md** (132 lines): system architecture diagram, CLI command reference, factor table, risk control rules, A-share simulation details, data source documentation, directory structure.
- **OpenSpec change archive** provides a complete audit trail of why the system was built the way it was -- proposal rationale, design decisions, use cases, and specifications are all preserved.
- **Plugin architecture** for factors via `@register_factor` decorator: adding a new factor requires only creating a new module file with a decorated class -- no modification to existing code.
- **Protocol-based data source interface**: adding a new data provider (e.g., Tushare) requires implementing `DataSource` protocol without touching existing sources.
- **YAML configuration**: strategy parameter changes (weights, thresholds, rebalance frequency) require only editing `settings.yaml`, not code.
- **8 synced spec files** in `openspec/specs/` serve as living documentation of system behavior.
- Demo script (`notebooks/demo_workflow.py`) serves as onboarding material for new developers.
- **Versioned change history**: the OpenSpec archive structure (`openspec/changes/archive/2026-02-21-...`) provides timestamped, self-documenting change sets.

---

## Summary Comparison

### Score Matrix

| Dimension | Project A (No OpenSpec) | Project B (Native OpenSpec) | Project C (OpenSpec-HW) |
|-----------|:----------------------:|:-------------------------:|:----------------------:|
| 1. Specifications & Requirements | **1** | **4** | **5** |
| 2. Design | **1** | **4** | **5** |
| 3. Implementation | **2** | **4** | **4** |
| 4. Verification & Validation | **1** | **3** | **4** |
| 5. Maintenance & Evolution | **1** | **4** | **5** |
| **Total (out of 25)** | **6** | **19** | **23** |
| **Average (out of 5)** | **1.2** | **3.8** | **4.6** |

### Radar Chart (ASCII)

```
                    Specifications
                         5
                         |
                    4    |
                    3    |
                    2    |
                    1    |
Maintenance -------+----+----+------- Design
    5  4  3  2  1  |    |  1  2  3  4  5
                    |    |
                    |    |
                    |    |
                    |    |
                         |
                  Verification
                         5
                         |
                   Implementation
                         5

Project A (No OpenSpec):        1-1-2-1-1 = 6/25
Project B (Native OpenSpec):    4-4-4-3-4 = 19/25
Project C (OpenSpec-HW):        5-5-4-4-5 = 23/25
```

---

## Key Findings

### 1. OpenSpec dramatically improves specification and design quality
Both OpenSpec projects (B and C) scored 4-5 on specifications and design, while the no-OpenSpec project scored 1 in both. The structured artifact workflow (proposal -> design -> specs -> tasks) ensures that requirements are explicitly captured, design decisions are documented with rationale, and behavioral specifications are written in testable WHEN/THEN format before implementation begins.

### 2. Specification-driven development leads to better test coverage
Project C's spec scenarios map directly to test cases, demonstrating **traceability from requirements to verification**. Project B also shows this pattern, though with less complete coverage. Project A, lacking any specifications, has zero tests -- suggesting that without explicit requirements, developers skip verification entirely.

### 3. Architectural quality correlates with upfront design work
The OpenSpec projects both use clean modular architectures with design patterns (Protocol, ABC, Adapter, Pipeline) because these decisions were documented in design artifacts. Project A's flat, procedural structure with duplicated logic and tight coupling reflects the absence of architectural planning.

### 4. The gap is most extreme in maintenance and evolution
Project C's combination of README, archived change history, plugin architecture, protocol-based interfaces, YAML configuration, and living specifications creates a system that is **demonstrably maintainable**. Project A's complete absence of documentation, tests, type hints, extension points, and design rationale makes any future modification high-risk.

### 5. Implementation quality is the most similar dimension
All three projects produce functionally correct quantitative trading systems. The implementation dimension (2:4:4) shows the smallest spread, suggesting that code quality is partially a function of developer skill regardless of process. However, even here, the OpenSpec projects benefit from cleaner architecture (driven by design docs) and better error handling patterns.

---

## Recommendations

### For Project A (No OpenSpec) -- Score: 6/25
- **Start with a README** describing the system, setup, and usage
- **Add a test suite** -- begin with the factor calculations and backtester logic
- Replace `print()` with the `logging` module
- Add type hints throughout
- Remove `debug=True` from production Flask code
- Eliminate duplicated factor logic between `factor_engine.py` and `backtester.py`
- Consider restructuring into packages with clear module boundaries
- Add a `.gitignore` file
- Consider adopting OpenSpec or similar specification workflow for future development

### For Project B (Native OpenSpec) -- Score: 19/25
- **Add a README.md** -- this is the most impactful single improvement
- Add an end-to-end integration test
- Add tests for data API wrappers and report generation
- Fix duplicated config loading (centralize in one place)
- Parameterize SQL table names to avoid injection risk

### For Project C (OpenSpec-HW) -- Score: 23/25
- Add tests for untested modules: `broker.py`, `pipeline.py`, `signal.py`, `alerts.py`
- Add mocking for external API calls in unit tests
- Replace generic `except Exception` with specific exception types
- Add config schema validation (e.g., using Pydantic)
