import argparse
import os
import sys
import textwrap
from typing import Dict, Any

import yaml
import snowflake.connector


def load_config(path: str) -> Dict[str, Any]:
	with open(path, "r") as f:
		return yaml.safe_load(f)


def connect(cfg: Dict[str, Any]):
	conn = snowflake.connector.connect(
		user=cfg["user"],
		password=cfg["password"],
		account=cfg["account"],
		role=cfg.get("role"),
		warehouse=cfg.get("warehouse"),
	)
	return conn


def ident(name: str) -> str:
	# Return identifier quoted only if needed
	if any(c in name for c in [" ", ".", "-", "/"]):
		return f'"{name}"'
	return name


def split_qualified_name(qualified: str) -> Dict[str, str]:
	# Expect DB.SCHEMA.OBJECT
	parts = qualified.split(".")
	if len(parts) != 3:
		raise ValueError(f"Expected qualified name DB.SCHEMA.OBJECT, got: {qualified}")
	return {"db": parts[0], "schema": parts[1], "object": parts[2]}


def create_search_agent(cur, agent_name: str, service_qualified: str):
	q = split_qualified_name(service_qualified)
	sql = f"""
	CREATE OR REPLACE AGENT {ident(agent_name)}
	USING 'Cortex Search'
	WITH PARAMETERS (
	  'service_name' = '{q['object']}',
	  'database' = '{q['db']}',
	  'schema' = '{q['schema']}'
	);
	"""
	cur.execute(sql)


def create_analyst_agent(cur, agent_name: str, database: str, schema: str, service_name: str):
	sql = f"""
	CREATE OR REPLACE AGENT {ident(agent_name)}
	USING 'Cortex Analyst'
	WITH PARAMETERS (
	  'service_name' = '{service_name}',
	  'database' = '{database}',
	  'schema' = '{schema}'
	);
	"""
	cur.execute(sql)


def ensure_email_objects(cur, cfg: Dict[str, Any]):
	email_cfg = cfg.get("email", {})
	if not email_cfg.get("enabled"):
		return

	integration = email_cfg["notification_integration"]
	recipient = email_cfg["recipient"]
	schedule = email_cfg.get("task_schedule", "USING CRON 0 9 * * * UTC")

	# Stored procedure to send a simple email summary. This is a placeholder; users can
	# customize SQL to gather summaries from Snowflake Intelligence logs/tables.
	proc_sql = textwrap.dedent(
		f"""
		CREATE OR REPLACE PROCEDURE SEND_ANALYSIS_EMAIL()
		RETURNS STRING
		LANGUAGE SQL
		AS
		$$
		BEGIN
		  -- TODO: Replace with real analysis summary generation as needed
		  CALL SYSTEM$SEND_EMAIL(
		    '{integration}',
		    '{recipient}',
		    'Snowflake Intelligence Daily Summary',
		    'Here is your analysis summary for today.'
		  );
		  RETURN 'Email sent';
		END;
		$$;
		"""
	)
	cur.execute(proc_sql)

	task_sql = textwrap.dedent(
		f"""
		CREATE OR REPLACE TASK EMAIL_ANALYSIS_TASK
		WAREHOUSE = {cfg.get('warehouse', 'AUTO')}
		SCHEDULE = '{schedule}'
		AS
		CALL SEND_ANALYSIS_EMAIL();
		"""
	)
	cur.execute(task_sql)


def main():
	parser = argparse.ArgumentParser(description="Create Cortex Agents for Labs 1–3 and email infra.")
	parser.add_argument("--config", required=True, help="Path to agents_config.yaml")
	args = parser.parse_args()

	cfg = load_config(args.config)
	conn = connect(cfg)
	cur = conn.cursor()
	try:
		# Set context if provided
		if cfg.get("warehouse"):
			cur.execute(f"USE WAREHOUSE {ident(cfg['warehouse'])}")

		# Lab 1 search agent
		lab1_service = cfg.get("lab1_search_service")
		if lab1_service:
			create_search_agent(cur, "LAB1_SEARCH_AGENT", lab1_service)

		# Lab 3 search agent
		lab3_service = cfg.get("lab3_search_service")
		if lab3_service:
			create_search_agent(cur, "LAB3_SEARCH_AGENT", lab3_service)

		# Lab 2 analyst agent
		lab2 = cfg.get("lab2_analyst", {})
		if lab2 and lab2.get("database") and lab2.get("schema"):
			service_name = lab2.get("service_name", "LAB2_ANALYST_SERVICE")
			create_analyst_agent(
				cur,
				"LAB2_ANALYST_AGENT",
				lab2["database"],
				lab2["schema"],
				service_name,
			)

		# Optional email proc + task
		ensure_email_objects(cur, cfg)

		conn.commit()
		print("Agents and email objects created successfully.")
	finally:
		cur.close()
		conn.close()


if __name__ == "__main__":
	main()
