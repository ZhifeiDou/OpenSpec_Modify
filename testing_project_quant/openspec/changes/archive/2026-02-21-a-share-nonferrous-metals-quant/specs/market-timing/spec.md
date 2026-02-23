## ADDED Requirements

### Requirement: Commodity momentum timing signal
The system SHALL compute a market timing signal based on SHFE copper and aluminum futures price momentum. The signal SHALL determine the overall portfolio position ratio: 1.0 (full), 0.6, 0.3, or 0.2 (defensive).

#### Scenario: Full position signal
- **WHEN** SHFE copper 60-day momentum > 0 AND copper 20-day momentum > 0 AND aluminum 20-day momentum > 0
- **THEN** position ratio is 1.0 (full position)

#### Scenario: Moderate position signal
- **WHEN** exactly 1 of the 3 momentum conditions is true
- **THEN** position ratio is 0.6

#### Scenario: Defensive position signal
- **WHEN** all 3 momentum conditions are false AND gold 60-day momentum > 5%
- **THEN** position ratio is 0.3 with preference for gold sub-sector stocks

#### Scenario: Minimum position signal
- **WHEN** all 3 momentum conditions are false AND gold momentum <= 5%
- **THEN** position ratio is 0.2 (near cash)

### Requirement: Gold hedging signal
The system SHALL track SHFE gold futures 60-day momentum as a hedging indicator. When industrial metals momentum is negative but gold momentum is strongly positive (> 5%), the system SHALL shift allocation toward gold sub-sector stocks.

#### Scenario: Gold hedge activation
- **WHEN** copper and aluminum momentum are both negative AND gold momentum is +8%
- **THEN** system recommends allocating available position ratio primarily to gold sub-sector stocks

#### Scenario: No hedge needed
- **WHEN** copper momentum is positive
- **THEN** system uses normal multi-factor scoring without gold preference

### Requirement: Timing signal override
The system SHALL allow users to manually override the timing signal with a fixed position ratio. The override SHALL persist until explicitly cleared.

#### Scenario: User forces full position
- **WHEN** user sets position ratio override to 1.0
- **THEN** system ignores commodity momentum signals and uses 1.0 until override is cleared

#### Scenario: Clear override
- **WHEN** user clears the position ratio override
- **THEN** system resumes computing timing signals from commodity momentum
