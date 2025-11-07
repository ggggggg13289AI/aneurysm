# Schema 的功用詳解

## 🎯 什麼是 Schema？

Schema 就像是**資料的藍圖**或**合約書**，定義了資料應該長什麼樣子。

## 💡 為什麼需要 Schema？

### ❌ 沒有 Schema 的世界

```python
# 沒人知道這個 dict 應該有什麼
data = {
    "lable": "A1",        # 拼錯了！應該是 label
    "diameter": "3.5",     # 是字串還是數字？
    "prob": 0.87           # 欄位名稱不一致
}

# 處理時充滿不確定性
def process(data):
    label = data['label']      # KeyError! 因為拼成了 'lable'
    size = data['diameter']    # 是 "3.5" 還是 3.5？
    prob = data.get('prob')    # 還是 'probability'？
    # 每次都要猜...
```

**問題:**
- ❌ 不知道有哪些欄位
- ❌ 不知道每個欄位的類型
- ❌ 不知道哪些必填、哪些可選
- ❌ 執行時才發現錯誤
- ❌ 沒有文檔

### ✅ 有 Schema 的世界

```python
from pydantic import BaseModel, Field

class DetectionSchema(BaseModel):
    """動脈瘤檢測結果"""
    label: str = Field(..., description="標籤，如 A1")
    diameter: float = Field(..., description="直徑 (mm)")
    probability: float = Field(..., ge=0.0, le=1.0)
    sub_location: str = Field("", description="次級位置（可選）")

# 使用 Schema
data = {
    "label": "A1",
    "diameter": "3.5",     # 字串會自動轉成 float！
    "probability": 0.87
}

detection = DetectionSchema.model_validate(data)
print(detection.diameter)  # 3.5 (float 類型)
print(detection.label)     # IDE 有自動補全！
```

**優點:**
- ✅ 明確定義資料結構
- ✅ 自動類型驗證與轉換
- ✅ 自帶文檔
- ✅ IDE 支援自動補全
- ✅ 編譯時就能發現問題

## 🔍 Schema 的 6 大功用

### 1. 資料驗證 ✅

```python
# 自動檢查必填欄位
data = {"label": "A1"}  # 缺少 diameter 和 probability

try:
    detection = DetectionSchema.model_validate(data)
except ValidationError as e:
    print("錯誤：缺少必填欄位！")
    # Field required [type=missing, input_value={'label': 'A1'}]
```

### 2. 類型轉換 🔄

```python
# 自動轉換類型
data = {
    "label": "A1",
    "diameter": "3.5",    # 字串 → float
    "probability": "0.87" # 字串 → float
}

detection = DetectionSchema.model_validate(data)
print(type(detection.diameter))  # <class 'float'>
```

### 3. 數值範圍驗證 📊

```python
class DetectionSchema(BaseModel):
    probability: float = Field(..., ge=0.0, le=1.0)  # 必須在 0-1 之間

# 會自動檢查
data = {"probability": 1.5}  # ❌ 超過 1.0，驗證失敗！
```

### 4. 自帶文檔 📚

```python
class RadaxDetection(BaseModel):
    """動脈瘤檢測結果"""
    
    series_instance_uid: str = Field(
        ..., 
        description="DICOM-SEG 的 SeriesInstanceUID"
    )
    diameter: float = Field(
        ..., 
        description="直徑大小 (mm)"
    )
    probability: float = Field(
        ..., 
        description="檢測置信度 (0-1)"
    )

# 其他開發者一看就懂！
```

### 5. JSON 序列化 🔄

```python
# Python 物件 → JSON
detection = DetectionSchema(label="A1", diameter=3.5, probability=0.87)
json_str = detection.model_dump_json()
# {"label":"A1","diameter":3.5,"probability":0.87}

# JSON → Python 物件
restored = DetectionSchema.model_validate_json(json_str)
```

### 6. IDE 支援 💻

```python
detection = DetectionSchema.model_validate(data)

# IDE 知道有哪些屬性，提供自動補全！
detection.label      # ✓ 自動補全
detection.diameter   # ✓ 自動補全
detection.prob       # ✗ IDE 會警告：沒有這個屬性
```

## 🎨 實際案例：RADAX 專案

### 原始 JSON 格式
```json
{
  "label": "A1",
  "diameter": 3.5,
  "probability": 0.87,
  "pitch_angle": 39,
  "sub_location": ""
}
```

### 對應的 Schema

```python
class RadaxDetection(BaseModel):
    """單個動脈瘤檢測結果"""
    
    series_instance_uid: str = Field(..., description="DICOM-SEG SeriesUID")
    sop_instance_uid: str = Field(..., description="DICOM-SEG SOPUID")
    label: str = Field(..., description="標籤 (如 A1, A2)")
    type: str = Field(..., description="類型 (如 saccular)")
    location: str = Field(..., description="位置 (如 ICA, MCA)")
    diameter: float = Field(..., description="直徑 (mm)")
    main_seg_slice: int = Field(..., description="最佳切片編號")
    probability: float = Field(..., description="置信度 (0-1)")
    
    # 可選欄位
    pitch_angle: Optional[int] = Field(None, description="pitch 角度")
    yaw_angle: Optional[int] = Field(None, description="yaw 角度")
    mask_index: int = Field(..., description="Mask 索引")
    sub_location: Optional[str] = Field("", description="次級位置")
```

### 使用效果

```python
# 1. 從 dict 創建（自動驗證）
data = {"label": "A1", "diameter": 3.5, ...}
detection = RadaxDetection.model_validate(data)

# 2. 使用 Builder（更優雅）
detection = (RadaxDetectionBuilder()
    .set_label("A1")
    .set_location("ICA")
    .set_measurements(3.5, 0.87)
    .build()  # ← 這裡會用 Schema 驗證
)

# 3. 轉成 JSON（用於 API 回應）
json_output = detection.model_dump_json()
```

## 📊 有無 Schema 對比

| 項目 | 沒有 Schema | 有 Schema (Pydantic) |
|-----|-----------|---------------------|
| **資料結構** | 不明確，靠猜測 | 明確定義 ✅ |
| **類型檢查** | 執行時才知道 | 建立時就驗證 ✅ |
| **錯誤發現** | 執行時 crash | 創建時就擋下 ✅ |
| **文檔** | 需要另外寫 | 自帶文檔 ✅ |
| **IDE 支援** | 無 | 自動補全 ✅ |
| **維護性** | 低 | 高 ✅ |
| **協作** | 容易誤解 | 清楚明確 ✅ |

## 🔄 Schema 在專案中的流程

```
1. 接收原始資料 (dict/JSON)
   ↓
2. Schema 驗證
   ├─ ✅ 通過 → 創建物件
   └─ ❌ 失敗 → 拋出詳細錯誤訊息
   ↓
3. 使用類型安全的物件
   - IDE 自動補全
   - 不會拼錯欄位名稱
   ↓
4. 輸出 JSON
   - 格式保證正確
   - 符合 API 規範
```

## 💡 實際錯誤範例

### 範例 1: 缺少必填欄位

```python
data = {
    "label": "A1",
    # 缺少 diameter
}

try:
    detection = RadaxDetection.model_validate(data)
except ValidationError as e:
    print(e)
    # Field required [type=missing, input_value={'label': 'A1'}, 
    #                 input_type=dict]
    # For further information visit https://errors.pydantic.dev/...
```

### 範例 2: 類型錯誤

```python
data = {
    "label": "A1",
    "diameter": "not a number",  # 無法轉成 float
    "probability": 0.87
}

try:
    detection = RadaxDetection.model_validate(data)
except ValidationError as e:
    print(e)
    # Input should be a valid number, unable to parse string as a number
```

### 範例 3: 數值超出範圍

```python
class DetectionSchema(BaseModel):
    probability: float = Field(..., ge=0.0, le=1.0)

data = {"probability": 1.5}  # 超過 1.0

try:
    detection = DetectionSchema.model_validate(data)
except ValidationError as e:
    print(e)
    # Input should be less than or equal to 1
```

## 🎯 總結

### Schema 就是：

1. **📋 資料的規格書** - 明確定義資料結構
2. **🛡️ 防護網** - 自動驗證，防止錯誤資料
3. **🔄 轉換器** - 自動類型轉換
4. **📚 活文檔** - 程式碼即文檔
5. **🤝 協作工具** - 團隊成員都知道資料格式
6. **💻 IDE 助手** - 提供自動補全和類型檢查

### 在 RADAX 專案中：

- `aneurysm_radax.py` (主邏輯) 使用 `schema/aneurysm_radax.py` (資料定義)
- 分離關注點：邏輯 vs 資料結構
- 可重用：其他模組也能用同樣的 Schema
- 易維護：修改資料格式只需改 Schema

**一句話總結：Schema 讓資料變得「可預測、可驗證、可維護」！** ✨

