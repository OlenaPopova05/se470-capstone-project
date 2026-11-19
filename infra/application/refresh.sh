#!/bin/bash
set -euo pipefail

source /etc/kvstore-deploy.env
mkdir -p /opt/kvstore
aws s3 cp "s3://$ARTIFACT_BUCKET/$ARTIFACT_KEY" /tmp/kvstore.tar.gz
tar -xzf /tmp/kvstore.tar.gz -C /opt/kvstore

if [[ "$MODE" == coordinator ]]; then
  /bin/bash /opt/kvstore/infra/application/bootstrap.sh coordinator
elif [[ "$MODE" == shard ]]; then
  /bin/bash /opt/kvstore/infra/application/bootstrap.sh shard "$SHARD_ID" "$COORDINATOR_URL"
else
  echo "Unknown mode: $MODE" >&2
  exit 2
fi
