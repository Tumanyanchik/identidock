#!/bin/bash
sudo tee /etc/logrotate.d/docker << 'EOF' > /dev/null
/var/lib/docker/containers/*/*.log {
    daily
    rotate 3
    compress
    delaycompress
    missingok
    copytruncate
}
EOF

sudo mkdir -p /etc/docker

if [ ! -f /etc/docker/daemon.json ]; then
    sudo tee /etc/docker/daemon.json << 'EOF' > /dev/null
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
    sudo systemctl restart docker
fi
