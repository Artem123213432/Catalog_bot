from dataclasses import dataclass, field
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME")
    GROUP_USERNAME: str = os.getenv("GROUP_USERNAME")
    ADMIN_IDS: List[int] = field(default_factory=lambda: 
                                 [int(id.strip()) for id in os.getenv("ADMIN_USER_ID", "").split(",") 
                                  if id.strip().isdigit()])  
