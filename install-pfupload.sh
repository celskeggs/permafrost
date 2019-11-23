#!/bin/bash
set -e -u -o pipefail
cd "$(dirname "$0")"
SYSTEMD_SVC="$HOME/.config/systemd/user"

mkdir -p "$HOME/staging"
mkdir -p "${SYSTEMD_SVC}"

cat >"${SYSTEMD_SVC}/pfupload.service" <<EOF
[Unit]
Description=Backup Uploader

[Service]
ExecStart=$PWD/pfupload.py
StandardInput=null
StandardOutput=journal
StandardError=inherit

[Install]
WantedBy=default.target
EOF

cat >"${SYSTEMD_SVC}/pfupload.timer" <<EOF
[Unit]
Description=Backup Uploader Timer

[Timer]
Persistent=false
OnBootSec=5min
OnUnitActiveSec=10min
Unit=pfupload.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload --user
systemctl enable --user pfupload.timer
systemctl start --user pfupload.timer
