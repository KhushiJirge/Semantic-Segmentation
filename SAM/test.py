import torch
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from transformers import SamModel, SamProcessor

def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def show_masks_on_image(raw_image, masks, scores):
    if len(masks.shape) == 4:
      masks = masks.squeeze()
    if scores.shape[0] == 1:
      scores = scores.squeeze()

    nb_predictions = scores.shape[-1]
    fig, axes = plt.subplots(1, nb_predictions, figsize=(15, 15))

    masks[1] = masks[1].cpu().detach()
    axes[1].imshow(np.array(raw_image))
    show_mask(masks[1], axes[1])
    axes[1].title.set_text(f"Mask {1}, Score: {scores[1].item():.3f}")
    axes[1].axis("off")
    plt.show()

# Step 1: Set device and load the model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SamModel.from_pretrained("facebook/sam-vit-huge").to(device)
processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")

# Step 2: Load the image from a local path
img_path = r"C:\Users\Khushi.Jirge\sem-seg\Custom-dataset-trained\2024-09-20 15.24.png"
raw_image = Image.open(img_path).convert("RGB")  # Load image directly from the file path

# Step 3: Define input points for segmentation (4 points for 4 different regions)
input_points = [[[[555, 1350]], [[1300, 2390]], [[2270, 2285]], [[3170, 2320]]]]  # Example 2D location of points

# Step 4: Preprocess inputs
inputs = processor(raw_image, input_points=input_points, return_tensors="pt").to(device)
image_embeddings = model.get_image_embeddings(inputs["pixel_values"])
inputs["input_points"].shape

inputs.pop("pixel_values", None)
inputs.update({"image_embeddings": image_embeddings})

with torch.no_grad():
    outputs = model(**inputs)

masks = processor.image_processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu())
scores = outputs.iou_scores

scores.shape

show_masks_on_image(raw_image, masks[0][0], scores[:, 0, :])
print(masks[0][0])
