from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import os
import logging
from pymongo import MongoClient
import signal

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["product_responses"]

processes = {
    "crawler": None,
    "excel": None
}

def start_crawler():
    """Start the product crawler"""
    global processes
    try:
        if processes["crawler"] and processes["crawler"].poll() is not None:
            processes["crawler"] = None

        if processes["crawler"]:
            raise HTTPException(
                status_code=400,
                detail="Crawler is already running"
            )

        processes["crawler"] = subprocess.Popen(
            ["python", "crawler.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"Crawler started with PID: {processes['crawler'].pid}")
        return {"status": "success", "pid": processes["crawler"].pid}
    
    except Exception as e:
        logger.error(f"Start error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start crawler: {str(e)}"
        )

@app.get("/stop")
def stop_crawler():
    """Stop the running crawler"""
    global processes
    try:
        if processes["crawler"]:
            os.killpg(os.getpgid(processes["crawler"].pid), signal.SIGTERM)
            processes["crawler"].wait(timeout=10)
            processes["crawler"] = None
            return {"status": "success", "message": "Crawler stopped"}
        
        raise HTTPException(
            status_code=404,
            detail="No crawler process running"
        )
    
    except Exception as e:
        logger.error(f"Stop error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop crawler: {str(e)}"
        )

@app.get("/status")
def get_status():
    """Get current crawler status"""
    try:
        if processes["crawler"] and processes["crawler"].poll() is None:
            return {
                "status": "running",
                "pid": processes["crawler"].pid
            }
        return {"status": "stopped"}
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to check status"
        )

@app.get("/get-excel")
def generate_excel_report():
    """Generate and download Excel report"""
    try:
        # Run Excel generator
        result = subprocess.run(
            ["python", "excel.py"],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            logger.error(f"Excel generation failed: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Excel generation failed: {result.stderr}"
            )

        file_path = "POPPOPS_products_export.xlsx"
        if not os.path.exists(file_path):
            logger.error("Excel file not found after generation")
            raise HTTPException(
                status_code=404,
                detail="Excel file not generated"
            )

        return FileResponse(
            file_path,
            filename="product_report.xlsx",
            media_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )
    
    except subprocess.TimeoutExpired:
        logger.error("Excel generation timed out")
        raise HTTPException(
            status_code=504,
            detail="Excel generation timed out"
        )
    except Exception as e:
        logger.error(f"Excel error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Excel generation failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
