# JPKR-Creator 설치 전 사전작업
Python 버전 == 3.11 
(Poetry 사용하지 않고 직접 venv 사용)
```
[python3.11 경로]/python.exe venv .venv
```
### pytorch 설치
- Torch 버전은 가급적 낮게, (espnet 호환성 문제) CUDA 버전은 하드웨어와 일치시킬 것(flash-attn 호환성)
```
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```
### ESPnet 다운로드
- pyproject.toml 이 있는 디렉토리
```
git clone https://github.com/espnet/espnet
cd espnet
pip install -e .
pip install espnet_model_zoo
```
### flash-attn
- pyproject.toml 이 있는 디렉토리
https://github.com/kingbri1/flash-attention/releases
여기서 버전 맞는 걸 찾아서,
##### Windows
아래 경로에 입력하여 다운받기 (아래는 예시)
```
curl -L https://github.com/kingbri1/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu124torch2.6.0cxx11abiFALSE-cp311-cp311-win_amd64.whl -o flash_attn.whl
pip install "flash_attn.whl"
```
##### Linux
```
# 빌드 준비물
pip install update
pip install -U pip setuptools wheel packaging ninja

# 소스 설치 (내 PyTorch/컴파일러로 빌드)
git clone https://github.com/Dao-AILab/flash-attention.git
cd flash-attention
pip install . --no-build-isolation
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
