## Purpose

Performance report output module supporting multiple formats (table, CSV, JSON, dict) with optional holdings analysis, factor exposure breakdown, and drawdown period analysis.

## Requirements

### Requirement: Multiple output formats
The system SHALL support four output formats for the performance report: `table` (human-readable terminal table), `csv` (comma-separated values), `json` (structured JSON), and `dict` (Python dictionary for API consumption). The default format SHALL be `table`. The `dict` format SHALL return a Python dict (not serialized JSON string) suitable for direct use by FastAPI response models.

#### Scenario: Table format output
- **WHEN** user runs `report --format table`
- **THEN** system displays a formatted table using comfy-table with aligned columns

#### Scenario: CSV format output
- **WHEN** user runs `report --format csv`
- **THEN** system outputs comma-separated values suitable for import into spreadsheet tools

#### Scenario: Dict format output
- **WHEN** `ReportExporter.export(result, format="dict")` is called
- **THEN** system returns a Python dictionary with keys: `metrics`, `nav_series`, `drawdown_series`, `factor_exposures`, `trade_log`, `holdings`

#### Scenario: JSON format output
- **WHEN** user runs `report --format json`
- **THEN** system outputs a structured JSON object with metrics, series, and analysis sections

### Requirement: Summary metrics display
The system SHALL display the following summary metrics: annualized return, Sharpe ratio, max drawdown, max drawdown duration, total trades, win rate, profit factor, and final NAV.

#### Scenario: Summary metrics
- **WHEN** user runs `report` with a valid backtest result
- **THEN** all eight summary metrics are displayed with appropriate formatting (percentages, ratios, currency)

### Requirement: Holdings analysis
When `--holdings` is provided, the system SHALL display per-stock analysis: symbol, name, average entry price, current/exit price, holding period, realized PnL, and weight in portfolio.

#### Scenario: Holdings breakdown
- **WHEN** user runs `report --holdings portfolio.csv`
- **THEN** system displays a per-stock breakdown table sorted by PnL descending

### Requirement: Factor exposure analysis
When `--factors` is provided, the system SHALL display the portfolio's average exposure to each factor category (commodity, fundamental, technical, flow, macro) and individual factor loadings.

#### Scenario: Factor exposure
- **WHEN** user runs `report --factors factors.csv`
- **THEN** system displays factor category average scores and top/bottom individual factor exposures

### Requirement: Drawdown analysis
When `--drawdowns` is provided, the system SHALL display a table of the top 5 drawdown periods showing: start date, trough date, recovery date, depth (percentage), and duration (trading days).

#### Scenario: Drawdown periods
- **WHEN** user runs `report --drawdowns` and the backtest had 3 significant drawdowns
- **THEN** system displays all 3 drawdown periods with start, trough, recovery dates and depth

### Requirement: Default source file
When no `--source` is specified, the system SHALL look for the default backtest result at `output/backtest_result.json`.

#### Scenario: Default source
- **WHEN** user runs `report` without `--source` and `output/backtest_result.json` exists
- **THEN** system loads and reports from the default file

#### Scenario: Missing default source
- **WHEN** user runs `report` without `--source` and no default file exists
- **THEN** system reports an error suggesting to run `backtest` first
