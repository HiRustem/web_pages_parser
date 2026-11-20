from pathlib import Path
from functools import lru_cache
import yaml
from pydantic import BaseModel

CONFIGS_DIR = Path( "src/app/configs" )

class GlobalConfig(BaseModel):
  request_timeout: int
  user_agent: str
  log_level: str
  browser: str
  modes_global: dict
  timeouts_global: dict

class SiteConfig(GlobalConfig):
  site_key: str
  base_url: str
  selectors: dict
  timeouts: dict


def _load_yaml(path: Path) -> dict:
  with path.open(encoding="utf-8") as f:
      return yaml.safe_load(f) or {}
  
@lru_cache
def get_global_config() -> GlobalConfig:
  return GlobalConfig(**_load_yaml(CONFIGS_DIR / "global.yaml"))

@lru_cache
def get_site_config(site_key: str) -> SiteConfig:
    global_data = get_global_config().model_dump()
    site_data = _load_yaml(CONFIGS_DIR / "sites" / f"{site_key}.yaml")
    merged = {**global_data, **site_data}
    return SiteConfig(**merged)