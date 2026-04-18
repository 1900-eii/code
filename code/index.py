import cv2
import torch
import clip
from PIL import Image
import numpy as np
import os
import pickle
from tqdm import tqdm

# 配置
VIDEO_PATH = os.path.join("video", "input.mp4")
OUTPUT_DIR = os.path.join("output", "keyframes")
INDEX_FILE = os.path.join("output", "video_index.pkl")

DEVICE = "cuda:2"
MODEL_TYPE = "ViT-L/14"


def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"File not found: {VIDEO_PATH}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 加载模型
    print(f"Loading CLIP model ({MODEL_TYPE}) on {DEVICE}...")
    try:
        model, preprocess = clip.load(MODEL_TYPE, device=DEVICE)
    except Exception as e:
        print(f"Model load failed: {e}")
        return

    # 读取视频信息
    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps == 0:
        print("Error reading video file.")
        return

    # 数据容器
    data_store = {
        "features": [],
        "metadata": []
    }

    # 采样间隔：每 1 秒一帧
    sample_rate = int(fps * 1)

    print(f"Processing {total_frames} frames. Sample rate: every {sample_rate} frames.")

    # 主循环
    pbar = tqdm(total=total_frames // sample_rate, unit="img")

    for count in range(0, total_frames, sample_rate):
        cap.set(cv2.CAP_PROP_POS_FRAMES, count)
        ret, frame = cap.read()

        if not ret:
            break

        try:
            # 转换颜色 BGRRGB
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image_input = preprocess(image).unsqueeze(0).to(DEVICE)

            # 计算特征
            with torch.no_grad():
                image_features = model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)

            # 保存图片文件
            timestamp = count / fps
            frame_filename = f"frame_{int(timestamp * 1000):06d}.jpg"
            save_path = os.path.join(OUTPUT_DIR, frame_filename)
            image.save(save_path)

            # 保存数据到内存
            data_store["features"].append(image_features.cpu().numpy())
            data_store["metadata"].append({
                "path": save_path,
                "timestamp": timestamp,
                "frame_idx": count
            })

            pbar.update(1)

        except Exception as e:
            print(f"Frame {count} error: {e}")
            continue

    pbar.close()
    cap.release()

    # 保存索引文件
    print(f"Saving index to {INDEX_FILE}...")
    try:
        with open(INDEX_FILE, 'wb') as f:
            pickle.dump(data_store, f)
        print("Indexing complete.")
    except Exception as e:
        print(f"Save failed: {e}")


if __name__ == "__main__":
    main()