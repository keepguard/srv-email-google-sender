
import uvicorn
from app.config.loader import load_settings

if __name__ == "__main__":
    s = load_settings()
    uvicorn.run("app.main:app", host=s.server.host, port=s.server.port, reload=False)
