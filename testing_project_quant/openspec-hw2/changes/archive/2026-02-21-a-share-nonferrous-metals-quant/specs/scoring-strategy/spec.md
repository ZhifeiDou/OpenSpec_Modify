## ADDED Requirements

### Requirement: Weighted factor scoring
The system SHALL compute a composite score for each stock by weighting standardized factor categories: commodity 35%, fundamental 25%, technical 20%, fund flow 15%, macro 5%. Within each category, individual factors SHALL be equally weighted.

#### Scenario: Compute composite score
- **WHEN** stock "601899" has category scores: commodity=1.2, fundamental=0.8, technical=0.5, fund_flow=0.3, macro=0.1
- **THEN** composite score = 1.2*0.35 + 0.8*0.25 + 0.5*0.20 + 0.3*0.15 + 0.1*0.05 = 0.42 + 0.20 + 0.10 + 0.045 + 0.005 = 0.77

#### Scenario: Handle NaN factor values
- **WHEN** a stock has NaN for one factor in the commodity category
- **THEN** system computes the category score using the remaining non-NaN factors in that category

### Requirement: Stock selection by ranking
The system SHALL select the top N stocks by composite score, where N = min(max_stocks, floor(universe_size * 0.2)). The default max_stocks SHALL be 10.

#### Scenario: Select top stocks from 80-stock universe
- **WHEN** universe has 80 stocks and max_stocks is 10
- **THEN** system selects top min(10, floor(80*0.2)) = 10 stocks by composite score

#### Scenario: Small universe
- **WHEN** universe has 15 stocks and max_stocks is 10
- **THEN** system selects top min(10, floor(15*0.2)) = 3 stocks by composite score

### Requirement: IC-weighted scoring mode
The system SHALL support an alternative IC-weighted mode where factor weights are determined by rolling 12-month Information Coefficient (rank correlation between factor and next-period return). Factors with IC_IR > 0.5 SHALL receive proportionally higher weight.

#### Scenario: Switch to IC-weighted mode
- **WHEN** user enables IC-weighted scoring in configuration
- **THEN** system uses IC-derived weights instead of static weights for the next rebalancing

#### Scenario: Insufficient history for IC calculation
- **WHEN** less than 12 months of history is available
- **THEN** system falls back to static equal-weight mode and logs a warning

### Requirement: Position allocation
The system SHALL allocate target weights to selected stocks proportional to their composite scores, adjusted by the market timing position ratio. Single stock weight SHALL NOT exceed 10%. Single sub-sector weight SHALL NOT exceed 25%.

#### Scenario: Apply single stock cap
- **WHEN** score-based weight for stock "601899" is 15%
- **THEN** system caps it at 10% and redistributes the 5% excess to remaining selected stocks

#### Scenario: Apply sub-sector cap
- **WHEN** 4 selected stocks are all in the copper sub-sector with total weight 35%
- **THEN** system reduces copper sub-sector weight to 25% by lowering weights of the lowest-scoring copper stocks

### Requirement: Trade signal generation
The system SHALL compare target positions against current holdings and generate actionable trade signals: BUY (new position), ADD (increase existing), REDUCE (decrease existing), SELL (close position). The system SHALL estimate transaction costs for each signal.

#### Scenario: Generate buy signal for new stock
- **WHEN** stock "002460" is in target portfolio but not in current holdings
- **THEN** system generates a BUY signal with target weight and estimated cost (stamp tax + commission + slippage)

#### Scenario: Skip trivial rebalance
- **WHEN** target weight differs from current weight by less than 2% for all stocks
- **THEN** system recommends skipping this rebalance to save transaction costs
