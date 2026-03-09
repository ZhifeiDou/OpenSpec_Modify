## MODIFIED Requirements

### Requirement: Filter by sector classification
The system SHALL filter stocks to include only those classified under the Shenwan (申万) non-ferrous metals sector using Tushare's sector classification or index member API. The system SHALL tag each stock with its sub-sector (copper, aluminum, zinc, tin, nickel, lead, rare earth, tungsten, lithium, cobalt, precious metals, other). The `classifier.py` SHALL instantiate `TushareSource` instead of `AKShareSource`.

#### Scenario: Sector filtering
- **WHEN** user runs `universe update`
- **THEN** only stocks in the Shenwan non-ferrous metals sector (fetched via Tushare) are included in the universe
