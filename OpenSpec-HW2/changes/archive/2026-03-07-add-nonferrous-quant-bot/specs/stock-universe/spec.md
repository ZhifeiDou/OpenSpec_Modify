## ADDED Requirements

### Requirement: Filter by sector classification
The system SHALL filter stocks to include only those classified under the Shenwan (申万) non-ferrous metals sector. The system SHALL tag each stock with its sub-sector (copper, aluminum, zinc, tin, nickel, lead, rare earth, tungsten, lithium, cobalt, precious metals, other).

#### Scenario: Sector filtering
- **WHEN** user runs `universe update`
- **THEN** only stocks in the Shenwan non-ferrous metals sector are included in the universe

### Requirement: Exclude ST and suspended stocks
The system SHALL exclude stocks with ST/\*ST designation and stocks currently suspended from trading when `exclude_st` is true.

#### Scenario: ST exclusion
- **WHEN** a stock has ST designation and `exclude_st = true`
- **THEN** the stock is excluded from the universe

### Requirement: Minimum listing days filter
The system SHALL exclude stocks that have been listed for fewer than `min_listing_days` calendar days.

#### Scenario: New listing exclusion
- **WHEN** a stock has been listed for 30 days and `min_listing_days = 60`
- **THEN** the stock is excluded from the universe

### Requirement: Minimum turnover filter
The system SHALL exclude stocks whose average daily turnover over the past 20 trading days is below `min_daily_turnover`.

#### Scenario: Low liquidity exclusion
- **WHEN** a stock's 20-day average daily turnover is 3,000,000 and `min_daily_turnover = 5,000,000`
- **THEN** the stock is excluded from the universe

### Requirement: Sub-sector filtering
The system SHALL support optional filtering by a specific sub-sector.

#### Scenario: Filter by copper sub-sector
- **WHEN** user runs `universe update --subsector copper`
- **THEN** only copper sub-sector stocks (that also pass all other filters) are included

### Requirement: Universe display
The system SHALL support displaying the current universe with sub-sector breakdown counts.

#### Scenario: Show universe
- **WHEN** user runs `universe show`
- **THEN** system displays the total stock count and count per sub-sector

### Requirement: Universe persistence
The system SHALL write the filtered universe to a CSV file with columns: symbol, name, subsector, listing_date, avg_turnover_20d.

#### Scenario: Universe file output
- **WHEN** universe update completes successfully
- **THEN** a CSV file exists at the configured path containing all passing stocks
