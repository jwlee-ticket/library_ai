#!/bin/bash
# VM에서 실행하는 배포 스크립트
#
# 실행 방법:
#   1. 프로젝트 디렉토리로 이동: cd /var/www/library-ai
#   2. 가상환경 활성화: source venv/bin/activate
#   3. git pull을 먼저 실행한 후
#   4. chmod +x deploy/deploy-vm.sh  (최초 1회만)
#   5. ./deploy/deploy-vm.sh
#   또는
#   bash deploy/deploy-vm.sh

set -e  # 에러 발생 시 중단

echo "배포 시작..."

# 의존성 업데이트
echo "의존성 설치 중..."
pip install -r requirements.txt

# Tailwind CSS 빌드
echo "Tailwind CSS 빌드 중..."
python manage.py tailwind build

# 정적 파일 수집
echo "정적 파일 수집 중..."
python manage.py collectstatic --noinput

# 데이터베이스 마이그레이션
echo "데이터베이스 마이그레이션 실행 중..."
python manage.py migrate

# Gunicorn 재시작
echo "Gunicorn 재시작 중..."
sudo systemctl restart library-ai

# 서비스 상태 확인
echo "서비스 상태 확인 중..."
sudo systemctl status library-ai --no-pager -l

echo "배포 완료!"

