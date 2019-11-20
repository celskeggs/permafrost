#!/bin/bash
set -e -u -o pipefail
cd "$(dirname "$0")"
SYSTEMD_SVC="$HOME/.config/systemd/user"

mkdir -p "${SYSTEMD_SVC}"

cat >"${SYSTEMD_SVC}/pfsave.service" <<EOF
[Unit]
Description=Backup Executor

[Service]
ExecStart=$PWD/pfsave.py

[Install]
WantedBy=default.target
EOF

cat >"${SYSTEMD_SVC}/pfsave.timer" <<EOF
[Unit]
Description=Backup Executor Timer

[Timer]
Persistent=false
OnBootSec=20min
OnUnitActiveSec=1h
Unit=pfsave.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload --user
systemctl enable --user pfsave.timer
systemctl start --user pfsave.timer

