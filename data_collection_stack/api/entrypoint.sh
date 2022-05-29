#!/bin/sh

echo "Waiting for postgres..."
until psql postgres://$DB_USER:$DB_PASS@$DB_URL:$DB_PORT/$DB_DBNAME -c '\l'; do
    echo "Postgres is unavailable - sleeping"
    sleep 2
done

echo "Postgres is up - continuing"
exec "$@"