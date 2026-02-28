## MODIFIED Requirements

### Requirement: Commodity factor calculation
The system SHALL compute: related metal SHFE 60-day price momentum, futures basis (spot minus near-month futures / near-month futures), LME/SHFE inventory weekly change rate, gold-silver ratio deviation, and gold-copper ratio rate-of-change. Each stock SHALL be linked to its primary metal for commodity factor mapping. The gold-silver ratio and gold-copper ratio factors SHALL only apply to gold-subsector stocks.

#### Scenario: Compute copper price momentum for a copper stock
- **WHEN** system computes commodity factor for stock "601899" (copper-related)
- **THEN** system uses SHFE copper main contract 60-day return as the factor value

#### Scenario: Compute inventory change rate
- **WHEN** SHFE copper inventory was 150,000 tons last week and 140,000 tons this week
- **THEN** inventory change rate is (140000 - 150000) / 150000 = -6.67%, indicating destocking

#### Scenario: Compute gold-silver ratio for a gold stock
- **WHEN** system computes commodity factors for a stock classified under "gold" subsector
- **THEN** system computes `gold_silver_ratio` using Au/Ag futures prices and includes it in the commodity factor output

#### Scenario: Gold cross-metal factors excluded for non-gold stocks
- **WHEN** system computes commodity factors for a stock classified under "copper" subsector
- **THEN** `gold_silver_ratio` and `gold_copper_ratio` return NaN for that stock
