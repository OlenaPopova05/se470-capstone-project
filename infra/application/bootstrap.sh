#!/bin/bash
set -euo pipefail

mode=$1
if [[ "$mode" != coordinator && "$mode" != shard ]]; then
  echo 'Expected coordinator or shard mode' >&2
  exit 2
fi

# The private subnets can reach the Amazon Linux repositories through the S3 gateway endpoint.
dnf install -y python3.11 python3.11-pip
python3.11 -m venv /opt/kvstore/.venv
/opt/kvstore/.venv/bin/python -m pip install \
  --no-index --find-links /opt/kvstore/wheels \
  -r /opt/kvstore/requirements.txt

if [[ "$mode" == coordinator ]]; then
  module=kvstore
  cat > /etc/kvstore.env <<'ENV'
HOST=0.0.0.0
PORT=8080
STORAGE_MODE=sharded
ENV
else
  if [[ $# -ne 3 ]]; then
    echo 'Shard mode requires shard ID and Coordinator URL' >&2
    exit 2
  fi
  shard_id=$2
  coordinator_url=$3
  module=kvstore.shard
  token=$(curl -fsS -X PUT \
    -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
    http://169.254.169.254/latest/api/token)
  private_ip=$(curl -fsS \
    -H "X-aws-ec2-metadata-token: $token" \
    http://169.254.169.254/latest/meta-data/local-ipv4)
  cat > /etc/kvstore.env <<ENV
HOST=0.0.0.0
PORT=8081
SHARD_ID=$shard_id
SHARD_ADDRESS=http://$private_ip:8081
COORDINATOR_URL=$coordinator_url
ENV
fi

cat > /etc/systemd/system/kvstore.service <<UNIT
[Unit]
Description=Capstone key-value store
Requires=kvstore-refresh.service
After=network-online.target kvstore-refresh.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/kvstore
EnvironmentFile=/etc/kvstore.env
ExecStart=/opt/kvstore/.venv/bin/python -m $module
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable kvstore.service
