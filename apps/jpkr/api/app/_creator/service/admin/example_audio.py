from espnet2.bin.tts_inference import Text2Speech
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.utils import which
import os

AudioSegment.converter = which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"
import io, uuid
import soundfile as sf
import warnings
from utils.aws_s3 import (
    is_allowed_content_type, build_object_key, upload_fileobj,
    presign_get_url, delete_object
)
# 특정 warning만 무시
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="torch.nn.utils.weight_norm"
)

def generate_audio(text: str):
    # 사전학습 모델 불러오기 (일본어 VITS 모델 예시)
    if not hasattr(generate_audio, "tts"):
        print("Initializing TTS Model")
        model_id = "kan-bayashi/jsut_vits_accent_with_pause"
        generate_audio.tts = Text2Speech.from_pretrained(model_id)

    speech = generate_audio.tts(text)["wav"]

    buf_wav = io.BytesIO()
    sf.write(buf_wav, speech.numpy(), generate_audio.tts.fs, format="WAV")
    buf_wav.seek(0)

    # 2) pydub로 WAV->MP3 인코딩 (192kbps 등 적당히 조절)
    mp3_buf = io.BytesIO()
    AudioSegment.from_file(buf_wav, format="wav").export(mp3_buf, format="mp3", bitrate="192k")
    mp3_buf.seek(0)

    return mp3_buf


from typing import List, Dict, Any
from sqlalchemy.orm import Session
from db import Example

def gen_example_audio(
    example_ids: List[int],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()
    inserted_keys = []
    try:
        for i, example in enumerate(examples):
            mp3_buf = generate_audio(example.jp_text)

            key = "onigiri/example_audio/" + uuid.uuid4().hex + ".mp3"

            try:
                upload_fileobj(mp3_buf, key, "audio/mpeg")
                inserted_keys.append(key)
            except Exception as e:
                print(f"S3 upload failed: {e}")
                continue

            example.audio_object_key = key

            if i % 10 == 9:
                db.commit()
                inserted_keys = []
                print(f"Generated audio for example {i+1}/{len(examples)}")
        db.commit()
        inserted_keys = []
        print(f"Generated audio for example {i+1}/{len(examples)}")
    except Exception as e:
        print(f"Error: {e}")
        for key in inserted_keys:
            try:
                delete_object(key)
            except:
                pass
    return {"message": "Example audio generated successfully"}


