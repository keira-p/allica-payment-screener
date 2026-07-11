from fastapi import FastAPI

app = FastAPI(title="Allica Payment Screener")


@app.get("/")
def read_root():
    return {"message": "Payment screening service is running"}
