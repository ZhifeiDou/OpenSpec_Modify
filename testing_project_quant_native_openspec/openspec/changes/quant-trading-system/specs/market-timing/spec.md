## ADDED Requirements

### Requirement: Gold hedge signal
The system SHALL generate a market timing signal based on gold price momentum: when gold 20-day momentum is positive and above threshold, signal indicates risk-off (reduce equity exposure).

#### Scenario: Gold risk-off signal
- **WHEN** gold futures 20-day return exceeds +5%
- **THEN** timing signal is "risk-off", reducing target equity exposure by 30%

#### Scenario: Gold neutral signal
- **WHEN** gold futures 20-day return is between -5% and +5%
- **THEN** timing signal is "neutral", maintaining full equity exposure

### Requirement: PMI direction signal
The system SHALL generate a timing signal from PMI trend: expanding PMI (>50 and rising) is bullish, contracting PMI (<50 and falling) is bearish.

#### Scenario: PMI bullish
- **WHEN** PMI > 50 and current PMI > previous month PMI
- **THEN** timing signal is "bullish", allowing full position sizing

#### Scenario: PMI bearish
- **WHEN** PMI < 50 and current PMI < previous month PMI
- **THEN** timing signal is "bearish", reducing target position to 70%

### Requirement: Composite timing signal
The system SHALL combine individual timing signals into a composite signal that adjusts overall portfolio exposure.

#### Scenario: Multiple bearish signals
- **WHEN** both gold and PMI signals indicate caution
- **THEN** composite timing multiplier is the product of individual multipliers (e.g., 0.7 × 0.7 = 0.49)

#### Scenario: Timing signal override
- **WHEN** market timing is disabled in configuration
- **THEN** composite timing multiplier is always 1.0 (no adjustment)
