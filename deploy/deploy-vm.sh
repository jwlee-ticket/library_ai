#!/bin/bash
# VM에서 실행하는 배포 스크립트
#
# 실행 방법:
#   1. 프로젝트 디렉토리로 이동: cd /var/www/library-ai
#   2. 가상환경 활성화: source venv/bin/activate
#   3. 배포 스크립트 실행: ./deploy/deploy-vm.sh 또는 bash deploy/deploy-vm.sh

set -e  # 에러 발생 시 중단

echo "--------------------------------- 배포 시작 ---------------------------------"

# git pull을 위해 소유권을 현재 사용자로 변경
echo "--------------------------------- git pull을 위해 소유권 변경 중 ---------------------------------"
sudo chown -R $USER:$USER /var/www/library-ai
sleep 2

# Git에서 최신 코드 가져오기
echo "--------------------------------- git pull 실행 ---------------------------------"
git pull
sleep 2

# 의존성 업데이트
echo "--------------------------------- 의존성 설치 실행 ---------------------------------"
pip install -r requirements.txt
sleep 2

# Tailwind CSS 빌드
echo "--------------------------------- Tailwind CSS 빌드 실행 ---------------------------------"
python manage.py tailwind build
sleep 2

# 정적 파일 수집
echo "--------------------------------- 정적 파일 수집 실행 ---------------------------------"
python manage.py collectstatic --noinput
sleep 2

# 데이터베이스 마이그레이션
echo "--------------------------------- 데이터베이스 마이그레이션 실행 ---------------------------------"
python manage.py migrate
sleep 2

# 소유권을 www-data로 변경 (Gunicorn이 정상 동작하도록)
# venv 디렉토리는 제외 (현재 사용자가 계속 사용해야 함)
echo "--------------------------------- 소유권을 www-data로 변경 ---------------------------------"
sudo chown -R www-data:www-data /var/www/library-ai
sleep 2

# Gunicorn 재시작
echo "--------------------------------- Gunicorn 재시작 ---------------------------------"
sudo systemctl restart library-ai
sleep 2

# 서비스 상태 확인
echo "--------------------------------- 서비스 상태 확인 ---------------------------------"
sudo systemctl status library-ai --no-pager -l
sleep 2

echo "--------------------------------- 배포 완료! ---------------------------------"

