## ADDED Requirements

### Requirement: Equal-weight scoring mode
The system SHALL support an equal-weight scoring mode where each factor category contributes its configured weight (commodity 35%, fundamental 25%, technical 20%, flow 15%, macro 5%) to the composite score.

#### Scenario: Equal-weight composite score
- **WHEN** scoring mode is set to "equal-weight"
- **THEN** composite score = Σ (category_weight × average_of_category_z_scores) for each stock

### Requirement: IC-weighted scoring mode
The system SHALL support an IC-weighted scoring mode where factor weights are dynamically adjusted based on rolling Information Coefficient (IC) — the correlation between factor values and forward returns.

#### Scenario: IC-weighted scoring
- **WHEN** scoring mode is set to "ic-weighted" and sufficient IC history exists (≥12 months)
- **THEN** factor weights are proportional to their rolling IC mean divided by IC standard deviation (IC_IR)

#### Scenario: Insufficient IC history
- **WHEN** IC history is less than 12 months
- **THEN** system falls back to equal-weight scoring mode

### Requirement: Stock selection and ranking
The system SHALL select the top 20% of stocks by composite score, capped at a maximum of 10 stocks.

#### Scenario: Top stock selection
- **WHEN** composite scores are computed for all stocks in the universe
- **THEN** system selects the top 20% stocks by score, up to a maximum of 10 stocks

### Requirement: Position allocation
The system SHALL allocate portfolio weights using score-proportional allocation, subject to position constraints: single stock maximum 10%, sub-sector maximum 25%.

#### Scenario: Score-proportional allocation
- **WHEN** selected stocks have composite scores
- **THEN** raw weight = stock_score / sum(selected_scores), then constrained by limits

#### Scenario: Single stock limit breach
- **WHEN** a stock's raw weight exceeds 10%
- **THEN** weight is capped at 10% and excess is redistributed proportionally to other stocks

#### Scenario: Sub-sector limit breach
- **WHEN** total weight of stocks in a sub-sector exceeds 25%
- **THEN** weights in that sub-sector are scaled down proportionally to 25%, excess redistributed
