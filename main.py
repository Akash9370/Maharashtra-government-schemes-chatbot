from dotenv import load_dotenv
import uvicorn

# 🔥 load env variables FIRST
load_dotenv()

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)