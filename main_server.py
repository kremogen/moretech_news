from fastapi import FastAPI

import main

app = FastAPI()


@app.get('/api/v1/get_trending')
async def get_trending(role: str = 'boss', count: int = 3):
    news = main.get_news()
    if role in news:
        result = list()
        for i in range(count):
            data = {
                'article': news['Article'][i],
                'link': news['Link'][i],
                'date': news['Date'][i],
            }
            result.append(data)
        return result
    else:
        return 'role not found'


@app.get('/api/v1/get_digest')
async def get_digest(role: str = 'boss', count: int = 3):
    news = main.get_news()
    if role in news:
        result = list()
        for i in range(count):
            data = {
                'digest': news['Digest'][i],
                'link': news['Link'][i],
                'date': news['Date'][i],
            }
            result.append(data)
        return result
    else:
        return 'role not found'
