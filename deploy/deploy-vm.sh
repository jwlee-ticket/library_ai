#!/bin/bash
# VM에서 실행하는 배포 스크립트
#
# 실행 방법:
#   1. 프로젝트 디렉토리로 이동: cd /var/www/library-ai
#   2. 가상환경 활성화: source venv/bin/activate
#   3. 배포 스크립트 실행: ./deploy/deploy-vm.sh 또는 bash deploy/deploy-vm.sh

set -e  # 에러 발생 시 중단

echo "\n--------------------------------- 배포 시작 ---------------------------------\n"

# git pull을 위해 소유권을 현재 사용자로 변경
echo "\n--------------------------------- git pull을 위해 소유권 변경 중 ---------------------------------\n"
sudo chown -R $USER:$USER /var/www/library-ai
sleep 2

# Git에서 최신 코드 가져오기
echo "\n--------------------------------- git pull 실행 ---------------------------------\n"
git pull origin main
sleep 2

# 의존성 업데이트
echo "\n--------------------------------- 의존성 설치 실행 ---------------------------------\n"
pip install -r requirements.txt
sleep 2

# Tailwind CSS 빌드
echo "\n--------------------------------- Tailwind CSS 빌드 실행 ---------------------------------\n"
python manage.py tailwind build
sleep 2

# 정적 파일 수집
echo "\n--------------------------------- 정적 파일 수집 실행 ---------------------------------\n"
python manage.py collectstatic --noinput
sleep 2

# 데이터베이스 마이그레이션
echo "\n--------------------------------- 데이터베이스 마이그레이션 실행 ---------------------------------\n"
python manage.py migrate
sleep 2

# 소유권을 www-data로 변경 (Gunicorn이 정상 동작하도록)
# venv 디렉토리는 제외 (현재 사용자가 계속 사용해야 함)
echo "\n--------------------------------- 소유권을 www-data로 변경 ---------------------------------\n"
sudo chown -R www-data:www-data /var/www/library-ai
sleep 2

# Gunicorn 재시작
echo "\n--------------------------------- Gunicorn 재시작 ---------------------------------\n"
sudo systemctl restart library-ai
sleep 2

# 서비스 상태 확인
echo "\n--------------------------------- 서비스 상태 확인 ---------------------------------\n"
sudo systemctl status library-ai --no-pager -l
sleep 2

echo "\n--------------------------------- 배포 완료! ---------------------------------\n"

