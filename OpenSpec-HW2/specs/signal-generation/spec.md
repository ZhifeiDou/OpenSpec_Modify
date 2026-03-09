## Purpose

Trading signal generation module. Computes composite scores from multi-factor weights, selects top stocks, allocates weights with concentration constraints, applies timing adjustment, and outputs actionable trade signals.

## Requirements

### Requirement: Composite scoring
The system SHALL compute a composite score for each stock as the weighted sum of factor category scores. The weights are defined in config: `commodity_weight`, `fundamental_weight`, `technical_weight`, `flow_weight`, `macro_weight`. The weights MUST sum to 1.0.

#### Scenario: Score computation
- **WHEN** a stock has commodity_score=0.8, fundamental_score=0.5, technical_score=0.3, flow_score=0.6, macro_score=0.2 and weights are 0.35/0.25/0.20/0.15/0.05
- **THEN** composite score = 0.35*0.8 + 0.25*0.5 + 0.20*0.3 + 0.15*0.6 + 0.05*0.2 = 0.56

### Requirement: Stock selection
The system SHALL rank stocks by composite score in descending order and select the top `max_stocks` stocks for the portfolio.

#### Scenario: Select top stocks
- **WHEN** `max_stocks = 10` and 45 stocks have composite scores
- **THEN** the top 10 stocks by score are selected for the target portfolio

### Requirement: Weight allocation with concentration limits
The system SHALL allocate portfolio weights to selected stocks subject to:
- No single stock weight exceeds `max_single_weight`
- No sub-sector total weight exceeds `max_subsector_weight`
- Total allocated weight equals the position size from timing (default 1.0)

The allocator SHALL use score-proportional weighting as the starting point, then iteratively clip and redistribute to satisfy constraints.

#### Scenario: Single stock cap
- **WHEN** `max_single_weight = 0.10` and a stock's score-proportional weight would be 0.15
- **THEN** the stock's weight is capped at 0.10 and excess is redistributed to other stocks

#### Scenario: Sub-sector cap
- **WHEN** `max_subsector_weight = 0.25` and three copper stocks have combined weight 0.30
- **THEN** copper stocks' weights are proportionally reduced to sum to 0.25 and excess is redistributed

### Requirement: Timing adjustment
The system SHALL apply a timing multiplier to the overall portfolio position size based on macro/market conditions. The timing signal SHALL range from 0.0 (fully defensive) to 1.0 (fully invested).

#### Scenario: Bearish timing
- **WHEN** PMI is below 50 and USD momentum is strongly positive (bearish for metals)
- **THEN** timing multiplier is reduced (e.g., 0.5), halving all position weights

#### Scenario: Bullish timing
- **WHEN** PMI is above 50 and metal momentum is positive
- **THEN** timing multiplier is 1.0, keeping position weights at full size

### Requirement: Trade delta calculation
When a current portfolio is provided, the system SHALL compute the trade deltas: stocks to buy (new positions or increase), stocks to sell (exit or decrease), and stocks to hold.

#### Scenario: Trade delta with existing portfolio
- **WHEN** current portfolio has stocks A(5%), B(8%), C(7%) and target has A(10%), D(8%), E(7%)
- **THEN** system outputs: buy A(+5%), buy D(8%), buy E(7%), sell B(-8%), sell C(-7%)

### Requirement: Signal output format
The system SHALL output the signal as a table with columns: symbol, name, subsector, composite_score, target_weight, current_weight (if portfolio provided), trade_action (buy/sell/hold), trade_weight_delta.

#### Scenario: Signal output
- **WHEN** signal generation completes with 10 selected stocks
- **THEN** system prints a formatted table with all columns and saves to `output/signal_YYYYMMDD.csv`
