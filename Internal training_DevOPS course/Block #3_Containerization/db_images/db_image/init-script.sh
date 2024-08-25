#!/bin/bash
set -e

cat /postgresql.conf > /var/lib/postgresql/data/postgresql.conf
cat /pg_hba.conf > /var/lib/postgresql/data/pg_hba.conf 

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" $POSTGRES_DB <<-EOSQL
	CREATE USER repl_user WITH REPLICATION PASSWORD 'P@ssw0rd';
	CREATE USER mr_bot WITH PASSWORD 'P@ssw0rd';
	CREATE database shurik_bot OWNER postgres;
EOSQL

psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "shurik_bot" -f /schema.sql