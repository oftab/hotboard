from dataclasses import dataclass, field
from typing import Optional
import os
from pathlib import Path


@dataclass
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = field(init=False)
    output_file: str = "hotboard.json"
    max_items: int = 100
    log_level: str = "INFO"
    config_file: str = "config.yaml"
    
    def __post_init__(self):
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    @property
    def output_path(self) -> Path:
        return self.data_dir / self.output_file
    
    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            project_root=Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent.parent)),
            output_file=os.environ.get("OUTPUT_FILE", "hotboard.json"),
            max_items=int(os.environ.get("MAX_ITEMS", "100")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            config_file=os.environ.get("CONFIG_FILE", "config.yaml"),
        )
    
    def to_dict(self) -> dict:
        return {
            "project_root": str(self.project_root),
            "data_dir": str(self.data_dir),
            "output_file": self.output_file,
            "max_items": self.max_items,
            "log_level": self.log_level,
            "config_file": self.config_file,
        }
