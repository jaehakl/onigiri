# JPKR-Creator 설치 전 사전작업
Python 버전 == 3.11 
```
[python3.11 경로]/python.exe venv .venv (Poetry 사용하지 않고 직접 venv 사용)
```
### pytorch 설치 버전 고정
```
pip install torch==2.6.0 torchvision --index-url https://download.pytorch.org/whl/cu124
```
### ESPnet 다운로드
(pyproject.toml 있는 폴더에서)
```
git clone https://github.com/espnet/espnet
cd espnet
pip install -e .
pip install espnet_model_zoo
```
### flash-attn
https://github.com/kingbri1/flash-attention/releases
여기서 버전 맞는 걸 다운받은 후,
```
pip install "[.whl 파일 경로]"
```
### requirments.txt 로 설치
```
pip install -r requirements.txt (혹시 torch, espnet, flash-attn 관련된 것들이 있으면 미리 삭제할 것)
```
# 설치 후 작업

###fugashi (MeCab) unidic 다운로드
```
python -m unidic download
```
### ffmpeg

##### 윈도우즈
- C:\ 에 ffmpeg 다운로드 받아놓을 것 (https://www.gyan.dev/ffmpeg/builds/)
AudioSegment.converter = which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"

##### 우분투
```
sudo apt install ffmpeg -y
```
