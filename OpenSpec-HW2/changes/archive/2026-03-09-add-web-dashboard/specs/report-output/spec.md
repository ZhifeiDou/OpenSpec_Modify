## MODIFIED Requirements

### Requirement: Multiple output formats
The system SHALL support four output formats for the performance report: `table` (human-readable terminal table), `csv` (comma-separated values), `json` (structured JSON), and `dict` (Python dictionary for API consumption). The default format SHALL be `table`. The `dict` format SHALL return a Python dict (not serialized JSON string) suitable for direct use by FastAPI response models.

#### Scenario: Dict format output
- **WHEN** `ReportExporter.export(result, format="dict")` is called
- **THEN** system returns a Python dictionary with keys: `metrics`, `nav_series`, `drawdown_series`, `factor_exposures`, `trade_log`, `holdings`

#### Scenario: JSON format output
- **WHEN** user runs `report --format json`
- **THEN** system outputs a structured JSON object with metrics, series, and analysis sections
