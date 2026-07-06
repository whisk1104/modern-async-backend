#!/bin/bash
echo "Waiting for tables to be created..."
sleep 3

echo "Populating database..."
DEFAULT_HASH="\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGGa31Sg"

for i in {1..50}
do
  docker exec postgres_db psql -U postgres -d training -c \
  "INSERT INTO users (username, email, hashed_password) VALUES ('user$i', 'user$i@example.com', '$DEFAULT_HASH') ON CONFLICT DO NOTHING;"
done
echo "Database populated successfully with 50 rows!"