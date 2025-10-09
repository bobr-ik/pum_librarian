from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import Field, BaseModel
from aiogram import Bot

BASE_DIR = Path(__file__).resolve().parent
print(f"{BASE_DIR}/.env")

class Settings(BaseSettings):
    db_url: str = Field(default=f'sqlite+aiosqlite:///{BASE_DIR}/database/data.db', validate_default=False) # по этому адресу создатся файл с бд
    BOT_TOKEN: str

    @property
    def BOT(self):
        return Bot(token=self.BOT_TOKEN)
    
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

settings = Settings() # объект класса настроек