#!/bin/bash

# PLEASE RUN THIS SCRIPT WITH:
# make postgres_restore_latest_backup

# shellcheck source=/dev/null
source .env

if [ -z "$PATH_TO_ITOU_BACKUPS" ]; then
  echo "please add 'PATH_TO_ITOU_BACKUPS=/your/itou-backups/root/directory' in .env at the root of the project in order to run this script"
  exit
fi

# Download last available backup, provided you already ran `make build` once.
echo "Downloading last available backup..."
( cd "$PATH_TO_ITOU_BACKUPS" && make download )
echo "Download is over."

# Get the latest backup filename and path
ITOU_DB_BACKUP_PATH=$(find "$PATH_TO_ITOU_BACKUPS"/backups/* | sort | tail -n1)
ITOU_DB_BACKUP_NAME=$(basename "$ITOU_DB_BACKUP_PATH")

echo "Going to inject ITOU_DB_BACKUP_PATH=$ITOU_DB_BACKUP_PATH"

docker cp "$ITOU_DB_BACKUP_PATH" itou_postgres:/backups && docker compose down && make postgres_backup_restore FILE="$ITOU_DB_BACKUP_NAME"; echo "Ignore warnings above."

cat << EOF

Import is over. Now you need to:
 - restart your container: make run
 - make mgmt_cmd COMMAND=set_fake_passwords
EOF
