import pygame
import socket
import threading

# Paramètres réseau
HOST = "xxx.xxx.x.xx"  # Mets ici l'IP du serveur 
PORT = 5555
BUFFER_SIZE = 1024

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialisation Pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe (Client)")
font = pygame.font.Font(None, 80)  # Police pour afficher les messages de fin

# Grille du jeu
board = [["" for _ in range(3)] for _ in range(3)]
player_symbol = None
my_turn = False
game_over = False
winner_text = ""  # Message de fin

# Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Fonction pour dessiner la grille
def draw_grid():
    screen.fill(WHITE)
    for x in range(1, 3):
        pygame.draw.line(screen, BLACK, (x * 200, 0), (x * 200, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, x * 200), (WIDTH, x * 200), LINE_WIDTH)

# Fonction pour afficher X et O
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

# Fonction pour afficher le message de fin
def display_winner():
    text = font.render(winner_text, True, GREEN)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(3000)  # Attendre 3 secondes avant de fermer

# Fonction pour écouter le serveur
def listen_server():
    global my_turn, player_symbol, game_over, winner_text
    while True:
        try:
            data = client.recv(BUFFER_SIZE).decode().strip()
            if not data:
                continue  # Ignore les messages vides

            if "START" in data:
                _, symbol = data.split()
                player_symbol = symbol
                my_turn = (symbol == "X")  # "X" commence toujours
                print(f"Vous êtes {player_symbol}")

            elif "a gagné" in data:  # Vérifie si le serveur annonce un gagnant
                print(data)  # Affiche "X a gagné" ou "O a gagné"
                winner_text = f"{data.split()[0]} Wins!"
                game_over = True
                break  # Arrête la boucle du thread

            elif "Égalité" in data:  # Vérifie si c'est un match nul
                print(data)  # Affiche "Égalité"
                winner_text = "It's a Tie!"
                game_over = True
                break

            else:
                try:
                    x, y, symbol = data.split()
                    board[int(y)][int(x)] = symbol
                    my_turn = (symbol != player_symbol)
                except ValueError:
                    print("Données mal reçues :", data)  # Debug si le message est incorrect

        except (ConnectionAbortedError, ConnectionResetError):
            print("Connexion fermée par le serveur.")
            break

# Démarrer l'écoute serveur
threading.Thread(target=listen_server, daemon=True).start()

# Boucle principale
running = True
while running:
    draw_grid()
    draw_symbols()

    if game_over:
        display_winner()
        running = False  # Quitter la boucle après l'affichage du message

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and my_turn and not game_over:
            x, y = event.pos
            grid_x, grid_y = x // 200, y // 200

            if board[grid_y][grid_x] == "":
                board[grid_y][grid_x] = player_symbol
                client.send(f"{grid_x} {grid_y} {player_symbol}".encode())
                my_turn = False

pygame.quit()
client.close()
