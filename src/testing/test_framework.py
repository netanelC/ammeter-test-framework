

from typing import Dict, Optional
from ..utils.config import load_config
from Ammeters.client import request_current_from_ammeter


class AmmeterTestFramework:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        
    def get_single_reading(self, ammeter_type: str) -> Optional[float]:
        """
        Fetches a single current reading from the specified ammeter.
        """
        if ammeter_type not in self.config.get('ammeters', {}):
            raise ValueError(f"Unknown ammeter type: {ammeter_type}")
            
        ammeter_config = self.config['ammeters'][ammeter_type]
        port = ammeter_config['port']
        command = ammeter_config['command'].encode('utf-8')
        
        return request_current_from_ammeter(port, command)

    def run_test(self, ammeter_type: str) -> Dict:
        pass