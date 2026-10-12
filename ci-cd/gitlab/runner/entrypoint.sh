#!/bin/bash
set -e

CONFIG_FILE="/etc/gitlab-runner/config.toml"

if [ -f "$CONFIG_FILE" ] && grep -q "token" "$CONFIG_FILE"; then
    echo "[runner] Конфиг найден — запускаем без регистрации."
    exec gitlab-runner run --user=gitlab-runner --working-directory=/home/gitlab-runner
fi

: "${RUNNER_TOKEN:?RUNNER_TOKEN is required}"
: "${GITLAB_URL:=https://gitlab.com/}"
: "${RUNNER_TAGS:=docker}"
: "${RUNNER_DESCRIPTION:=gitlab-runner}"

echo "[runner] Регистрация в $GITLAB_URL (tags: $RUNNER_TAGS)..."

gitlab-runner register \
    --non-interactive \
    --url "$GITLAB_URL" \
    --registration-token "$RUNNER_TOKEN" \
    --executor "docker" \
    --docker-image "docker:27" \
    --description "$RUNNER_DESCRIPTION" \
    --tag-list "$RUNNER_TAGS" \
    --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
    --docker-privileged=false \
    --run-untagged="false" \
    --locked="false"

echo "[runner] Регистрация завершена — запускаем."
exec gitlab-runner run --user=gitlab-runner --working-directory=/home/gitlab-runner
