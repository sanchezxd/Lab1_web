import requests
import sys

def test_server():
    try:
        # Пингуем главную страницу нашего приложения
        r = requests.get('http://127.0.0.1:5000/')
        if r.status_code == 200:
            print("Успех: Сервер Flask работает и возвращает статус 200!")
            sys.exit(0)
        else:
            print(f"Провал: Сервер вернул статус {r.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка подключения: Сервер не запущен. Детали: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_server()
