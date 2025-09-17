import os
import uvicorn
from api.app import app 

def main():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"
    log_level = os.getenv("API_LOG_LEVEL", "info")

    uvicorn.run(app, host=host, port=port, reload=reload, log_level=log_level)

if __name__ == "__main__":
    main()
