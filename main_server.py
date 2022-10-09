from fastapi import FastAPI

app = FastAPI()


@app.get('/get_buh_digest')
async def root():

    return {'data': 322}


@app.get('/get_dir_digest')
async def root():
    return {'data': 322}


@app.get('/get_trending')
async def root():
    return {'data': 322}
