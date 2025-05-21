from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    BOT_TOKEN: str = "7775177461:AAFbCo3l64_7CIPJusp_3bXfA7ucKVoVfvo"
    CHANNEL_USERNAME: str = "testcatalog"
    GROUP_USERNAME: str = None
    ADMIN_IDS: List[int] = field(default_factory=list)  
