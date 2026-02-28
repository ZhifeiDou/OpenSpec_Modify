## MODIFIED Requirements

### Requirement: Commodity futures data
The system SHALL fetch SHFE futures prices (copper cu, aluminum al, zinc zn, nickel ni, tin sn, lead pb, gold au, silver ag) and LME corresponding metal prices. The system SHALL also fetch SHFE warehouse inventory data and futures basis (spot minus futures).

#### Scenario: Fetch SHFE copper main contract price
- **WHEN** user requests copper futures update
- **THEN** system returns daily OHLCV for the continuous main contract (cu0) with settlement price

#### Scenario: Fetch LME metals prices
- **WHEN** user requests LME data update
- **THEN** system returns daily closing prices for all 6 base metals (copper, aluminum, zinc, nickel, tin, lead)

#### Scenario: Fetch silver futures data
- **WHEN** user requests futures update and `_metals` list includes "ag"
- **THEN** system fetches daily OHLCV for the silver continuous main contract (ag0) and stores it in `futures_daily` with `metal = 'ag'`

#### Scenario: Fetch gold inventory data
- **WHEN** user requests inventory update for metal "au"
- **THEN** system resolves "au" to "黄金" in the metal name mapping and returns gold exchange inventory data

#### Scenario: Fetch silver inventory data
- **WHEN** user requests inventory update for metal "ag"
- **THEN** system resolves "ag" to "白银" in the metal name mapping and returns silver exchange inventory data
