import requests

API_KEY = "45525d80aed6beabf843b705a3b6e017"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str, api_key: str = API_KEY) -> dict:
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
    except requests.exceptions.Timeout:
        raise TimeoutError("Превышено время ожидания ответа от сервера (таймаут 5 сек)")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Ошибка сетевого запроса: {e}")

    if response.status_code == 401:
        raise ValueError("Неверный API ключ (401)")
    elif response.status_code == 404:
        raise LookupError("Город не найден (404)")
    elif response.status_code != 200:
        raise RuntimeError(f"Ошибка API: {response.status_code} - {response.text}")

    data = response.json()

    return {
        "city": data.get("name"),
        "temperature": data["main"].get("temp"),
        "description": data["weather"][0].get("description"),
        "humidity": data["main"].get("humidity"),
        "wind_speed": data["wind"].get("speed")
    }

from fastapi import FastAPI, HTTPException, Query
app = FastAPI()

@app.get("/weather")
def weather_endpoint(city: str = Query(..., description="Название города")):
    try:
        return get_weather(city)
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

