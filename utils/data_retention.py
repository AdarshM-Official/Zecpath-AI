import os
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

class DataRetentionManager:
    """
    Handles data retention and compliance (e.g., Right to Erasure / GDPR).
    """
    
    def __init__(self, storage_dir: str = "candidates"):
        self.storage_dir = storage_dir
        
    def purge_candidate_data(self, candidate_id: str) -> bool:
        """
        Permanently deletes all data associated with a candidate.
        """
        success = True
        # For demo purposes, we define patterns of files to delete.
        # In a real system, this might also involve database queries.
        files_to_check = [
            f"{self.storage_dir}/{candidate_id}_score.json",
            f"{self.storage_dir}/{candidate_id}_transcript.txt",
            f"{self.storage_dir}/{candidate_id}_report.md"
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Purged: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to purge {file_path}: {e}")
                    success = False
                    
        return success
        
    def anonymize_candidate_data(self, candidate_id: str) -> bool:
        """
        Removes PII but retains the objective scores for system fairness auditing.
        """
        score_file = f"{self.storage_dir}/{candidate_id}_score.json"
        if os.path.exists(score_file):
            try:
                with open(score_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Replace ID and remove any names
                data["candidate_id"] = "ANON_" + str(hash(candidate_id))
                if "name" in data:
                    del data["name"]
                    
                with open(score_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                return True
            except Exception as e:
                logger.error(f"Failed to anonymize {score_file}: {e}")
                return False
        return False
