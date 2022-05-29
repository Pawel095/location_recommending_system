#!/bin/bash

echo "Enable plpython3"

psql postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@$localhost:5432/$POSTGRES_DB <<-'EOSQL'
CREATE EXTENSION IF NOT EXISTS plpython3u;
EOSQL