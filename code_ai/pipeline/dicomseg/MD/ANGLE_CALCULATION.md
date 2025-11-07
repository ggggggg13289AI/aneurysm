# 最佳觀察角度計算說明

## 📐 算法公式

```
角度 = (標註張數的中位數) × 3 - 3
```

## 🎯 函數說明

### `calculate_best_angles(pred_nii_path, mask_index)`

**功能**: 計算特定動脈瘤的最佳 Pitch 和 Yaw 觀察角度

**參數**:
- `pred_nii_path`: Pred.nii.gz 檔案的路徑
- `mask_index`: 動脈瘤編號 (1, 2, 3, ...)

**返回**:
```python
{
    "pitch": 33,  # Pitch 方向角度
    "yaw": 27     # Yaw 方向角度
}
```

## 📂 檔案結構要求

```
patient_root/
├── Image_nii/
│   └── Pred.nii.gz              # 用於定位根目錄
└── Image_reslice/                # 必須存在！
    ├── MIP_Pitch_pred.nii.gz    # Pitch 方向 MIP 預測
    └── MIP_Yaw_pred.nii.gz      # Yaw 方向 MIP 預測
```

## 🔢 計算步驟

### 步驟 1: 讀取 MIP 預測檔案

```python
# 從 Image_nii/Pred.nii.gz 定位到 Image_reslice/
reslice_path = pred_nii_path.parent.parent / "Image_reslice"

# 讀取 MIP 預測
pitch_array = utils.get_array_to_dcm_axcodes("MIP_Pitch_pred.nii.gz")
yaw_array = utils.get_array_to_dcm_axcodes("MIP_Yaw_pred.nii.gz")
```

### 步驟 2: 找出特定動脈瘤的標註張數

```python
# 假設要計算動脈瘤 #1 (mask_index=1)
pitch_slices = np.where(pitch_array == 1)[0]
# 範例結果: [10, 11, 12, 13, 14, 15]

yaw_slices = np.where(yaw_array == 1)[0]
# 範例結果: [8, 9, 10, 11, 12]
```

### 步驟 3: 計算中位數

```python
median_pitch = int(np.median(pitch_slices))  # 12
median_yaw = int(np.median(yaw_slices))      # 10
```

### 步驟 4: 計算角度

```python
pitch_angle = median_pitch * 3 - 3  # 12 * 3 - 3 = 33°
yaw_angle = median_yaw * 3 - 3      # 10 * 3 - 3 = 27°
```

## 💡 完整範例

### 範例 1: 動脈瘤 #1

```
Pitch 方向:
  標註張數: [10, 11, 12, 13, 14, 15]
  中位數: 12
  角度: 12 × 3 - 3 = 33°

Yaw 方向:
  標註張數: [8, 9, 10, 11, 12]
  中位數: 10
  角度: 10 × 3 - 3 = 27°

結果: {"pitch": 33, "yaw": 27}
```

### 範例 2: 動脈瘤 #2

```
Pitch 方向:
  標註張數: [20, 21, 22, 23, 24, 25, 26]
  中位數: 23
  角度: 23 × 3 - 3 = 66°

Yaw 方向:
  標註張數: [15, 16, 17, 18, 19, 20]
  中位數: 17
  角度: 17 × 3 - 3 = 48°

結果: {"pitch": 66, "yaw": 48}
```

## 🔄 在主流程中使用

```python
from code_ai.pipeline.dicomseg.aneurysm_radax import calculate_best_angles
import pathlib

# 預測檔案路徑
pred_nii_path = pathlib.Path("/path/to/Image_nii/Pred.nii.gz")

# 預測資料（來自 Excel）
predictions = [
    {"mask_index": "1", "mask_name": "A1", ...},
    {"mask_index": "2", "mask_name": "A2", ...},
    {"mask_index": "3", "mask_name": "A3", ...},
]

# 計算每顆動脈瘤的角度
angles_list = [
    calculate_best_angles(pred_nii_path, int(pred["mask_index"]))
    for pred in predictions
]

# 結果
# angles_list = [
#     {"pitch": 33, "yaw": 27},   # 動脈瘤 #1
#     {"pitch": 66, "yaw": 48},   # 動脈瘤 #2
#     {"pitch": 54, "yaw": 39},   # 動脈瘤 #3
# ]
```

## 🛡️ 邊界情況處理

### 情況 1: 檔案不存在

```python
# MIP 預測檔案不存在
result = calculate_best_angles(pred_nii_path, 1)
# 返回: {"pitch": 0, "yaw": 0}
```

### 情況 2: 沒有標註

```python
# 該動脈瘤在 MIP 中沒有標註
# np.where(array == mask_index)[0] 返回空陣列 []
result = calculate_best_angles(pred_nii_path, 99)
# 返回: {"pitch": 0, "yaw": 0}
```

### 情況 3: 只有一個張數

```python
# 只有第 5 張有標註
slices = [5]
median = 5
angle = 5 * 3 - 3 = 12°
```

### 情況 4: 讀取錯誤

```python
# 檔案損壞或格式錯誤
# 捕獲異常，返回角度 0
result = calculate_best_angles(bad_file_path, 1)
# 返回: {"pitch": 0, "yaw": 0}
```

## 📊 NIfTI 檔案格式

### 3D 陣列結構

```python
# MIP_Pitch_pred.nii.gz 內容範例
array.shape = (30, 256, 256)  # (張數, 高, 寬)

# 第 0 維是張數索引
array[0]    # 第 0 張
array[10]   # 第 10 張
array[12]   # 第 12 張

# 值的含義
array[12, 100, 150] = 0   # 背景
array[12, 120, 180] = 1   # 動脈瘤 #1
array[15, 90, 200] = 2    # 動脈瘤 #2
```

### 找出標註張數

```python
# 動脈瘤 #1 出現在哪些張數？
pitch_array = load_nifti("MIP_Pitch_pred.nii.gz")
slices_with_mask_1 = np.where(pitch_array == 1)[0]

# 可能結果: [10, 11, 12, 13, 14, 15]
# 表示動脈瘤 #1 在第 10-15 張有標註
```

## 🎨 視覺化理解

```
MIP Pitch 方向（側面觀察）:
張數:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
動脈瘤#1: .  .  .  .  .  .  .  .  .  . 🔴 🔴 🔴 🔴 🔴 🔴  .  .  .  .  .
                                         ↑           ↑
                                        張10        張15
                                    
中位數: (10 + 11 + 12 + 13 + 14 + 15) / 6 = 12.5 → 12
角度: 12 × 3 - 3 = 33°


MIP Yaw 方向（俯視觀察）:
張數:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
動脈瘤#1: .  .  .  .  .  .  .  . 🔴 🔴 🔴 🔴 🔴  .  .  .  .  .  .  .  .
                                    ↑        ↑
                                   張8       張12
                                    
中位數: (8 + 9 + 10 + 11 + 12) / 5 = 10
角度: 10 × 3 - 3 = 27°
```

## ✅ 檢查清單

使用前確認：

- [ ] Image_reslice 目錄存在
- [ ] MIP_Pitch_pred.nii.gz 存在
- [ ] MIP_Yaw_pred.nii.gz 存在
- [ ] NIfTI 檔案包含對應的 mask_index 標註
- [ ] 檔案格式正確且可讀取

## 🔧 除錯技巧

### 檢查標註是否存在

```python
import numpy as np
from code_ai.pipeline.dicomseg import utils

# 讀取檔案
pitch_array = utils.get_array_to_dcm_axcodes("MIP_Pitch_pred.nii.gz")

# 檢查動脈瘤 #1 的標註
mask_1_slices = np.where(pitch_array == 1)[0]
print(f"動脈瘤 #1 標註張數: {mask_1_slices}")
print(f"共 {len(mask_1_slices)} 張")

# 檢查所有標註值
unique_values = np.unique(pitch_array)
print(f"檔案中的所有值: {unique_values}")
```

### 驗證角度計算

```python
# 手動驗證
slices = [10, 11, 12, 13, 14, 15]
median = np.median(slices)
angle = median * 3 - 3

print(f"張數: {slices}")
print(f"中位數: {median}")
print(f"角度: {angle}°")
```

## 📝 注意事項

1. **張數索引從 0 開始**: NumPy 陣列索引從 0 開始
2. **中位數取整**: 使用 `int(np.median())` 取整數
3. **每顆動脈瘤獨立計算**: 不同 mask_index 有不同的角度
4. **預設值為 0**: 任何錯誤都返回角度 0，不拋出異常

## 🔗 相關文件

- `aneurysm_radax.py`: 主要實現
- `calculate_angles_example.py`: 詳細範例
- `utils.py`: `get_array_to_dcm_axcodes()` 函數

---

**實現完成** ✅ 已整合到 RADAX JSON 生成流程中！

