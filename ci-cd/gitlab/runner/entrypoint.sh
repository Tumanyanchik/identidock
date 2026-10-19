#!/bin/bash
set -e

CONFIG_FILE="/etc/gitlab-runner/config.toml"

if [ ! -f "$CONFIG_FILE" ] || ! grep -q '^  token' "$CONFIG_FILE"; then
    : "${RUNNER_TOKEN:?RUNNER_TOKEN is required}"
    : "${GITLAB_URL:=http://gitlab:8929/}"
    : "${RUNNER_DESCRIPTION:=gitlab-runner}"

    echo "[runner] Регистрация в $GITLAB_URL..."
    gitlab-runner register \
        --non-interactive \
        --url "$GITLAB_URL" \
        --token "$RUNNER_TOKEN" \
        --executor "docker" \
        --docker-image "docker:27" \
        --description "$RUNNER_DESCRIPTION" \
        --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
        --docker-volumes "/cache" \
        --docker-volumes "/opt/identidock-prod:/opt/identidock-prod" \
        --docker-privileged=false
fi

grep -q 'clone_url' "$CONFIG_FILE" || \
    sed -i '/^\[\[runners\]\]/a\  clone_url = "http://gitlab:8929"' "$CONFIG_FILE"

grep -q 'network_mode' "$CONFIG_FILE" || \
    sed -i '/runners\.docker/a\    network_mode = "gitlab-net"' "$CONFIG_FILE"

echo "[runner] Запускаем."
exec gitlab-runner run --user=gitlab-runner --working-directory=/home/gitlab-runner
