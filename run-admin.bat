@echo off
REM 백엔드 실행 (새 창)
cd ./apps/jpkr/api
start cmd /k "call creator.bat"
cd ../../..

REM 프론트엔드 실행 (새 창)
cd ./apps/jpkr/_creator-ui   
start cmd /k "call run.bat"
cd ../../..






