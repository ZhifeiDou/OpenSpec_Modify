## ADDED Requirements

### Requirement: Interactive HTML report generation
The system SHALL generate an interactive HTML report using Plotly, displaying backtest performance metrics and charts.

#### Scenario: Report generation
- **WHEN** user runs the `report` command after a backtest
- **THEN** system generates an HTML file with interactive Plotly charts

### Requirement: NAV curve visualization
The system SHALL display a NAV curve chart comparing portfolio performance against a benchmark (e.g., CSI Non-ferrous Metals Index).

#### Scenario: NAV chart display
- **WHEN** report is generated
- **THEN** report includes an interactive line chart showing portfolio NAV and benchmark NAV over time

### Requirement: Performance metrics summary
The system SHALL display key performance metrics: total return, annualized return, maximum drawdown, Sharpe ratio, Calmar ratio, win rate, and profit/loss ratio.

#### Scenario: Metrics calculation
- **WHEN** backtest NAV series is available
- **THEN** report displays all 7 performance metrics with correct calculations

### Requirement: Position and trade history
The system SHALL display portfolio position history and trade execution log.

#### Scenario: Trade log display
- **WHEN** report is generated
- **THEN** report includes a table of all executed trades with date, stock, direction, price, quantity, and cost

### Requirement: Report export
The system SHALL support exporting charts as static PNG images in addition to the interactive HTML.

#### Scenario: PNG export
- **WHEN** user runs report with `--export png` flag
- **THEN** system exports chart images as PNG files alongside the HTML report
