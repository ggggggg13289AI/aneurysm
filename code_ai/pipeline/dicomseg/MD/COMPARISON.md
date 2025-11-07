# aneurysm.py vs aneurysm_radax.py 對比

## 📋 快速對比表

| 特性 | aneurysm.py | aneurysm_radax.py |
|------|------------|------------------|
| **主函數** | `main(_id, path_processID, group_id)` | `main(_id, path_processID, group_id)` ✅ |
| **執行函數** | `execute_dicomseg_platform_json()` | `execute_radax_json_generation()` |
| **輸入目錄** | `root/Dicom`, `root/Image_nii`, etc. | **相同** ✅ |
| **Excel 文件** | `Aneurysm_Pred_list.xlsx` | **相同** ✅ |
| **DICOM-SEG** | 創建 | **創建** ✅ |
| **序列處理** | MRA_BRAIN, MIP_Pitch, MIP_Yaw | **相同** ✅ |
| **輸出格式** | Platform JSON (多層嵌套) | RADAX JSON (扁平) |
| **Schema** | `AneurysmAITeamRequest` | `RadaxAneurysmResponse` |
| **角度計算** | ❌ 無 | ✅ `calculate_best_angles()` |
| **Builder 模式** | ❌ 無 | ✅ `RadaxDetectionBuilder` |

## 🔄 函數簽名對比

### aneurysm.py
```python
def main(
    _id='07807990_20250715_MR_21405290051',
    path_processID=pathlib.Path('...'),
    group_id='54'
):
    execute_dicomseg_platform_json(
        _id=_id,
        root_path=path_processID,
        group_id=group_id
    )
```

### aneurysm_radax.py
```python
def main(
    _id: str = '07807990_20250715_MR_21405290051',
    path_processID: Union[str, pathlib.Path] = pathlib.Path('...'),
    group_id: int = 54
):
    execute_radax_json_generation(
        _id=_id,
        root_path=path_processID,
        group_id=group_id
    )
```

✅ **簽名相同，可以直接替換使用！**

## 📊 輸出格式對比

### aneurysm.py - Platform JSON
```json
{
  "ai_team": {
    "study": {
      "study_instance_uid": "...",
      "group_id": 54,
      "series": [...],
      "model": [...]
    },
    "sorted": {
      "study_instance_uid": "...",
      "series": [...]
    },
    "mask": {
      "study_instance_uid": "...",
      "group_id": 54,
      "series": [
        {
          "series_instance_uid": "...",
          "series_type": "MRA_BRAIN",
          "instances": [
            {
              "mask_index": 1,
              "mask_name": "A1",
              "diameter": "3.5",
              "type": "saccular",
              "location": "ICA",
              "sub_location": "",
              "prob_max": "0.87",
              "checked": "1",
              "is_ai": "1",
              "seg_sop_instance_uid": "...",
              "seg_series_instance_uid": "...",
              "dicom_sop_instance_uid": "...",
              "main_seg_slice": "79",
              "is_main_seg": "1"
            }
          ]
        }
      ]
    }
  }
}
```

### aneurysm_radax.py - RADAX JSON
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
    }
  ]
}
```

## 🆕 新增功能

### 1. 角度計算
```python
# aneurysm.py: ❌ 無此功能

# aneurysm_radax.py: ✅ 自動計算
angles = calculate_best_angles(pred_nii_path, mask_index=1)
# 返回: {"pitch": 33, "yaw": 27}
```

### 2. Builder 模式
```python
# aneurysm.py: ❌ 手動建構 dict

# aneurysm_radax.py: ✅ 使用 Builder
detection = (RadaxDetectionBuilder()
    .set_series_uid("...")
    .set_label("A1")
    .set_measurements(3.5, 0.87)
    .set_angles(33, 27)
    .build()
)
```

### 3. 類型提示
```python
# aneurysm.py: 部分類型提示

# aneurysm_radax.py: ✅ 完整類型提示
def execute_radax_json_generation(
    _id: str,
    root_path: Union[str, pathlib.Path],
    group_id: int = 51,
    model_version: str = "aneurysm_v1"
) -> Optional[str]:
    ...
```

## 🔧 共用函數

這些函數在兩個文件中**完全相同**：

### 1. use_create_dicom_seg_file()
```python
# 創建 DICOM-SEG 文件
# 參數和返回值相同
```

### 2. get_excel_to_pred_json()
```python
# 從 Excel 載入預測資料
# 參數和返回值相同
```

## 🚀 使用方式

### 替換使用（相同接口）
```python
# 原本使用 aneurysm.py
from code_ai.pipeline.dicomseg.aneurysm import main
main(_id='xxx', path_processID='/path', group_id=54)

# 改用 aneurysm_radax.py（完全相同！）
from code_ai.pipeline.dicomseg.aneurysm_radax import main
main(_id='xxx', path_processID='/path', group_id=54)
```

### 指定模型版本（新功能）
```python
from code_ai.pipeline.dicomseg.aneurysm_radax import execute_radax_json_generation

execute_radax_json_generation(
    _id='xxx',
    root_path='/path',
    group_id=54,
    model_version='aneurysm_v2'  # 新參數
)
```

## 📂 目錄結構（完全相同）

```
root_path/
├── Dicom/
│   ├── MRA_BRAIN/              ← 必須
│   ├── MIP_Pitch/              ← 可選
│   ├── MIP_Yaw/                ← 可選
│   └── Dicom-Seg/              ← 輸出
├── Image_nii/
│   └── Pred.nii.gz             ← 必須
├── Image_reslice/
│   ├── MIP_Pitch_pred.nii.gz  ← 角度計算用
│   └── MIP_Yaw_pred.nii.gz    ← 角度計算用
├── excel/
│   └── Aneurysm_Pred_list.xlsx ← 必須
└── JSON/                        ← 輸出
    ├── xxx_platform_json.json  ← aneurysm.py 輸出
    └── xxx_radax_aneurysm.json ← aneurysm_radax.py 輸出
```

## ✅ 重構成果

### 保留的特性
- ✅ 相同的函數簽名和參數
- ✅ 相同的目錄結構要求
- ✅ 相同的 Excel 格式要求
- ✅ 創建 DICOM-SEG 文件
- ✅ 處理三個序列（MRA_BRAIN, MIP_Pitch, MIP_Yaw）
- ✅ 完整的錯誤處理

### 新增的特性
- ✅ RADAX JSON 格式輸出
- ✅ 角度計算（pitch, yaw）
- ✅ Builder 模式
- ✅ 完整的類型提示
- ✅ Pydantic 資料驗證
- ✅ 更清晰的程式碼結構

### 改進的特性
- ✅ 扁平化的 JSON 格式（更易讀）
- ✅ 自動類型轉換（字串 → 數字）
- ✅ 更好的錯誤訊息
- ✅ 模型版本控制

## 🎯 使用建議

### 何時使用 aneurysm.py
- 需要 Platform JSON 格式
- 現有系統依賴該格式
- 不需要角度資訊

### 何時使用 aneurysm_radax.py
- 需要 RADAX JSON 格式
- 需要 pitch/yaw 角度資訊
- 希望有類型驗證
- 偏好扁平化的 JSON 結構

## 🔄 遷移指南

### 從 aneurysm.py 遷移到 aneurysm_radax.py

**步驟 1: 更改 import**
```python
# 原本
from code_ai.pipeline.dicomseg.aneurysm import main

# 改成
from code_ai.pipeline.dicomseg.aneurysm_radax import main
```

**步驟 2: 確認目錄結構**
- 確保 `Image_reslice/` 目錄存在（角度計算需要）
- 確保 `MIP_Pitch_pred.nii.gz` 和 `MIP_Yaw_pred.nii.gz` 存在

**步驟 3: 執行**
```python
main(_id='xxx', path_processID='/path', group_id=54)
```

**就這麼簡單！** ✅

---

**總結：aneurysm_radax.py 完全相容於 aneurysm.py 的接口，但提供更現代化的輸出格式和額外功能！**

