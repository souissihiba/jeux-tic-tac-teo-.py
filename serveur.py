import socket
import select
import threading
import pygame
import random

# Paramètres réseau
HOST = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 1024

# Couleurs et paramètres Pygame
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15

# Initialisation Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")

def draw_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 50)
    text1 = font.render("1. Jouer contre un autre PC", True, BLACK)
    text2 = font.render("2. Jouer contre l'IA", True, BLACK)
    screen.blit(text1, (100, 200))
    screen.blit(text2, (100, 300))
    pygame.display.flip()

def choose_mode():
    while True:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "online"
                elif event.key == pygame.K_2:
                    return "ai"

mode = choose_mode()

# Grille du jeu
board = [["" for _ in range(3)] for _ in range(3)]
player_symbol = "X"
ai_symbol = "O"
my_turn = True
running = True
clients = []

# Vérifier le gagnant
def check_winner():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != "":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != "":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
        return board[0][2]
    if all(board[y][x] != "" for y in range(3) for x in range(3)):
        return "Tie"
    return None

if mode == "online":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print("Serveur en attente d'un joueur...")

    def handle_client(client):
        global my_turn, running
        try:
            while running:
                ready, _, _ = select.select([client], [], [], 0.1)
                if ready:
                    data = client.recv(BUFFER_SIZE).decode()
                    if not data:
                        break
                    print(f"Données reçues: {data}")
                    x, y, symbol = data.split()
                    if board[int(y)][int(x)] == "":
                        board[int(y)][int(x)] = symbol
                        my_turn = True
                        if check_winner():
                            running = False
        except:
            pass
        finally:
            client.close()

    def accept_connections():
        client, addr = server.accept()
        clients.append(client)
        print(f"Joueur connecté depuis {addr}")
        client.send("START O".encode())
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

    threading.Thread(target=accept_connections, daemon=True).start()

elif mode == "ai":
    def ai_move():
        global my_turn, running
        empty_cells = [(y, x) for y in range(3) for x in range(3) if board[y][x] == ""]
        if empty_cells:
            y, x = random.choice(empty_cells)
            board[y][x] = ai_symbol
            winner = check_winner()
            if winner:
                print(f"{winner} a gagné !")
                running = False
            else:
                my_turn = True

# Fonction pour dessiner la grille
def draw_grid():
    screen.fill(WHITE)
    for x in range(1, 3):
        pygame.draw.line(screen, BLACK, (x * 200, 0), (x * 200, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, x * 200), (WIDTH, x * 200), LINE_WIDTH)

def draw_symbols():
    for y in range(3):
        for x in range(3):
            if board[y][x] == "X":
                pygame.draw.line(screen, BLUE, (x * 200 + 50, y * 200 + 50),
                                 (x * 200 + 150, y * 200 + 150), LINE_WIDTH)
                pygame.draw.line(screen, BLUE, (x * 200 + 150, y * 200 + 50),
                                 (x * 200 + 50, y * 200 + 150), LINE_WIDTH)
            elif board[y][x] == "O":
                pygame.draw.circle(screen, RED, (x * 200 + 100, y * 200 + 100), 50, LINE_WIDTH)

while running:
    draw_grid()
    draw_symbols()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        elif event.type == pygame.MOUSEBUTTONDOWN and my_turn:
            x, y = event.pos
            grid_x, grid_y = x // 200, y // 200

            if board[grid_y][grid_x] == "":
                board[grid_y][grid_x] = player_symbol
                print(f"Joueur local a joué: {grid_x} {grid_y} {player_symbol}")
                if mode == "online":
                    for client in clients:
                        client.send(f"{grid_x} {grid_y} {player_symbol}".encode())
                winner = check_winner()
                if winner:
                    print(f"{winner} a gagné !")
                    running = False
                else:
                    my_turn = False
                    if mode == "ai":
                        pygame.time.delay(500)
                        ai_move()

pygame.quit()
if mode == "online":
    server.close()


