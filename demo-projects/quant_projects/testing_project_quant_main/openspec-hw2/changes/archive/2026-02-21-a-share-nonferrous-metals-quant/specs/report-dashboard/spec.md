## ADDED Requirements

### Requirement: NAV curve chart
The system SHALL generate a line chart comparing strategy NAV against the non-ferrous metals sector index benchmark. The chart SHALL show both absolute NAV and relative outperformance over time.

#### Scenario: Generate NAV comparison chart
- **WHEN** user requests performance report after backtest
- **THEN** system outputs a chart with two lines: strategy NAV (blue) and benchmark NAV (gray), with dates on x-axis and values on y-axis

#### Scenario: Insufficient data
- **WHEN** less than 20 trading days of data is available
- **THEN** system displays a warning that the chart may not be meaningful

### Requirement: Drawdown analysis chart
The system SHALL generate an underwater chart showing portfolio drawdown over time. Maximum drawdown periods SHALL be highlighted with start/end date annotations.

#### Scenario: Display drawdown chart
- **WHEN** user requests drawdown analysis
- **THEN** system outputs a filled area chart showing drawdown percentage (negative values), with the worst drawdown period highlighted in red

### Requirement: Holdings overview
The system SHALL generate a holdings table showing: stock code, name, sub-sector, current weight, unrealized P&L, and entry date. A pie chart SHALL show weight distribution by sub-sector.

#### Scenario: Show current holdings
- **WHEN** user requests holdings overview for the current (or latest backtest) portfolio
- **THEN** system displays a table with all holdings sorted by weight descending, plus a sub-sector pie chart

### Requirement: Factor exposure heatmap
The system SHALL generate a heatmap showing each held stock's exposure to each factor category (commodity, fundamental, technical, fund flow, macro). Color intensity SHALL represent the standardized factor value.

#### Scenario: Display factor heatmap
- **WHEN** user requests factor exposure report
- **THEN** system outputs a matrix heatmap with stocks on y-axis, factor categories on x-axis, and color representing Z-Score values (red = high, blue = low)

### Requirement: Factor IC tracking chart
The system SHALL generate rolling IC (Information Coefficient) charts for each factor, showing 12-month rolling rank IC values over time. This helps users evaluate which factors are currently effective.

#### Scenario: Display IC tracking
- **WHEN** user requests factor IC report with at least 12 months of data
- **THEN** system outputs line charts for each factor showing rolling IC values, with a horizontal reference line at IC = 0.03

#### Scenario: Insufficient history for IC
- **WHEN** less than 12 months of backtest history is available
- **THEN** system displays available IC data with a note that results may be unreliable

### Requirement: Report export
The system SHALL support exporting reports as HTML (interactive, with Plotly) or PNG (static images). The default format SHALL be HTML.

#### Scenario: Export as HTML
- **WHEN** user requests HTML export
- **THEN** system generates a single HTML file with all charts as interactive Plotly figures

#### Scenario: Export as PNG
- **WHEN** user requests PNG export
- **THEN** system generates individual PNG files for each chart in a specified output directory
