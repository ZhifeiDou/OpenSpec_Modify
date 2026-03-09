## ADDED Requirements

### Requirement: React application with Material Design
The system SHALL provide a React + TypeScript frontend application in `frontend/` using MUI (Material UI) component library for Google-style clean design. The application SHALL use a responsive layout with a persistent left sidebar navigation and a top app bar.

#### Scenario: Load dashboard
- **WHEN** user opens `http://localhost:8000` in a browser
- **THEN** a clean Material Design dashboard loads with sidebar navigation and overview page

### Requirement: Overview page
The system SHALL display an overview page as the default landing page with: data freshness summary cards, latest portfolio metrics (NAV, daily return, Sharpe), risk status indicator (green/yellow/red), and a mini NAV chart showing recent 30-day performance.

#### Scenario: All data available
- **WHEN** data, backtest, and risk information exist
- **THEN** overview shows all cards populated with live data

#### Scenario: Empty state
- **WHEN** no data has been fetched
- **THEN** overview shows "Get Started" guidance cards

### Requirement: Data Management page
The system SHALL display a Data Management page showing: last-updated timestamps for each category in a status table, "Update" buttons per category and an "Update All" button, progress indicator during updates, and a history of recent update operations.

#### Scenario: Trigger update
- **WHEN** user clicks "Update Stock Data"
- **THEN** system calls `POST /api/data/update`, shows a loading spinner, and refreshes timestamps on completion

### Requirement: Universe page
The system SHALL display a Universe page with: a searchable/sortable data table of current stocks (symbol, name, subsector, listing date, turnover), a sub-sector distribution pie chart, and a search/filter bar.

#### Scenario: Search stocks
- **WHEN** user types "copper" in the filter
- **THEN** table shows only copper-subsector stocks

### Requirement: Factor Analysis page
The system SHALL display a Factor Analysis page with: a factor heatmap (interactive Plotly chart embedded via `react-plotly.js`), category-level score summary bar chart, and a detail panel that shows factor distribution histogram and IC tracking chart when a factor is clicked.

#### Scenario: View factor detail
- **WHEN** user clicks on "metal_price_mom_60d" in the heatmap
- **THEN** a detail panel opens showing that factor's value distribution and IC chart

### Requirement: Signals page
The system SHALL display a Signals page with: a ranked table of stocks by composite score with color-coded signal direction (green=buy, gray=hold, red=sell), sentiment label column, and an expandable row showing per-factor score contributions.

#### Scenario: Expand signal detail
- **WHEN** user clicks a stock row
- **THEN** row expands to show individual factor contributions as a horizontal bar chart

### Requirement: Risk Monitor page
The system SHALL display a Risk Monitor page with: a drawdown underwater chart (Plotly), an alert panel showing active risk warnings with severity (info/warning/critical), and a position risk table showing per-stock weight, stop price, and distance to stop.

#### Scenario: Active alerts
- **WHEN** portfolio drawdown exceeds 15%
- **THEN** alert panel shows a critical warning with the drawdown percentage

#### Scenario: No alerts
- **WHEN** all risk metrics are within normal ranges
- **THEN** system shows a green "All clear" status badge

### Requirement: Backtest page
The system SHALL display a Backtest page with: input form for start date, end date, and initial capital; a "Run Backtest" button; and results section showing NAV curve chart (strategy vs benchmark), summary metrics cards (annual return, Sharpe, max drawdown, win rate), and a trade log table with date, symbol, action, price, quantity, PnL columns.

#### Scenario: Run backtest
- **WHEN** user fills in dates and clicks "Run Backtest"
- **THEN** system shows a loading state, then renders results with charts and metrics

#### Scenario: Load previous result
- **WHEN** a previous backtest result exists and user opens the page
- **THEN** the most recent result is pre-loaded

### Requirement: Report page
The system SHALL display a Report page with: all report visualizations (NAV chart, drawdown chart, factor heatmap, holdings breakdown), summary metrics grid, and an "Export HTML" button.

#### Scenario: Export report
- **WHEN** user clicks "Export HTML"
- **THEN** system downloads the current report as a standalone HTML file

### Requirement: Responsive layout
The system SHALL be responsive: the sidebar collapses to a hamburger menu on screens narrower than 768px. Cards and charts SHALL stack vertically on mobile viewports.

#### Scenario: Mobile view
- **WHEN** user opens the dashboard on a phone-width viewport
- **THEN** sidebar becomes a toggleable drawer and content stacks vertically

### Requirement: Color theme
The system SHALL use a light theme with Google-style color palette: white background, blue primary (#1976d2), subtle gray cards (#f5f5f5 background, #e0e0e0 borders), and Roboto font family. Charts SHALL use a consistent color scale.

#### Scenario: Visual consistency
- **WHEN** user navigates between pages
- **THEN** all pages use the same typography, spacing, and color palette

### Requirement: Production build
The system SHALL support building the frontend as static files (`npm run build`) that are served by FastAPI from `frontend/build/`. No separate Node.js server is needed in production.

#### Scenario: Production deployment
- **WHEN** user runs `npm run build` in `frontend/` and starts `python main.py serve`
- **THEN** dashboard is served as static files by the FastAPI server
