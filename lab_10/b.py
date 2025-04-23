import pygame
import sys
import random
import psycopg2
from tabulate import tabulate


conn = psycopg2.connect(
    host="localhost", dbname="lab10",
    user="postgres", password="123456789", port=5432
)
cur = conn.cursor()


cur.execute("""
    CREATE TABLE IF NOT EXISTS snake_game_scores (
        id SERIAL PRIMARY KEY,
        player_name VARCHAR(50),
        score INTEGER,
        level INTEGER
    )
""")
conn.commit()

def insert_score(name, score, level):
    cur.execute("INSERT INTO snake_game_scores (player_name, score, level) VALUES (%s, %s, %s)", (name, score, level))
    conn.commit()

def show_scores(name=None):
    if name:
        cur.execute("SELECT score, level FROM snake_game_scores WHERE player_name = %s ORDER BY score DESC", (name,))
    else:
        cur.execute("SELECT player_name, score, level FROM snake_game_scores ORDER BY score DESC LIMIT 10")
    rows = cur.fetchall()
    headers = ["Name", "Score", "Level"] if not name else ["Score", "Level"]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))


def play_game():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    snake_pos = [[100, 50], [90, 50], [80, 50]]
    snake_speed = [10, 0]
    food = {'pos': [0, 0], 'weight': 1, 'spawn_time': 0}
    food_spawn = True
    score = 0
    level = 1
    speed_increase = 0.5
    food_counter = 0
    fps = pygame.time.Clock()
    paused = False
    


    player_name = input("Enter your name: ").strip()
    print("\nYour previous scores:")
    show_scores(player_name) 

    def check_collision(pos, level):
        if pos[0] < 0 or pos[0] >= SCREEN_WIDTH :
            return True
        if pos in snake_pos[1:]:
            return True
        
        return False

    def check_wrap(pos):
        if pos[1] < 0:
            pos[1] = SCREEN_HEIGHT - 10
        elif pos[1] > SCREEN_HEIGHT - 10:
            pos[1] = 0
        return pos

    def get_random_food():
        nonlocal food_counter
        while True:
            pos = [random.randrange(1, (SCREEN_WIDTH // 10)) * 10,
                   random.randrange(1, (SCREEN_HEIGHT // 10)) * 10]
            if pos not in snake_pos:
                weight = 2 if food_counter >= 2 else 1
                food_counter = 0 if weight == 2 else food_counter + 1
                return {'pos': pos, 'weight': weight, 'spawn_time': pygame.time.get_ticks()}

    
    saved_text_timer = 0 

    while True:
        saved_text_timer = 0  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake_speed[1] == 0:
                    snake_speed = [0, -10]
                elif event.key == pygame.K_DOWN and snake_speed[1] == 0:
                    snake_speed = [0, 10]
                elif event.key == pygame.K_LEFT and snake_speed[0] == 0:
                    snake_speed = [-10, 0]
                elif event.key == pygame.K_RIGHT and snake_speed[0] == 0:
                    snake_speed = [10, 0]
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_s and paused:
                    insert_score(player_name, score, level)
                    print(f"[✔] Score saved: {score} (Level {level})")
                    saved_text_timer = pygame.time.get_ticks()  


        if not paused:
            snake_pos.insert(0, [snake_pos[0][0] + snake_speed[0], snake_pos[0][1] + snake_speed[1]])

            snake_pos[0] = check_wrap(snake_pos[0])
            if check_collision(snake_pos[0], level):
                insert_score(player_name, score, level)

                screen.fill(BLACK)
                font_big = pygame.font.SysFont('arial', 50)
                game_over_text = font_big.render("GAME OVER", True, RED)
                screen.blit(game_over_text, [SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 25])
                pygame.display.flip()
                pygame.time.delay(2000)
                pygame.quit()

                print("\n===== GAME OVER =====")
                print(f"Player: {player_name} | Score: {score} | Level: {level}\n")
                print("=== Top 10 Leaderboard ===")
                show_scores()
                return

            if snake_pos[0] == food['pos']:
                score += food['weight']
                if score % 3 == 0:
                    level += 1
                food_spawn = True
            else:
                snake_pos.pop()

            if food_spawn:
                food = get_random_food()
                food_spawn = False

            
            if pygame.time.get_ticks() - food['spawn_time'] > 10000:
                food_spawn = True

        screen.fill(BLACK)
        for pos in snake_pos:
            pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

        food_color = RED if food['weight'] == 1 else (255, 165, 0)
        pygame.draw.rect(screen, food_color, pygame.Rect(food['pos'][0], food['pos'][1], 10, 10))

        font = pygame.font.SysFont('arial', 20)
        score_text = font.render(f"Score: {score} Level: {level}", True, WHITE)
        screen.blit(score_text, [0, 0])

        if paused:
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, [SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2])

            if pygame.time.get_ticks() - saved_text_timer < 2000:
                saved_text = font.render("✔ Saved!", True, (0, 255, 0))
                screen.blit(saved_text, [SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 + 30])
                
        pygame.display.flip()
        fps.tick(10 + level * speed_increase)

def menu():
    while True:
        print("""
        === SNAKE GAME MENU ===
        [p] Play Game
        [r] Show Top Ratings
        [f] Finish
        """)
        cmd = input("Choose command: ").lower()

        if cmd == "p":
            play_game()
        elif cmd == "r":
            print("\n=== TOP 10 RATINGS ===")
            show_scores()
        elif cmd == "f":
            break

menu()
cur.close()
conn.close()