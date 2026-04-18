import cv2
import torch
import clip
from PIL import Image
import numpy as np
import os
from ultralytics import YOLO, SAM
from tqdm import tqdm

VIDEO_PATH = os.path.join("video", "input.mp4")
OUTPUT_DIR = os.path.join("output", "final_results")  # 最终结果文件夹
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

# 设计语言分类
TAXONOMY_COLORS = {
    "person_child": (0, 0, 255),  # 红
    "playable_surface": (0, 140, 255),  # 橙
    "sloped_platform": (42, 42, 165),  # 棕
    "edge_condition": (255, 255, 0),  # 青
    "undefined": (200, 200, 200)
}


def get_taxonomy_label(raw_name):
    raw = raw_name.lower()

    # Child
    if "child" in raw or "kid" in raw or "boy" in raw or "girl" in raw:
        return "person_child"

    # Edge Condition
    if "puzzle" in raw or "spinning" in raw or "interactive" in raw or "metal" in raw:
        return "edge_condition"

    # Playable Surface
    if "print" in raw or "foot" in raw or "hopscotch" in raw:
        return "playable_surface"

    # Sloped Platform
    if "deck" in raw or "wood" in raw or "platform" in raw or "seat" in raw:
        return "sloped_platform"

    return "undefined"


def apply_mask_overlay(img, mask, color, alpha=0.5):
    overlay = img.copy()
    overlay[mask] = color
    return np.where(mask[..., None], cv2.addWeighted(img, 1 - alpha, overlay, alpha, 0), img)


def draw_design_label(img, box, label, color):
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    text_w, text_h = text_size
    cv2.rectangle(img, (x1, y1 - 25), (x1 + text_w + 10, y1), color, -1)
    cv2.putText(img, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    return img


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Initializing logic on {DEVICE}")

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

    print(f"Processing {total_frames} frames...")
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

            # 场景过滤
            with torch.no_grad():
                img_feat = model_clip.encode_image(clip_input)
                img_feat /= img_feat.norm(dim=-1, keepdim=True)
                if (img_feat @ feat_scene_neg.T).item() > (img_feat @ feat_scene_pos.T).item():
                    continue

            # YOLO 检测
            results = model_yolo.predict(frame, conf=0.08, verbose=False)
            if not results: continue

            boxes = results[0].boxes.xyxy.cpu().numpy()
            cls_ids = results[0].boxes.cls.cpu().numpy()
            names_dict = results[0].names

            child_boxes = []
            arch_boxes = []

            for i, box in enumerate(boxes):
                raw_name = names_dict[int(cls_ids[i])]
                label = get_taxonomy_label(raw_name)  # 映射到设计标签
                if label == "person_child":
                    child_boxes.append((box, label))
                elif label != "undefined":
                    arch_boxes.append((box, label))

            # 互动确认
            if child_boxes and arch_boxes:
                for (c_box, c_label) in child_boxes:
                    for (a_box, a_label) in arch_boxes:
                        ax1, ay1, ax2, ay2 = c_box
                        bx1, by1, bx2, by2 = a_box

                        if (ax1 < bx2 + 100 and ax2 > bx1 - 100 and
                                ay1 < by2 + 100 and ay2 > by1 - 100):

                            # CLIP 判定
                            u_x1, u_y1 = int(min(ax1, bx1)), int(min(ay1, by1))
                            u_x2, u_y2 = int(max(ax2, bx2)), int(max(ay2, by2))
                            h, w = frame.shape[:2]
                            pad = 60
                            crop_img = pil_img.crop(
                                (max(0, u_x1 - pad), max(0, u_y1 - pad), min(w, u_x2 + pad), min(h, u_y2 + pad)))

                            crop_input = preprocess(crop_img).unsqueeze(0).to(DEVICE)
                            with torch.no_grad():
                                crop_feat = model_clip.encode_image(crop_input)
                                crop_feat /= crop_feat.norm(dim=-1, keepdim=True)
                                score = (crop_feat @ feat_int_yes.T).item()
                                score_no = (crop_feat @ feat_int_no.T).item()

                            if score > score_no * 1.05:
                                # SAM 分割
                                c_list = [c_box.tolist()];
                                a_list = [a_box.tolist()]
                                res_c = model_sam(frame, bboxes=c_list, verbose=False)
                                res_a = model_sam(frame, bboxes=a_list, verbose=False)

                                if (len(res_c) > 0 and res_c[0].masks is not None and
                                        len(res_a) > 0 and res_a[0].masks is not None):

                                    # 准备数据
                                    mask_c = res_c[0].masks.data[0].cpu().numpy().astype(bool)
                                    mask_a = res_a[0].masks.data[0].cpu().numpy().astype(bool)

                                    c_color = TAXONOMY_COLORS[c_label]
                                    a_color = TAXONOMY_COLORS[a_label]

                                    # 裁剪区域
                                    cy1, cy2 = max(0, u_y1 - 30), min(h, u_y2 + 30)
                                    cx1, cx2 = max(0, u_x1 - 30), min(w, u_x2 + 30)


                                    # 透明图
                                    rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
                                    rgba[~(mask_c | mask_a)] = [0, 0, 0, 0]
                                    img_cutout = rgba[cy1:cy2, cx1:cx2]

                                    # 带框原图
                                    vis_box = frame.copy()
                                    vis_box = draw_design_label(vis_box, c_box, c_label, c_color)
                                    vis_box = draw_design_label(vis_box, a_box, a_label, a_color)
                                    img_source_box = vis_box[cy1:cy2, cx1:cx2]

                                    # 纯净裁剪图
                                    img_raw = frame[cy1:cy2, cx1:cx2]

                                    # 上色分析图
                                    vis_analysis = frame.copy()
                                    vis_analysis = apply_mask_overlay(vis_analysis, mask_a, a_color, alpha=0.5)
                                    vis_analysis = apply_mask_overlay(vis_analysis, mask_c, c_color, alpha=0.3)
                                    vis_analysis = draw_design_label(vis_analysis, c_box, c_label, c_color)
                                    vis_analysis = draw_design_label(vis_analysis, a_box, a_label, a_color)
                                    img_analysis = vis_analysis[cy1:cy2, cx1:cx2]

                                    if img_cutout.size > 0:
                                        base_name = f"{a_label}_{frame_count:05d}"

                                        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{base_name}_A_cutout.png"), img_cutout)
                                        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{base_name}_B_source_box.jpg"),
                                                    img_source_box)
                                        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{base_name}_C_raw_crop.jpg"), img_raw)
                                        cv2.imwrite(os.path.join(OUTPUT_DIR, f"{base_name}_D_analysis.jpg"),
                                                    img_analysis)

                                        saved_count += 1
        except Exception:
            continue

    pbar.close()
    cap.release()
    print(f"Saved {saved_count} sets to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()