from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Adding CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can customize this to a specific origin if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

numbers = [None, None]  # Player numbers
players = []  # Player WebSockets
player1_guess = []  # Player 1's guess history
player2_guess = []  # Player 2's guess history
last_guess = [None, None]  # Last guesses of players
both_numbers_ready = asyncio.Event()
both_guesses_ready = asyncio.Event()


# FUNCTION TO CHECK WHICH NUMBERS MATCH
async def check_number(player_id):
    websocket = players[player_id]
    if player_id == 0:  # For player 1
        x = 0
        for number in str(player1_guess[-1]):
            if number == str(numbers[1][x]):
                result = f"{number} znajduje sie na wlasciwej pozycji"
            elif number in str(numbers[1]):
                result = f"{number} znajduje sie, ale na zlej pozycji"
            else:
                result = f"{number} nie znajduje sie"
            await websocket.send_text(result)
            x = x + 1
    elif player_id == 1:  # For player 2
        x = 0
        for number in str(player2_guess[-1]):
            if number == str(numbers[0][x]):
                result = f"{number} znajduje sie na wlasciwej pozycji"
            elif number in str(numbers[0]):
                result = f"{number} znajduje sie, ale na zlej pozycji"
            else:
                result = f"{number} nie znajduje sie"
            await websocket.send_text(result)
            x = x + 1


# HANDLING PLAYER GUESSES
async def guesses(player_id):
    while True:
        global players, last_guess
        websocket = players[player_id]
        last_guess[player_id] = await websocket.receive_text()  # Assigning the last guess
        # Adding numbers to history
        if player_id == 0:
            player1_guess.append(last_guess[0])
        elif player_id == 1:
            player2_guess.append(last_guess[1])

        if last_guess[0] and last_guess[1]:
            both_guesses_ready.set()  # Waiting for an event

        await both_guesses_ready.wait()
        # Printing text for players and server
        ready = f'Obaj gracze podali liczby'
        print(ready)
        if player_id == 0:
            message = f'Przeciwnik zgaduje: {player2_guess[-1]}'
            await websocket.send_text(message)
        elif player_id == 1:
            message = f'Przeciwnik zgaduje: {player1_guess[-1]}'
            await websocket.send_text(message)
        # Checking if any player has won
        if player1_guess[-1] == numbers[1] and player2_guess[-1] != numbers[0]:
            winner = f'Wygral gracz 1'
        elif player2_guess[-1] == numbers[0] and player1_guess[-1] != numbers[1]:
            winner = f'Wygral gracz 2.'
        elif player1_guess[-1] == numbers[1] and player2_guess[-1] == numbers[0]:
            winner = f"REMIS!!!"
        else:
            winner = f"Sprobuj zgadnac liczbe przeciwnika"
            await check_number(player_id)
            last_guess[player_id] = None  # Resetting the variable needed for the event
        both_guesses_ready.clear()  # Resetting the event
        print(winner)
        await websocket.send_text(winner)


# START OF THE PROGRAM, ENTERING YOUR NUMBERS
async def run(websocket):
    global numbers, players, player1_guess, player2_guess, last_guess, both_numbers_ready
    # The server will only allow 2 players
    if len(players) >= 2:
        print("Za dużo graczy, odrzucam połączenie.")
        await websocket.close()
        return
    # Adds WebSockets to the player list and assigns each an ID
    players.append(websocket)
    player_id = len(players) - 1
    print(f'Gracz {player_id} | {players[player_id]} | połączył się')
    try:
        # Assign the ID to the player
        await websocket.send_text(str(player_id + 1))
        # ENTERING THEIR NUMBER
        numbers[player_id] = await websocket.receive_text()
        print(f'Liczba gracza {player_id} to: {numbers[player_id]}')
        # Checks if both players have submitted numbers and sets the event
        if numbers[0] and numbers[1]:
            both_numbers_ready.set()
        # Waiting for the event
        await both_numbers_ready.wait()
        # Sending a message to players and server
        ready = f'Obaj gracze podali swoje liczby'
        print(ready)
        await websocket.send_text(ready)
        # Handling guesses in a separate coroutine
        await guesses(player_id)

    except WebSocketDisconnect:
        print(f'Gracz {player_id} rozłączył się')

    finally:
        players.remove(websocket)
        print(f'Gracz {player_id} rozłączył się')


# Running the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


@app.get("/")
async def get():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await run(websocket)
