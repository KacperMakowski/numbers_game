📖 Overview

Guess-IT is a multiplayer browser-based number-guessing game where two players compete to guess each other's secret 5-digit numbers. 
The game uses a FastAPI backend to manage WebSocket connections for real-time communication between players.

🛠 Features

Real-Time Gameplay: Players receive immediate feedback about their guesses via WebSockets.
Interactive Interface: Dynamic updates in the browser, such as guess history and real-time results.
Multiplayer Logic: Manages interactions between two players, ensuring fairness.
Responsive Design: Optimized for different devices with a simple, clean UI.
Hints for Guesses: Players receive feedback about their guesses:
Correct digit and position.
Correct digit but incorrect position.
Incorrect digit.

⚙️ Tech Stack

Frontend: HTML, TailwindCSS, JavaScript.
Backend: FastAPI (Python), WebSockets.
Server: Uvicorn.

🕹 How to Play

Setup Your Number: Each player enters a 5-digit number.
Start Guessing: Players take turns guessing their opponent's number.
Get Feedback: For each digit:
Green: Correct position.
Yellow: Correct digit, wrong position.
Gray: Incorrect digit.
Winning: The first player to guess their opponent's number wins. If both guess correctly in the same turn, it's a draw.

🚀 Getting Started

Prerequisites
Python 3.9+ installed.
Node.js (optional, for additional front-end tooling like TailwindCSS).
Installation Steps

1. Clone the repository:
git clone https://github.com/your-repo/guess-it.git
cd guess-it

2. Install dependencies:
pip install fastapi uvicorn

3. Ensure TailwindCSS is compiled (if modified):
npx tailwindcss build src/styles.css -o static/output.css

4. Run the server:
python main.py

5. Open your browser at http://localhost:8000.

Directory Structure
/static         # Static files for CSS
main.py         # FastAPI backend logic
index.html      # Frontend HTML and JavaScript

📂 Code Highlights

Frontend (index.html)
Dynamic Updates: JavaScript manages real-time updates via WebSocket.
Interactive Feedback: Displays history and hints dynamically.
Backend (main.py)
WebSocket Communication: Handles connections, game state, and message passing.
Game Logic: Checks guesses and determines results.

🌐 Game Flow

Player Connects: WebSocket assigns a unique ID.
Submit Numbers: Both players input their secret numbers.
Turn-Based Guesses: Players alternately guess and receive hints.
Determine Winner: Server checks for a win or draw.

🛡 Known Limitations

Only two players can connect simultaneously.
Basic error handling for disconnections.

📜 License

MIT License. Feel free to use, modify, and distribute.

🤝 Contributions

Contributions are welcome! Feel free to open issues or submit pull requests.
