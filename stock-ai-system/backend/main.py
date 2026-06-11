from fastapi import FastAPI
from scanner import scan_market

app = FastAPI()


@app.get("/signals")
def get_signals():

    signals = scan_market()

    return {
        "status": "success",
        "data": signals
    }
