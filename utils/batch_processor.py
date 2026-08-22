import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class AsyncBatchProcessor:
    """
    Utility for processing large batches of tasks concurrently.
    Used for bulk resume parsing, end-of-day scoring aggregations, and report generations.
    """

    def __init__(self, max_workers: int = None):
        # Default to CPU cores * 4 for I/O bound tasks
        self.max_workers = max_workers or (os.cpu_count() or 1) * 4

    def process_batch(self, items: List[Any], process_fn: Callable[[Any], Any]) -> Dict[str, Any]:
        """
        Executes a processing function across a list of items concurrently.
        """
        results = []
        errors = []
        
        logging.info(f"Starting batch processing of {len(items)} items with {self.max_workers} workers.")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map futures to their original item for error tracing
            future_to_item = {executor.submit(process_fn, item): item for item in items}
            
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    logging.error(f"Item processing failed: {exc}")
                    errors.append({"item": item, "error": str(exc)})

        logging.info(f"Batch complete. {len(results)} succeeded, {len(errors)} failed.")
        
        return {
            "total_processed": len(items),
            "success_count": len(results),
            "error_count": len(errors),
            "results": results,
            "errors": errors
        }

if __name__ == "__main__":
    # Example usage mock
    import time
    
    def mock_parse_resume(resume_id: str):
        time.sleep(0.1) # Simulate I/O bound parsing task
        if "fail" in resume_id:
            raise ValueError("Corrupted PDF")
        return {"id": resume_id, "ats_score": 85.0}

    processor = AsyncBatchProcessor()
    res = processor.process_batch(["res_1", "res_2", "res_fail_3", "res_4"], mock_parse_resume)
    print(json.dumps(res, indent=2))
