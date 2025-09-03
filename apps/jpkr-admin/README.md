# ESPnet 다운로드
(pyproject.toml 있는 폴더에서)
git clone https://github.com/espnet/espnet

# ffmpeg
- C:\ 에 ffmpeg 다운로드 받아놓을 것 (https://www.gyan.dev/ffmpeg/builds/)
AudioSegment.converter = which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"

# flash-attn (윈도우즈)
https://github.com/kingbri1/flash-attention/releases
여기서 버전 맞는 걸 다운받은 후,
poetry add "[.whl 파일 경로]"
