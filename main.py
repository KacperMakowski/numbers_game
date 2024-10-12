from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Dodanie middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Możesz dostosować to do konkretnego źródła, jeśli to konieczne
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


numbers = [None, None]  # Liczby graczy
players = []  # Websockety graczy
player1_guess = []  # Lista prób gracza 1
player2_guess = []  # Lista prób gracza 2
last_guess = [None, None]  # Ostatnie próby graczy
both_numbers_ready = asyncio.Event()
both_guesses_ready = asyncio.Event()


# FUNKCJA SPRAWDZAJĄCA, KTÓRE LICZBY SIĘ ZGADZAJĄ
async def check_number(player_id):
    websocket = players[player_id]
    if player_id == 0:  # Dla gracza 1
        x = 0
        for number in str(player1_guess[-1]):
            if number == str(numbers[1][x]):
                result = f"{number} znajduje się na właściwej pozycji"
            elif number in str(numbers[1]):
                result = f"{number} znajduje się, ale na złej pozycji"
            else:
                result = f"{number} nie znajduje się"
            await websocket.send_text(result)
            x = x + 1
    elif player_id == 1:  # Dla gracza 2
        x = 0
        for number in str(player2_guess[-1]):
            if number == str(numbers[0][x]):
                result = f"{number} znajduje sie na właściwej pozycji"
            elif number in str(numbers[0]):
                result = f"{number} znajduje sie, ale na zlej pozycji"
            else:
                result = f"{number} nie znajduje sie"
            await websocket.send_text(result)
            x = x + 1


# OBSŁUGA TRAFIEŃ GRACZY
async def guesses(player_id):
    while True:
        global players, last_guess
        websocket = players[player_id]
        last_guess[player_id] = await websocket.receive_text()  # Przypisanie ostaniej liczby
        # Dodanie liczb do historii
        if player_id == 0:
            player1_guess.append(last_guess[0])
        elif player_id == 1:
            player2_guess.append(last_guess[1])

        if last_guess[0] and last_guess[1]:
            both_guesses_ready.set()  # Czeka na zdarzenie

        await both_guesses_ready.wait()
        # Wypisanie tekstu dla graczy i serwera
        ready = f'Obaj gracze podali liczby'
        print(ready)
        if player_id == 0:
            message = f'Przeciwnik zgaduje: {player2_guess[-1]}'
            await websocket.send_text(message)
        elif player_id == 1:
            message = f'Przeciwnik zgaduje: {player1_guess[-1]}'
            await websocket.send_text(message)
        # Sprawdzenie, czy któryś gracz wygrał
        if player1_guess[-1] == numbers[1] and player2_guess[-1] != numbers[0]:
            winner = f'Wygrał gracz 1. GRATULACJE!!!'
        elif player2_guess[-1] == numbers[0] and player1_guess[-1] != numbers[1]:
            winner = f'Wygrał gracz 2. GRATULACJE!!!'
        elif player1_guess[-1] == numbers[1] and player2_guess[-1] == numbers[0]:
            winner = f"REMIS!!! Obaj gracze odgadli liczby w tej samej turze. GRATULACJE!!"
        else:
            winner = f"Sprobuj zgadnac liczbe przeciwnika"
            await check_number(player_id)
            last_guess[player_id] = None  # Zerowanie zmiennej potrzebne do zdarzenia
        both_guesses_ready.clear()  # Reset zdarzenia
        print(winner)
        await websocket.send_text(winner)


# POCZĄTEK PROGRAMU, PODANIE SWOICH LICZB
async def run(websocket):
    global numbers, players, player1_guess, player2_guess, last_guess, both_numbers_ready
    # Serwer wpuści tylko 2 graczy
    if len(players) >= 2:
        print("Za dużo graczy, odrzucam połączenie.")
        await websocket.close()
        return
    # Dodaje websockety do listy graczy po czym nadaje każdemu ID
    players.append(websocket)
    player_id = len(players) - 1
    print(f'Gracz {player_id} | {players[player_id]} | połączył się')
    try:
        # Przypisz graczowi ID
        await websocket.send_text(str(player_id + 1))
        # PODANIE SWOJEJ LICZBY
        numbers[player_id] = await websocket.receive_text()
        print(f'Liczba gracza {player_id} to: {numbers[player_id]}')
        # Sprawdza, czy obaj gracze wysłali liczby i ustawia zdarzenie
        if numbers[0] and numbers[1]:
            both_numbers_ready.set()
        # Czeka na zdarzenie
        await both_numbers_ready.wait()
        # Wysłanie wiadomości do graczy i serwera
        ready = f'Obaj gracze podali swoje liczby'
        print(ready)
        await websocket.send_text(ready)
        # Obsługa zgadywania w osobnej korutynie
        await guesses(player_id)

    except WebSocketDisconnect:
        print(f'Gracz {player_id} rozłączył się')

    finally:
        players.remove(websocket)
        print(f'Gracz {player_id} rozłączył się')


# Uruchomienie serwera
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


@app.get("/")
async def get():
    with open("static/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await run(websocket)
