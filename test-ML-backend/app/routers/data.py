from __future__ import annotations

from datetime import date, datetime
from enum import IntEnum
from typing import List, Annotated

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict
from pydantic import UrlConstraints

# ---- URL 타입 (s3://... 과 https://... 허용) ----
S3Url = Annotated[str, UrlConstraints(allowed_schemes=['s3', 'https'])]

# ---- 고정값이면 Enum으로 문서화/타입안전 ----
class SexType(IntEnum):
    male = 1
    female = 2

class StatusType(IntEnum):
    normal = 0
    hold = 1

# ---- 하위 오브젝트 ----
class DeepAging(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_deep_aging: bool = Field(..., alias="isDeepAging")
    seqno: int = Field(..., ge=0)

class Sensory(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    marbling: float = Field(..., ge=0)
    color: float = Field(..., ge=0)
    texture: float = Field(..., ge=0)
    surface_moisture: float = Field(..., ge=0, alias="surfaceMoisture")
    overall: float = Field(..., ge=0)

class HsiImage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    spectral_index: int = Field(..., ge=0, alias="spectralIndex")
    s3_path: S3Url = Field(..., alias="s3Path")

class Hsi(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_refrigerated: bool = Field(..., alias="isRefrigerated")
    filmed_at: datetime = Field(..., alias="filmedAt")
    images: List[HsiImage]

    @field_validator("images")
    @classmethod
    def images_not_empty(cls, v: List[HsiImage]):
        if not v:
            raise ValueError("images must not be empty")
        return v

    @field_validator("images")
    @classmethod
    def spectral_index_unique(cls, v: List[HsiImage]):
        idxs = [img.spectral_index for img in v]
        if len(idxs) != len(set(idxs)):
            raise ValueError("images.spectralIndex must be unique within a meat item")
        return v

# ---- 상위(한 건) ----
class MeatItem(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,   # alias로 들어오는 camelCase를 수용
        use_enum_values=True,    # Enum을 숫자 값으로 직렬화
        from_attributes=True,    # orm_mode 대체
    )

    trace_num: str = Field(..., alias="traceNum", min_length=1)
    species_id: int = Field(..., alias="speciesId", gt=0)
    category_id: int = Field(..., alias="categoryId", gt=0)
    sex_type: SexType = Field(..., alias="sexType")
    grade_num: int = Field(..., alias="gradeNum", ge=0)
    status_type: StatusType = Field(..., alias="statusType")
    butchery_ymd: date = Field(..., alias="butcheryYmd")
    birth_ymd: date = Field(..., alias="birthYmd")
    weight_kg: float = Field(..., alias="weightKg", gt=0)
    deep_aging: DeepAging = Field(..., alias="deepAging")
    sensory: Sensory
    hsi: Hsi

    @model_validator(mode="after")
    def validate_dates(self):
        if self.birth_ymd and self.butchery_ymd and self.birth_ymd > self.butchery_ymd:
            raise ValueError("birthYmd must be on/before butcheryYmd")
        return self

# ---- 배치(여러 건) ----
class MeatBatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: EmailStr = Field(..., alias="userId")
    batch_id: str = Field(..., alias="batchId", min_length=1)
    meats: List[MeatItem] = Field(..., min_items=1)

    @field_validator("meats")
    @classmethod
    def meats_not_empty(cls, v: List[MeatItem]):
        if not v:
            raise ValueError("meats must not be empty")
        return v

    @model_validator(mode="after")
    def validate_trace_unique(self):
        traces = [m.trace_num for m in self.meats]
        if len(traces) != len(set(traces)):
            raise ValueError("traceNum must be unique within the batch")
        return self
    

"""
{
  "userId": "deeplant@example.com",
  "batchId": "2025-08-19-001",
  "meats": [
    {
      "traceNum": "L01709271277001",
      "speciesId": 1,
      "categoryId": 2,
      "sexType": 1,
      "gradeNum": 2,
      "statusType": 0,
      "butcheryYmd": "2025-08-01",
      "birthYmd": "2023-02-10",
      "weightKg": 12.4,
      "deepAging": {
        "isDeepAging": false,
        "seqno": 0
      },
      "sensory": {
        "marbling": 3.5,
        "color": 4.0,
        "texture": 2.8,
        "surfaceMoisture": 1.2,
        "overall": 3.9
      },
      "hsi": {
        "isRefrigerated": false,
        "filmedAt": "2025-08-19T10:00:00Z",
        "images": [
          { "spectralIndex": 0, "s3Path": "s3://bucket/hsi/trace001/430.png" },
          { "spectralIndex": 1, "s3Path": "s3://bucket/hsi/trace001/450.png" },
          { "spectralIndex": 2, "s3Path": "s3://bucket/hsi/trace001/470.png" },
          { "spectralIndex": 3, "s3Path": "s3://bucket/hsi/trace001/490.png" },
          { "spectralIndex": 4, "s3Path": "s3://bucket/hsi/trace001/510.png" },
          { "spectralIndex": 5, "s3Path": "s3://bucket/hsi/trace001/530.png" },
          { "spectralIndex": 6, "s3Path": "s3://bucket/hsi/trace001/550.png" },
          { "spectralIndex": 7, "s3Path": "s3://bucket/hsi/trace001/570.png" },
          { "spectralIndex": 8, "s3Path": "s3://bucket/hsi/trace001/590.png" }
        ]
      }
    },
    {
      "traceNum": "L01709271277002",
      "speciesId": 1,
      "categoryId": 5,
      "sexType": 2,
      "gradeNum": 3,
      "statusType": 1,
      "butcheryYmd": "2025-08-05",
      "birthYmd": "2023-01-20",
      "weightKg": 14.8,
      "deepAging": {
        "isDeepAging": true,
        "seqno": 1
      },
      "sensory": {
        "marbling": 2.9,
        "color": 3.7,
        "texture": 3.2,
        "surfaceMoisture": 1.5,
        "overall": 3.5
      },
      "hsi": {
        "isRefrigerated": true,
        "filmedAt": "2025-08-19T11:00:00Z",
        "images": [
          { "spectralIndex": 0, "s3Path": "s3://bucket/hsi/trace002/430.png" },
          { "spectralIndex": 1, "s3Path": "s3://bucket/hsi/trace002/450.png" },
          { "spectralIndex": 2, "s3Path": "s3://bucket/hsi/trace002/470.png" },
          { "spectralIndex": 3, "s3Path": "s3://bucket/hsi/trace002/490.png" },
          { "spectralIndex": 4, "s3Path": "s3://bucket/hsi/trace002/510.png" },
          { "spectralIndex": 5, "s3Path": "s3://bucket/hsi/trace002/530.png" },
          { "spectralIndex": 6, "s3Path": "s3://bucket/hsi/trace002/550.png" },
          { "spectralIndex": 7, "s3Path": "s3://bucket/hsi/trace002/570.png" },
          { "spectralIndex": 8, "s3Path": "s3://bucket/hsi/trace002/590.png" }
        ]
      }
    },
    {
      "traceNum": "L01709271277003",
      "speciesId": 2,
      "categoryId": 1,
      "sexType": 1,
      "gradeNum": 1,
      "statusType": 0,
      "butcheryYmd": "2025-08-03",
      "birthYmd": "2022-12-25",
      "weightKg": 11.6,
      "deepAging": {
        "isDeepAging": false,
        "seqno": 0
      },
      "sensory": {
        "marbling": 4.1,
        "color": 3.8,
        "texture": 3.0,
        "surfaceMoisture": 1.0,
        "overall": 4.2
      },
      "hsi": {
        "isRefrigerated": false,
        "filmedAt": "2025-08-19T12:00:00Z",
        "images": [
          { "spectralIndex": 0, "s3Path": "s3://bucket/hsi/trace003/430.png" },
          { "spectralIndex": 1, "s3Path": "s3://bucket/hsi/trace003/450.png" },
          { "spectralIndex": 2, "s3Path": "s3://bucket/hsi/trace003/470.png" },
          { "spectralIndex": 3, "s3Path": "s3://bucket/hsi/trace003/490.png" },
          { "spectralIndex": 4, "s3Path": "s3://bucket/hsi/trace003/510.png" },
          { "spectralIndex": 5, "s3Path": "s3://bucket/hsi/trace003/530.png" },
          { "spectralIndex": 6, "s3Path": "s3://bucket/hsi/trace003/550.png" },
          { "spectralIndex": 7, "s3Path": "s3://bucket/hsi/trace003/570.png" },
          { "spectralIndex": 8, "s3Path": "s3://bucket/hsi/trace003/590.png" }
        ]
      }
    },
    {
      "traceNum": "L01709271277004",
      "speciesId": 2,
      "categoryId": 4,
      "sexType": 2,
      "gradeNum": 2,
      "statusType": 0,
      "butcheryYmd": "2025-08-02",
      "birthYmd": "2023-03-14",
      "weightKg": 13.3,
      "deepAging": {
        "isDeepAging": true,
        "seqno": 1
      },
      "sensory": {
        "marbling": 3.2,
        "color": 4.2,
        "texture": 2.9,
        "surfaceMoisture": 1.3,
        "overall": 3.8
      },
      "hsi": {
        "isRefrigerated": true,
        "filmedAt": "2025-08-19T13:00:00Z",
        "images": [
          { "spectralIndex": 0, "s3Path": "s3://bucket/hsi/trace004/430.png" },
          { "spectralIndex": 1, "s3Path": "s3://bucket/hsi/trace004/450.png" },
          { "spectralIndex": 2, "s3Path": "s3://bucket/hsi/trace004/470.png" },
          { "spectralIndex": 3, "s3Path": "s3://bucket/hsi/trace004/490.png" },
          { "spectralIndex": 4, "s3Path": "s3://bucket/hsi/trace004/510.png" },
          { "spectralIndex": 5, "s3Path": "s3://bucket/hsi/trace004/530.png" },
          { "spectralIndex": 6, "s3Path": "s3://bucket/hsi/trace004/550.png" },
          { "spectralIndex": 7, "s3Path": "s3://bucket/hsi/trace004/570.png" },
          { "spectralIndex": 8, "s3Path": "s3://bucket/hsi/trace004/590.png" }
        ]
      }
    },
    {
      "traceNum": "L01709271277005",
      "speciesId": 1,
      "categoryId": 6,
      "sexType": 1,
      "gradeNum": 3,
      "statusType": 0,
      "butcheryYmd": "2025-08-06",
      "birthYmd": "2022-11-11",
      "weightKg": 15.1,
      "deepAging": {
        "isDeepAging": false,
        "seqno": 0
      },
      "sensory": {
        "marbling": 3.7,
        "color": 3.9,
        "texture": 3.1,
        "surfaceMoisture": 1.4,
        "overall": 4.0
      },
      "hsi": {
        "isRefrigerated": false,
        "filmedAt": "2025-08-19T14:00:00Z",
        "images": [
          { "spectralIndex": 0, "s3Path": "s3://bucket/hsi/trace005/430.png" },
          { "spectralIndex": 1, "s3Path": "s3://bucket/hsi/trace005/450.png" },
          { "spectralIndex": 2, "s3Path": "s3://bucket/hsi/trace005/470.png" },
          { "spectralIndex": 3, "s3Path": "s3://bucket/hsi/trace005/490.png" },
          { "spectralIndex": 4, "s3Path": "s3://bucket/hsi/trace005/510.png" },
          { "spectralIndex": 5, "s3Path": "s3://bucket/hsi/trace005/530.png" },
          { "spectralIndex": 6, "s3Path": "s3://bucket/hsi/trace005/550.png" },
          { "spectralIndex": 7, "s3Path": "s3://bucket/hsi/trace005/570.png" },
          { "spectralIndex": 8, "s3Path": "s3://bucket/hsi/trace005/590.png" }
        ]
      }
    }
  ]
}
"""