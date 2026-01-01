import torch
import cv2
import numpy as np
from model import enhance_net_nopool
import matplotlib.pyplot as plt

# Load model
model = enhance_net_nopool()
model.load_state_dict(torch.load("zero_dce.pth", map_location='cpu'))
model.eval()

# Read image
img = cv2.imread("input.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (512, 512))

# Normalize
img_norm = img / 255.0
img_tensor = torch.from_numpy(img_norm).float()
img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)

# Enhance
with torch.no_grad():
    enhanced_img, _ = model(img_tensor)

# Convert back
enhanced_img = enhanced_img.squeeze(0).permute(1, 2, 0).numpy()
enhanced_img = np.clip(enhanced_img * 255, 0, 255).astype(np.uint8)

# Save
cv2.imwrite("output.jpg", cv2.cvtColor(enhanced_img, cv2.COLOR_RGB2BGR))

# Display
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.title("Original")
plt.imshow(img)
plt.axis("off")

plt.subplot(1,2,2)
plt.title("Enhanced")
plt.imshow(enhanced_img)
plt.axis("off")

plt.show()
