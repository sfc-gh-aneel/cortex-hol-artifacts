## Lab 4 - Agents

Create Snowflake Cortex Agents for existing services from Labs 1–3 and configure an email agent for Snowflake Intelligence summaries.

### Files
- `agents_config.yaml` — configuration for account, warehouse, and service names
- `create_agents.py` — script to create agents and optional email infra
- `requirements.txt` — Python dependencies

### Configure
Edit `agents_config.yaml` with your Snowflake account, credentials, and service names.

### Setup
```bash
cd Cortex-hol-artifacts/Lab 4 - Agents
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

### Run
```bash
python create_agents.py --config agents_config.yaml
```

Creates:
- `LAB1_SEARCH_AGENT` for Lab 1 search service
- `LAB2_ANALYST_AGENT` for Lab 2 Cortex Analyst
- `LAB3_SEARCH_AGENT` for Lab 3 search service
- Optional: `SEND_ANALYSIS_EMAIL` procedure and `EMAIL_ANALYSIS_TASK` if enabled in config
