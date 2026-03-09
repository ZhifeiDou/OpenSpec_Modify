## ADDED Requirements

### Requirement: Load Tushare token from environment variable
The system SHALL load the Tushare Pro API token from the environment variable specified in `config/settings.yaml` under `data.tushare_token_env` (default: `TUSHARE_TOKEN`). The system SHALL support loading environment variables from a `.env` file in the project root using `python-dotenv`.

#### Scenario: Token loaded from environment
- **WHEN** `TUSHARE_TOKEN` environment variable is set to a valid token
- **THEN** system initializes Tushare with `ts.pro_api(token)` successfully

#### Scenario: Token loaded from .env file
- **WHEN** `.env` file contains `TUSHARE_TOKEN=abc123` and no system env var is set
- **THEN** system loads the token from `.env` and initializes Tushare successfully

#### Scenario: No token configured
- **WHEN** neither environment variable nor `.env` file provides a token
- **THEN** system raises a clear error: "TUSHARE_TOKEN environment variable not set. Get your token from https://tushare.pro/user/token and set it in .env or as an environment variable."

### Requirement: Token never hardcoded in source
The system SHALL NOT contain any hardcoded API tokens in source code, configuration files tracked by git, or test fixtures. The `.env` file SHALL be listed in `.gitignore`.

#### Scenario: .env.example provided
- **WHEN** a developer clones the repository
- **THEN** a `.env.example` file exists with `TUSHARE_TOKEN=your_token_here` as a template

#### Scenario: .env in gitignore
- **WHEN** `.gitignore` is checked
- **THEN** it contains an entry for `.env`

### Requirement: Token validation on startup
The system SHALL validate the Tushare token by making a lightweight API call (`pro.trade_cal(start_date=today, end_date=today)`) during data pipeline initialization. Invalid tokens SHALL cause an early exit with a descriptive error.

#### Scenario: Valid token
- **WHEN** the token is valid and Tushare responds successfully
- **THEN** system proceeds with data fetching

#### Scenario: Invalid token
- **WHEN** the token is invalid or expired
- **THEN** system exits with error message including instructions to update the token

### Requirement: Configurable token environment variable name
The system SHALL allow the environment variable name for the token to be configured via `data.tushare_token_env` in `config/settings.yaml`, defaulting to `TUSHARE_TOKEN`.

#### Scenario: Custom env var name
- **WHEN** `settings.yaml` contains `data.tushare_token_env: MY_TS_TOKEN`
- **THEN** system reads the token from `MY_TS_TOKEN` environment variable
