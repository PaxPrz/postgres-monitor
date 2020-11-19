# PostgreSQL Activity Monitor
=============================

Nonitors for:

- Database connections: Total, Active, Idle
- Number of transaction, commits and rollbacks performed


## Usage

1. Configure the .env file

`$ cp postgres_monitor/.env.bak postgres_monitor/.env`

2. Install dependencies from poetry

`$ poetry install`

3. Activate the poetry virtual environment

`$ poetry shell`

4. Run the program

`$ uvicorn postgres_monitor.app:app`
