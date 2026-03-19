from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

TAGS = [
    "B-AGE",
    "B-BUILDINGNUM",
    "B-CITY",
    "B-CREDITCARDNUMBER",
    "B-DATE",
    "B-DRIVERLICENSENUM",
    "B-EMAIL",
    "B-GENDER",
    "B-GIVENNAME",
    "B-IDCARDNUM",
    "B-PASSPORTNUM",
    "B-SEX",
    "B-SOCIALNUM",
    "B-STREET",
    "B-SURNAME",
    "B-TAXNUM",
    "B-TELEPHONENUM",
    "B-TIME",
    "B-TITLE",
    "B-ZIPCODE",
    "I-BUILDINGNUM",
    "I-CITY",
    "I-CREDITCARDNUMBER",
    "I-DATE",
    "I-DRIVERLICENSENUM",
    "I-EMAIL",
    "I-GENDER",
    "I-GIVENNAME",
    "I-IDCARDNUM",
    "I-PASSPORTNUM",
    "I-SEX",
    "I-SOCIALNUM",
    "I-STREET",
    "I-SURNAME",
    "I-TAXNUM",
    "I-TELEPHONENUM",
    "I-TIME",
    "I-TITLE",
    "I-ZIPCODE",
    "O",
]


class Settings(BaseSettings):
    tags: list[str] = TAGS

    gf_security_admin_password: str
    triton_server_url: str = "triton:8001"
    auth_token: str
    scope: str = "GIGACHAT_API_PERS"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()
