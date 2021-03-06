#!/bin/bash
set -e -u -o pipefail
cd "$(dirname "$0")"
SYSTEMD_SVC="$HOME/.config/systemd/user"

mkdir -p "$HOME/staging"
mkdir -p "${SYSTEMD_SVC}"

cat >"${SYSTEMD_SVC}/pfaccept.service" <<EOF
[Unit]
Description=Backup Acceptor

[Service]
ExecStart=$PWD/pfaccept.py
StandardInput=null
StandardOutput=journal
StandardError=inherit

[Install]
WantedBy=default.target
EOF

cat >"${SYSTEMD_SVC}/pfaccept.timer" <<EOF
[Unit]
Description=Backup Acceptor Timer

[Timer]
Persistent=false
OnBootSec=5min
OnUnitActiveSec=10min
Unit=pfaccept.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload --user
systemctl enable --user pfaccept.timer
systemctl start --user pfaccept.timer
