"""    
# ---------- 2) 이미지 업로드 & WordImage 등록 ----------
created_images = []
failed_images = []

for idx, up in enumerate(files):
    meta = file_meta[idx] if idx < len(file_meta) else {}
    word_text = meta.get("word")
    tags = meta.get("tags", "")

    if not word_text or word_text not in word_id_map:
        failed_images.append({"index": idx, "reason": "unknown word in file_meta"})
        continue

    if not is_allowed_content_type(up.content_type):
        failed_images.append({"index": idx, "reason": "unsupported content-type"})
        continue

    # 크기 제한
    raw = await up.read()
    if len(raw) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        failed_images.append({"index": idx, "reason": "too large"})
        continue

    word_id = word_id_map[word_text]
    key = build_object_key(user_id=user_id, word_id=word_id, filename=up.filename or "image")

    # 기존 이미지 삭제
    existing_images = db.query(WordImage).filter(
        WordImage.user_id == user_id,
        WordImage.word_id == word_id
    ).all()
    for old in existing_images:
        try:
            if hasattr(old, "object_key") and old.object_key:
                delete_object(old.object_key)  # S3 삭제
        except Exception as e:
            print("S3 delete failed:", e)
        db.delete(old)  # DB 삭제

        # 이후 새 파일 업로드
    try:
        upload_fileobj(io.BytesIO(raw), key, up.content_type or "application/octet-stream")
    except Exception as e:
        failed_images.append({"index": idx, "reason": f"S3 upload failed: {e}"})
        continue

    # presigned 보기 URL (사설 버킷 가정)
    view_url = presign_get_url(key, expires=3600)

    try:
        wi = WordImage(
            user_id=user_id,
            word_id=word_id,
            prompt=tags,
            image_url=view_url,
            object_key=key,
            content_type=up.content_type,
            size_bytes=len(raw),
        )
        db.add(wi)
        db.flush()
        created_images.append({"index": idx, "word": word_text, "image_id": str(wi.id)})
    except Exception as e:
        # DB 실패 → 업로드 롤백
        try:
            delete_object(key)
        except:
            pass
        failed_images.append({"index": idx, "reason": f"DB insert failed: {e}"})
# ---------- 3) 커밋 ----------
"""