#!/usr/bin/env bash

# 제외할 패턴
EXCLUDES=(
  "*/__pycache__/*"
  "*/.mypy_cache/*"
  "*/.pytest_cache/*"
  "*/.git/*"
  "*.pyc"
  # lock 파일과 해시값 등이 들어있는 파일들 제외
  "poetry.lock"
  "Pipfile.lock"
  "*requirements*.txt" # 필요없다면 제외 가능, 필요하다면 주석처리
)

# 포함할 파일 패턴들
INCLUDES=(
  "*.py"                # Python 소스
  "Dockerfile"          # Docker 빌드 파일
  "docker-compose.yml"  # Docker Compose 파일
  "pyproject.toml"      # Poetry 설정
  "Pipfile"             # Pipenv 설정 파일 (필요 없다면 제외 가능)
  ".gitignore"          # Git 무시 패턴
  ".flake8"             # Flake8 설정
  ".editorconfig"       # 코드 스타일 설정
  "README*"             # README 파일
  "LICENSE*"            # 라이선스 파일
)

# EXCLUDES 배열을 find 인자화
EXCLUDE_ARGS=()
for pattern in "${EXCLUDES[@]}"; do
  EXCLUDE_ARGS+=( -not -path "$pattern" )
done

# INCLUDES 배열 처리: ( -false -o -name "*.py" -o -name "Dockerfile" ... )
NAME_ARGS=( -false )
for pattern in "${INCLUDES[@]}"; do
  NAME_ARGS+=( -o -name "$pattern" )
done

# find 명령 실행
find . "(" "${NAME_ARGS[@]}" ")" "${EXCLUDE_ARGS[@]}" -type f -print0 |
while IFS= read -r -d '' file; do
  echo "===== $file ====="
  cat "$file"
  echo
done