from dataclasses import dataclass
from src.app.lib.logger import site_key_var
import logging

from src.app.lib.config import SiteConfig

@dataclass
class AppContext:
  config: SiteConfig
  logger: logging.Logger

  def __post_init__(self):
    site_key_var.set(self.config.site_key)

  @property
  def modes_global( self ):
    return self.config.modes_global
  
  @property
  def timeouts_global( self ):
    return self.config.timeouts_global

  @property
  def selectors(self):
    return self.config.selectors

  @property
  def timeouts(self):
    return self.config.timeouts