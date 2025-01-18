#!/usr/bin/env bash
# Description: 멀티 아키텍처 도커 이미지 빌드 및 푸시 스크립트
#   - Git 리포지토리 이름, Poetry 버전, Git SHA(8자리)를 태그로 활용
#   - amd64와 arm64 이미지를 동시 빌드 후 docker push
#   - 기본 DOCKER_USERNAME=cagojeiger, 첫 번째 인자를 받은 경우 해당 값으로 대체
#
# Usage:
#   ./build_and_push.sh [DOCKER_USERNAME]
#
# Requirements:
#   - Docker 19.03 이상 (buildx 지원)
#   - Poetry (버전 파싱용)
#   - git (리포지토리 이름 및 SHA 추출용)
#   - docker login (Docker Hub 로그인)

set -euo pipefail

###############################################################################
# 0) Docker Hub 사용자명 설정
###############################################################################
# 인자가 주어지면 해당 값을, 그렇지 않으면 기본값(cagojeiger)을 사용함
DOCKER_USERNAME="${1:-cagojeiger}"

echo "DOCKER_USERNAME: ${DOCKER_USERNAME}"

###############################################################################
# 1) Git 리포지토리 이름 추출
###############################################################################
REMOTE_URL="$(git config --get remote.origin.url || true)"
if [[ -z "${REMOTE_URL}" ]]; then
  echo "Error: origin 리모트가 설정되지 않았음. Git 리포지토리가 아니거나 remote.origin.url이 없음." 1>&2
  exit 1
fi

STRIPPED="${REMOTE_URL%.git}"          # .git 제거
REPO_NAME="$(basename "${STRIPPED}")"  # 마지막 슬래시 뒤의 이름 추출
if [[ -z "${REPO_NAME}" ]]; then
  echo "Error: 유효한 리포지토리 이름을 찾지 못했음: ${REMOTE_URL}" 1>&2
  exit 1
fi

###############################################################################
# 2) Poetry 버전 추출
###############################################################################
VERSION="$(poetry version -s 2>/dev/null || true)"
if [[ -z "${VERSION}" ]]; then
  echo "Error: Poetry 버전을 추출할 수 없음. Poetry가 설치되지 않았거나 pyproject.toml에 버전이 없음." 1>&2
  exit 1
fi

###############################################################################
# 3) Git SHA(8자리) 추출
###############################################################################
SHORT_SHA="$(git rev-parse --short=8 HEAD 2>/dev/null || true)"
if [[ -z "${SHORT_SHA}" ]]; then
  echo "Error: Git SHA를 추출할 수 없음. Git 리포지토리가 아니거나 커밋이 없음." 1>&2
  exit 1
fi

echo "Poetry 버전: ${VERSION}"
echo "Git 리포지토리 이름: ${REPO_NAME}"
echo "Git SHA(8자리): ${SHORT_SHA}"

###############################################################################
# 4) 멀티 아키텍처 빌드 및 푸시
###############################################################################
#   - ${DOCKER_USERNAME}/${REPO_NAME}:${VERSION}-${SHORT_SHA}
#   - ${DOCKER_USERNAME}/${REPO_NAME}:latest
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "${DOCKER_USERNAME}/${REPO_NAME}:${VERSION}-${SHORT_SHA}" \
  -t "${DOCKER_USERNAME}/${REPO_NAME}:latest" \
  --push \
  .

###############################################################################
# 5) 완료 메시지
###############################################################################
echo "================================================="
echo "멀티 아키텍처 빌드 및 푸시 완료되었음!"
echo "생성된 이미지:"
echo "  ${DOCKER_USERNAME}/${REPO_NAME}:${VERSION}-${SHORT_SHA}"
echo "  ${DOCKER_USERNAME}/${REPO_NAME}:latest"
echo "================================================="