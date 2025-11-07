# RADAX 重構說明

## ✅ 已完成重構

`aneurysm_radax.py` 已重構為遵循 `aneurysm.py` 的架構，但輸出 RADAX JSON 格式。

## 🎯 重構目標

1. ✅ **相同的 input/output 結構** - 與 aneurysm.py 一致
2. ✅ **相同的函數簽名** - main() 和 execute 函數相同
3. ✅ **保留 RADAX schema** - 使用 RadaxAneurysmResponse
4. ✅ **保留 calculate_best_angles** - 角度計算功能
5. ✅ **遵循 Linus 風格** - 扁平、Early Return

## 📊 架構對比

### aneurysm.py (原始)
```
主函數簽名：
  main(_id, path_processID, group_id)
  
輸出：
  Platform JSON (多層嵌套結構)
  {
    "ai_team": {
      "study": {...},
      "sorted": {...},
      "mask": {...}
    }
  }
```

### aneurysm_radax.py (重構後)
```
主函數簽名：
  main(_id, path_processID, group_id)  ✅ 相同！
  
輸出：
  RADAX JSON (扁平結構)
  {
    "inference_timestamp": "...",
    "patient_id": "...",
    "study_instance_uid": "...",
    "series_instance_uid": "...",
    "model_id": "...",
    "detections": [...]
  }
```

## 🔄 共用函數

### 1. use_create_dicom_seg_file()
```python
# 與 aneurysm.py 相同
def use_create_dicom_seg_file(
    path_nii, series_name, output_folder,
    image, first_dcm, source_images
) -> List[Dict]:
    # 創建 DICOM-SEG 文件
    # 返回結果列表
```

### 2. get_excel_to_pred_json()
```python
# 與 aneurysm.py 相同
def get_excel_to_pred_json(
    excel_file_path: str,
    input_list: List[Dict]
) -> List[Dict]:
    # 從 Excel 載入預測資料
```

### 3. calculate_best_angles() 
```python
# 新增功能，RADAX 專用
def calculate_best_angles(
    pred_nii_path: pathlib.Path,
    mask_index: int
) -> Dict[str, int]:
    # 計算 pitch 和 yaw 角度
    # 只看 z 軸有沒有標註
```

## 🆕 新函數

### build_radax_json()
```python
def build_radax_json(
    source_images,
    result_list,
    pred_json_list,
    pred_nii_path,
    model_version
) -> RadaxAneurysmResponse:
    """
    建構 RADAX JSON 回應
    
    功能：
    1. 從 DICOM 提取基本資訊
    2. 創建 RadaxAneurysmResponse
    3. 處理每個序列的檢測結果
    4. 計算最佳觀察角度
    5. 建構 RadaxDetection 物件
    """
```

## 📂 檔案結構要求

### 與 aneurysm.py 相同

```
root_path/
├── Dicom/
│   ├── MRA_BRAIN/              # 必須存在
│   ├── MIP_Pitch/              # 可選
│   ├── MIP_Yaw/                # 可選
│   └── Dicom-Seg/              # 輸出目錄
├── Image_nii/
│   └── Pred.nii.gz             # MRA_BRAIN 預測
├── Image_reslice/
│   ├── MIP_Pitch_pred.nii.gz  # MIP Pitch 預測
│   └── MIP_Yaw_pred.nii.gz    # MIP Yaw 預測
├── excel/
│   └── Aneurysm_Pred_list.xlsx # 預測資料
└── JSON/                        # 輸出目錄
    └── {_id}_radax_aneurysm.json
```

## 🔄 執行流程

### 步驟 1: 初始化路徑
```python
path_root = pathlib.Path(root_path)
path_dcms = path_root / "Dicom"
path_nii = path_root / "Image_nii"
path_reslice_nii = path_root / "Image_reslice"
```

### 步驟 2: 載入預測資料
```python
# 從 Excel 載入
pred_json_list = get_excel_to_pred_json(
    excel_file_path=str(excel_path),
    input_list=pred_nii_path_list
)
```

### 步驟 3: 處理每個序列
```python
# MRA_BRAIN (必須)
mra_brain_result_list = use_create_dicom_seg_file(...)

# MIP_Pitch (可選)
if mip_pitch_path_dcms.exists():
    mip_pitch_result_list = use_create_dicom_seg_file(...)

# MIP_Yaw (可選)
if mip_yaw_path_dcms.exists():
    mip_yaw_result_list = use_create_dicom_seg_file(...)
```

### 步驟 4: 建構 RADAX JSON
```python
radax_response = build_radax_json(
    source_images=mra_brain_source_images,
    result_list=result_list,
    pred_json_list=pred_json_list,
    pred_nii_path=path_nii / "Pred.nii.gz",
    model_version="aneurysm_v1"
)
```

### 步驟 5: 保存 JSON
```python
output_path = path_root / "JSON" / f"{_id}_radax_aneurysm.json"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(radax_response.to_json())
```

## 💡 關鍵改進

### 1. 角度計算整合
```python
# 在 build_radax_json() 中自動計算
if series_name == "MRA_BRAIN":
    angles = calculate_best_angles(pred_nii_path, int(mask_index))
else:
    angles = {"pitch": 0, "yaw": 0}

# 設置到 detection
.set_angles(angles.get("pitch"), angles.get("yaw"))
```

### 2. 多序列支援
```python
# 處理所有序列的結果
for series_idx, series_result in enumerate(result_list):
    series_name = series_result["series_name"]
    # MRA_BRAIN, MIP_Pitch, MIP_Yaw
    ...
```

### 3. 錯誤處理
```python
# Early return 模式
if not mra_brain_path_dcms.exists():
    print(f"錯誤：找不到 MRA_BRAIN 目錄")
    return None

# Try-except 包裝
try:
    _, image, first_dcm, source_images = utils.load_and_sort_dicom_files(...)
except Exception as e:
    print(f"錯誤：載入 DICOM 失敗: {e}")
    return None
```

## 📝 使用方式

### 方式 1: 直接調用 main()
```python
from code_ai.pipeline.dicomseg.aneurysm_radax import main

main(
    _id='07807990_20250715_MR_21405290051',
    path_processID='/path/to/process/dir',
    group_id=54  # 保留參數，RADAX 不使用
)
```

### 方式 2: 調用 execute 函數
```python
from code_ai.pipeline.dicomseg.aneurysm_radax import execute_radax_json_generation

result = execute_radax_json_generation(
    _id='07807990_20250715_MR_21405290051',
    root_path='/path/to/process/dir',
    group_id=54,
    model_version='aneurysm_v1'
)

if result:
    print(f"成功: {result}")
```

### 方式 3: 命令行（與 aneurysm.py 相同）
```bash
python code_ai/pipeline/dicomseg/aneurysm_radax.py
```

## 🔍 輸出範例

### RADAX JSON 格式
```json
{
  "inference_timestamp": "2025-01-17T12:34:56.789Z",
  "patient_id": "07807990",
  "study_instance_uid": "1.2.840.113820...",
  "series_instance_uid": "1.2.840.113619...",
  "model_id": "924d1538-597c-41d6-bc27-4b0b359111cf",
  "detections": [
    {
      "series_instance_uid": "1.2.826.0.1.3680043...",
      "sop_instance_uid": "1.2.840.113619...",
      "label": "A1",
      "type": "saccular",
      "location": "ICA",
      "diameter": 3.5,
      "main_seg_slice": 79,
      "probability": 0.87,
      "pitch_angle": 33,
      "yaw_angle": 27,
      "mask_index": 1,
      "sub_location": ""
    },
    {
      "series_instance_uid": "1.2.826.0.1.3680043...",
      "sop_instance_uid": "1.2.840.113619...",
      "label": "A2",
      "type": "saccular",
      "location": "MCA",
      "diameter": 2.8,
      "main_seg_slice": 85,
      "probability": 0.92,
      "pitch_angle": 66,
      "yaw_angle": 48,
      "mask_index": 2,
      "sub_location": "M1"
    }
  ]
}
```

## ⚙️ 配置

### 模型 ID 配置
```python
MODEL_ID_MAP = {
    "aneurysm_v1": "924d1538-597c-41d6-bc27-4b0b359111cf",
    "aneurysm_v2": "另一個-UUID",
}
```

### 修改模型 ID
```python
# 方式 1: 修改 MODEL_ID_MAP
MODEL_ID_MAP["aneurysm_v1"] = "新的-UUID"

# 方式 2: 傳入 model_version
execute_radax_json_generation(
    _id="...",
    root_path="...",
    model_version="aneurysm_v2"  # 使用 v2
)
```

## 📊 與 aneurysm.py 對比

| 項目 | aneurysm.py | aneurysm_radax.py |
|-----|------------|------------------|
| **函數簽名** | `main(_id, path, group_id)` | `main(_id, path, group_id)` ✅ 相同 |
| **輸入結構** | 相同目錄結構 | 相同目錄結構 ✅ |
| **處理流程** | 載入 → 創建 DICOM-SEG → JSON | 載入 → 創建 DICOM-SEG → JSON ✅ |
| **DICOM-SEG** | 創建 | 創建 ✅ |
| **輸出格式** | Platform JSON | RADAX JSON |
| **角度計算** | ❌ 無 | ✅ 有 (calculate_best_angles) |
| **Schema** | AneurysmAITeamRequest | RadaxAneurysmResponse |
| **Linting** | 通過 | 通過 ✅ |

## ✅ 重構完成清單

- [x] 保持相同的函數簽名
- [x] 保持相同的 input 結構
- [x] 使用 RADAX schema
- [x] 保留 calculate_best_angles
- [x] 遵循 Linus 風格
- [x] 通過 linting 檢查
- [x] 支援多序列處理
- [x] 完整的錯誤處理
- [x] 詳細的註釋和文檔

## 🔗 相關文件

- `aneurysm.py` - 原始架構參考
- `schema/aneurysm_radax.py` - RADAX 資料模型
- `RADAX_README.md` - RADAX 使用說明
- `ANGLE_CALCULATION.md` - 角度計算說明
- `Z_AXIS_FIX.md` - Z 軸修正說明

---

**總結：aneurysm_radax.py 現在與 aneurysm.py 具有相同的架構和接口，但輸出 RADAX JSON 格式，並包含角度計算功能！** ✅

