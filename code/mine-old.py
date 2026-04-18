import cv2
import torch
import clip
from PIL import Image
import numpy as np
import os
from ultralytics import YOLO, SAM
from tqdm import tqdm

# 配置
VIDEO_PATH = os.path.join("video", "input.mp4")
OUTPUT_DIR = os.path.join("output", "results")
DEVICE = "cuda:2"


SCENE_NEG = ["close-up face", "interview", "talking head", "blur background"]
SCENE_POS = ["bus stop", "wooden deck", "pavement with markings", "metal structure", "children playing"]


PROMPTS = {
    "child": ["child", "kid", "toddler", "boy", "girl"],
    "architecture": [
        "rotating puzzle wall",
        "metal wall with spinning blocks",
        "interactive bus stop wall",

        "painted shoe prints on ground",
        "orange footprints on pavement",
        "hopscotch markings",

        "faceted wooden deck",
        "slatted wood platform",
        "tiered wooden seating"
    ]
}


INTERACTION_PROMPTS = {
    "yes": [
        "child spinning the blocks",
        "child touching the puzzle wall",
        "child moving the rotating parts",
        "child jumping on footprints",
        "child hopping on the ground",
        "child climbing on the wooden deck",
        "child playing on the platform"
    ],
    "no": [
        "child walking past a fence",
        "child standing waiting for bus",
        "child walking on sidewalk",
        "child sitting still",
        "no interaction"
    ]
}


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Initializing ogic on {DEVICE}")

    # 加载模型
    model_clip, preprocess = clip.load("ViT-L/14", device=DEVICE)

    def get_text_features(text_list):
        tokens = clip.tokenize(text_list).to(DEVICE)
        with torch.no_grad():
            feats = model_clip.encode_text(tokens)
            feats /= feats.norm(dim=-1, keepdim=True)
        return feats.mean(dim=0, keepdim=True)

    feat_scene_neg = get_text_features(SCENE_NEG)
    feat_scene_pos = get_text_features(SCENE_POS)
    feat_int_yes = get_text_features(INTERACTION_PROMPTS["yes"])
    feat_int_no = get_text_features(INTERACTION_PROMPTS["no"])

    model_yolo = YOLO('yolov8x-worldv2.pt')
    model_yolo.set_classes(PROMPTS["child"] + PROMPTS["architecture"])
    model_yolo.to(DEVICE)

    model_sam = SAM('sam_b.pt')
    model_sam.to(DEVICE)

    cap = cv2.VideoCapture(VIDEO_PATH)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    target_step = int(fps * 0.5)

    print(f"Processing {total_frames} frames")
    pbar = tqdm(total=total_frames, unit="frame")

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_count += 1
        pbar.update(1)

        if frame_count % target_step != 0: continue

        try:
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            clip_input = preprocess(pil_img).unsqueeze(0).to(DEVICE)

            # 场景初筛
            with torch.no_grad():
                img_feat = model_clip.encode_image(clip_input)
                img_feat /= img_feat.norm(dim=-1, keepdim=True)
                score_neg = (img_feat @ feat_scene_neg.T).item()
                score_pos = (img_feat @ feat_scene_pos.T).item()
            if score_neg > score_pos: continue

            # YOLO 原生识别
            results = model_yolo.predict(frame, conf=0.08, verbose=False)
            if not results: continue

            boxes = results[0].boxes.xyxy.cpu().numpy()
            cls_ids = results[0].boxes.cls.cpu().numpy()
            names_dict = results[0].names

            child_boxes = []
            arch_boxes = []

            for i, box in enumerate(boxes):
                name = names_dict[int(cls_ids[i])]
                if name in PROMPTS["child"]:
                    child_boxes.append(box)
                elif name in PROMPTS["architecture"]:
                    arch_boxes.append(box)

            # 互动确认
            if child_boxes and arch_boxes:
                for c_box in child_boxes:
                    for a_box in arch_boxes:
                        # 距离检查
                        ax1, ay1, ax2, ay2 = c_box
                        bx1, by1, bx2, by2 = a_box

                        if (ax1 < bx2 + 100 and ax2 > bx1 - 100 and
                                ay1 < by2 + 100 and ay2 > by1 - 100):

                            # 裁剪局部画面
                            u_x1 = int(min(ax1, bx1))
                            u_y1 = int(min(ay1, by1))
                            u_x2 = int(max(ax2, bx2))
                            u_y2 = int(max(ay2, by2))
                            h, w = frame.shape[:2]
                            pad = 60

                            crop_img = pil_img.crop((
                                max(0, u_x1 - pad), max(0, u_y1 - pad),
                                min(w, u_x2 + pad), min(h, u_y2 + pad)
                            ))

                            crop_input = preprocess(crop_img).unsqueeze(0).to(DEVICE)
                            with torch.no_grad():
                                crop_feat = model_clip.encode_image(crop_input)
                                crop_feat /= crop_feat.norm(dim=-1, keepdim=True)
                                score_interact = (crop_feat @ feat_int_yes.T).item()
                                score_passby = (crop_feat @ feat_int_no.T).item()


                            if score_interact > score_passby * 1.1:

                                # 保存结果
                                c_list = [c_box.tolist()]
                                a_list = [a_box.tolist()]
                                res_c = model_sam(frame, bboxes=c_list, verbose=False)
                                res_a = model_sam(frame, bboxes=a_list, verbose=False)

                                if (len(res_c) > 0 and res_c[0].masks is not None and
                                        len(res_a) > 0 and res_a[0].masks is not None):

                                    # 透明图
                                    mask = res_c[0].masks.data[0].cpu().numpy().astype(bool) | \
                                           res_a[0].masks.data[0].cpu().numpy().astype(bool)
                                    rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                                    rgba[~mask] = [0, 0, 0, 0]
                                    cutout = rgba[max(0, u_y1 - 20):min(h, u_y2 + 20),
                                    max(0, u_x1 - 20):min(w, u_x2 + 20)]

                                    # 原图
                                    vis_frame = frame.copy()
                                    cv2.rectangle(vis_frame, (int(ax1), int(ay1)), (int(ax2), int(ay2)), (255, 0, 0), 2)
                                    cv2.rectangle(vis_frame, (int(bx1), int(by1)), (int(bx2), int(by2)), (0, 255, 255),
                                                  2)
                                    source_crop = vis_frame[max(0, u_y1 - 20):min(h, u_y2 + 20),
                                    max(0, u_x1 - 20):min(w, u_x2 + 20)]

                                    if cutout.size > 0:
                                        # 保存一对
                                        cv2.imwrite(os.path.join(OUTPUT_DIR, f"pair_{saved_count}_A.png"), cutout)
                                        cv2.imwrite(os.path.join(OUTPUT_DIR, f"pair_{saved_count}_B.jpg"), source_crop)
                                        saved_count += 1
        except Exception:
            continue

    pbar.close()
    cap.release()
    print(f"Saved {saved_count} pairs.")


if __name__ == "__main__":
    main()