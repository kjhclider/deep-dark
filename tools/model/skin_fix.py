"""원본 텍스처의 올리브색 피부를 사람 살색으로 바꾼다. 갑옷(어두운색), 붉은 천, 금속은 건드리지 않는다."""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255.0
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx = im.max(-1); mn = im.min(-1); d = mx - mn + 1e-6
h = np.zeros_like(mx)
m = mx == r; h[m] = ((g - b)[m] / d[m]) % 6
m = mx == g; h[m] = (b - r)[m] / d[m] + 2
m = mx == b; h[m] = (r - g)[m] / d[m] + 4
h *= 60
s = d / (mx + 1e-6)
# 올리브(누런 초록) 피부: 색상 45~85도, 채도 0.25 이상, 밝기 0.2 이상
mask = (h > 45) & (h < 85) & (s > 0.25) & (mx > 0.2)
# 가장자리는 부드럽게
w = np.clip((s - 0.25) / 0.15, 0, 1) * np.clip((mx - 0.2) / 0.1, 0, 1) * mask
L = (0.3 * r + 0.59 * g + 0.11 * b)
skin = np.stack([L * 1.55, L * 1.12, L * 0.86], -1)   # 따뜻한 살색, 밝기는 원래 명암을 따른다
skin = np.clip(skin, 0, 1)
out = im * (1 - w[..., None]) + skin * w[..., None]
Image.fromarray((out * 255).astype(np.uint8)).save(dst, quality=92)
print('pixels changed', int((w > 0.5).sum()))
