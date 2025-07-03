import pygame
import sys
import random
from collections import deque
import heapq
import itertools

pygame.init()

WIDTH = 700
GRID_SIZE = 100
CELL_SIZE = WIDTH // GRID_SIZE
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Visualizer: Enhanced Maze and Search")

BACKGROUND = (255, 255, 255)
GRID_LINES = (220, 220, 220)
OBSTACLE = (0, 0, 0)
START = (0, 255, 0)
STOP = (0, 0, 255)
END = (255, 0, 0)
PATH = (255, 165, 0)
SEARCH_COLORS = [
    {
        "QUEUE": (144, 238, 144),
        "VISITED": (173, 216, 230),
        "QUEUE_END": (255, 182, 193),
        "VISITED_END": (221, 160, 221)
    },
    {
        "QUEUE": (255, 218, 128),
        "VISITED": (255, 235, 205),
        "QUEUE_END": (200, 200, 255),
        "VISITED_END": (180, 180, 220)
    }
]
INPUT_BG = (240, 240, 240)
INPUT_BORDER = (180, 180, 180)
BUTTON_BG = (245, 245, 245)
BUTTON_HOVER = (220, 220, 255)
BUTTON_TEXT = (40, 40, 40)
INPUT_PROMPT = (40, 40, 40)
INPUT_TEXT = (40, 40, 40)
OVERLAY = (0, 0, 0, 120)

SEARCH_OPTIONS = [
    "Single-Point BFS",
    "Bidirectional BFS",
    "DFS Search",
    "Greedy Best-First",
    "A* Search"
]

def display_no_path_message(screen, width, height):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    font_size = 48
    message_font = pygame.font.SysFont(None, font_size, bold=True)
    message = "No path found!"
    text_surface = message_font.render(message, True, (255, 69, 0))
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))
    padding = 20
    bg_rect = text_rect.inflate(padding * 2, padding * 2)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=15)
    pygame.draw.rect(screen, (255, 69, 0), bg_rect, width=3, border_radius=15)
    screen.blit(text_surface, text_rect)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * CELL_SIZE
        self.y = col * CELL_SIZE
        self.color = BACKGROUND
        self.previous = None

    def get_pos(self):
        return (self.row, self.col)
    
    def is_obstacle(self):
        return self.color == OBSTACLE
    
    def is_special(self):
        return self.color in [START, STOP, END]
    
    def reset(self):
        if not self.is_special() and self.color != OBSTACLE:
            self.color = BACKGROUND
        self.previous = None

    def draw(self):
        pygame.draw.rect(WIN, self.color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(WIN, GRID_LINES, (self.x, self.y, CELL_SIZE, CELL_SIZE), 1)

def make_grid():
    grid = []
    for i in range(GRID_SIZE):
        grid.append([])
        for j in range(GRID_SIZE):
            grid[i].append(Node(i, j))
    return grid

def draw_grid(grid):
    WIN.fill(BACKGROUND, (0, 0, WIDTH, WIDTH))
    for row in grid:
        for node in row:
            node.draw()
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    if y >= WIDTH:
        return None, None
    row = x // CELL_SIZE
    col = y // CELL_SIZE
    return row, col

def get_neighbors(grid, node):
    neighbors = []
    row, col = node.get_pos()
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE):
            neighbor = grid[new_row][new_col]
            if not neighbor.is_obstacle():
                neighbors.append(neighbor)
    return neighbors

def manhattan(node1, node2):
    return abs(node1.row - node2.row) + abs(node1.col - node2.col)

def bfs_visualize(grid, start, end, draw, preserve_colors=None, search_colors=None):
    queue = deque()
    queue.append(start)
    visited = {start}
    parent = {}
    found = False
    QUEUE = search_colors["QUEUE"]
    VISITED = search_colors["VISITED"]
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        current = queue.popleft()
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                parent[neighbor] = current
                visited.add(neighbor)
                queue.append(neighbor)
                if not neighbor.is_special() and (not preserve_colors or neighbor.color not in preserve_colors):
                    neighbor.color = QUEUE
                    draw()
        if not current.is_special() and (not preserve_colors or current.color not in preserve_colors):
            current.color = VISITED
            draw()
    if not found:
        return None
    path = []
    node = end
    while node != start:
        path.append(node)
        node = parent.get(node)
        if node is None:
            return None
    path.append(start)
    path.reverse()
    return path

def bidirectional_bfs(grid, start, end, draw, preserve_colors=None, search_colors=None):
    queue_start = deque([start])
    queue_end = deque([end])
    visited_start = {start}
    visited_end = {end}
    parent_start = {start: None}
    parent_end = {end: None}
    meeting_node = None
    QUEUE = search_colors["QUEUE"]
    VISITED = search_colors["VISITED"]
    QUEUE_END = search_colors["QUEUE_END"]
    VISITED_END = search_colors["VISITED_END"]
    while queue_start and queue_end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        current_start = queue_start.popleft()
        if current_start in visited_end:
            meeting_node = current_start
            break
        for neighbor in get_neighbors(grid, current_start):
            if neighbor not in visited_start:
                parent_start[neighbor] = current_start
                visited_start.add(neighbor)
                queue_start.append(neighbor)
                if not neighbor.is_special() and (preserve_colors is None or neighbor.color not in preserve_colors):
                    neighbor.color = QUEUE
                    draw()
        current_end = queue_end.popleft()
        if current_end in visited_start:
            meeting_node = current_end
            break
        for neighbor in get_neighbors(grid, current_end):
            if neighbor not in visited_end:
                parent_end[neighbor] = current_end
                visited_end.add(neighbor)
                queue_end.append(neighbor)
                if not neighbor.is_special() and (preserve_colors is None or neighbor.color not in preserve_colors):
                    neighbor.color = QUEUE_END
                    draw()
        if not current_start.is_special() and (preserve_colors is None or current_start.color not in preserve_colors):
            current_start.color = VISITED
            draw()
        if not current_end.is_special() and (preserve_colors is None or current_end.color not in preserve_colors):
            current_end.color = VISITED_END
            draw()
    if not meeting_node:
        return None
    path_start = []
    node = meeting_node
    while node is not None:
        path_start.append(node)
        node = parent_start.get(node)
    path_start.reverse()
    path_end = []
    node = parent_end.get(meeting_node)
    while node is not None:
        path_end.append(node)
        node = parent_end.get(node)
    return path_start + path_end

def dfs_visualize(grid, start, end, draw, preserve_colors=None, search_colors=None):
    stack = [start]
    visited = {start}
    parent = {}
    found = False
    QUEUE = search_colors["QUEUE"]
    VISITED = search_colors["VISITED"]
    while stack:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        current = stack.pop()
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                parent[neighbor] = current
                visited.add(neighbor)
                stack.append(neighbor)
                if not neighbor.is_special() and (not preserve_colors or neighbor.color not in preserve_colors):
                    neighbor.color = QUEUE
                    draw()
        if not current.is_special() and (not preserve_colors or current.color not in preserve_colors):
            current.color = VISITED
            draw()
    if not found:
        return None
    path = []
    node = end
    while node != start:
        path.append(node)
        node = parent.get(node)
        if node is None:
            return None
    path.append(start)
    path.reverse()
    return path

def greedy_best_first_search(grid, start, end, draw, preserve_colors=None, search_colors=None):
    heap = []
    counter = itertools.count()
    heapq.heappush(heap, (manhattan(start, end), next(counter), start))
    parent = {}
    visited = {start}
    found = False
    QUEUE = search_colors["QUEUE"]
    VISITED = search_colors["VISITED"]
    while heap:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        _, _, current = heapq.heappop(heap)
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(grid, current):
            if neighbor not in visited:
                parent[neighbor] = current
                visited.add(neighbor)
                heapq.heappush(heap, (manhattan(neighbor, end), next(counter), neighbor))
                if not neighbor.is_special() and (not preserve_colors or neighbor.color not in preserve_colors):
                    neighbor.color = QUEUE
                    draw()
        if not current.is_special() and (not preserve_colors or current.color not in preserve_colors):
            current.color = VISITED
            draw()
    if not found:
        return None
    path = []
    node = end
    while node != start:
        path.append(node)
        node = parent.get(node)
        if node is None:
            return None
    path.append(start)
    path.reverse()
    return path

def astar_search(grid, start, end, draw, preserve_colors=None, search_colors=None):
    heap = []
    counter = itertools.count()
    g_score = {start: 0}
    heapq.heappush(heap, (manhattan(start, end), next(counter), start))
    parent = {}
    visited = set()
    QUEUE = search_colors["QUEUE"]
    VISITED = search_colors["VISITED"]
    while heap:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        _, _, current = heapq.heappop(heap)
        if current == end:
            break
        visited.add(current)
        for neighbor in get_neighbors(grid, current):
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan(neighbor, end)
                parent[neighbor] = current
                heapq.heappush(heap, (f_score, next(counter), neighbor))
                if not neighbor.is_special() and (not preserve_colors or neighbor.color not in preserve_colors):
                    neighbor.color = QUEUE
                    draw()
        if not current.is_special() and (not preserve_colors or current.color not in preserve_colors):
            current.color = VISITED
            draw()
    path = []
    node = end
    while node != start:
        path.append(node)
        node = parent.get(node)
        if node is None:
            return None
    path.append(start)
    path.reverse()
    return path

def mark_path(path, draw):
    for node in path:
        if not node.is_special() and node.color != PATH:
            node.color = PATH
        draw()

def generate_random_obstacles(grid, start, stops, end, density=0.25):
    for row in grid:
        for node in row:
            if node not in [start] + stops + [end] and random.random() < density:
                node.color = OBSTACLE

def clear_grid_except_special(grid, start, stops, end):
    for row in grid:
        for node in row:
            if node not in [start] + stops + [end]:
                node.reset()

def input_number_modal(screen, prompt):
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 28)
    overlay = pygame.Surface((WIDTH, WIDTH), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    screen.blit(overlay, (0, 0))
    modal_w = 500
    modal_h = 200
    modal_x = (WIDTH - modal_w) // 2
    modal_y = (WIDTH - modal_h) // 2
    pygame.draw.rect(screen, (255, 255, 255), (modal_x, modal_y, modal_w, modal_h), border_radius=16)
    pygame.draw.rect(screen, (200, 200, 200), (modal_x, modal_y, modal_w, modal_h), 2, border_radius=16)
    prompt_surface = font.render(prompt, True, INPUT_PROMPT)
    screen.blit(prompt_surface, (modal_x + (modal_w - prompt_surface.get_width()) // 2, modal_y + 20))
    input_rect = pygame.Rect(modal_x + 50, modal_y + 70, modal_w - 100, 50)
    pygame.draw.rect(screen, (245, 245, 245), input_rect, border_radius=8)
    pygame.draw.rect(screen, (180, 180, 180), input_rect, 2, border_radius=8)
    instruction = small_font.render("Type a number (0-99) and press Enter", True, (100, 100, 100))
    screen.blit(instruction, (modal_x + (modal_w - instruction.get_width()) // 2, modal_y + 130))
    user_text = ''
    active = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    if user_text.isdigit():
                        return int(user_text)
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.unicode.isdigit() and len(user_text) < 2:
                    user_text += event.unicode
        pygame.draw.rect(screen, (255, 255, 255), (modal_x, modal_y, modal_w, modal_h), border_radius=16)
        pygame.draw.rect(screen, (200, 200, 200), (modal_x, modal_y, modal_w, modal_h), 2, border_radius=16)
        screen.blit(prompt_surface, (modal_x + (modal_w - prompt_surface.get_width()) // 2, modal_y + 20))
        pygame.draw.rect(screen, (245, 245, 245), input_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 180, 180), input_rect, 2, border_radius=8)
        screen.blit(instruction, (modal_x + (modal_w - instruction.get_width()) // 2, modal_y + 130))
        text_surface = font.render(user_text, True, INPUT_TEXT)
        text_x = input_rect.x + (input_rect.width - text_surface.get_width()) // 2
        text_y = input_rect.y + (input_rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
        pygame.display.update()

def vertical_menu(screen, prompt, options):
    font = pygame.font.SysFont(None, 36)
    overlay = pygame.Surface((WIDTH, WIDTH), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    screen.blit(overlay, (0, 0))
    prompt_surface = font.render(prompt, True, (40, 40, 40))
    menu_w = WIDTH // 2
    menu_x = WIDTH // 4
    menu_y = WIDTH // 4
    menu_h = 60 + 60 * len(options)
    menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
    pygame.draw.rect(screen, (255,255,255), menu_rect, border_radius=16)
    screen.blit(prompt_surface, (menu_x + (menu_w - prompt_surface.get_width()) // 2, menu_y + 20))
    btn_h = 48
    btn_gap = 12
    btn_y = menu_y + 60
    btn_rects = []
    for i, label in enumerate(options):
        r = pygame.Rect(menu_x + 20, btn_y + i * (btn_h + btn_gap), menu_w - 40, btn_h)
        btn_rects.append(r)
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(btn_rects):
                    if rect.collidepoint(event.pos):
                        return i + 1
        pygame.draw.rect(screen, (255,255,255), menu_rect, border_radius=16)
        screen.blit(prompt_surface, (menu_x + (menu_w - prompt_surface.get_width()) // 2, menu_y + 20))
        for i, rect in enumerate(btn_rects):
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_BG
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, INPUT_BORDER, rect, 1, border_radius=8)
            label_surface = font.render(options[i], True, BUTTON_TEXT)
            screen.blit(label_surface, (rect.x + (rect.width - label_surface.get_width()) // 2,
                                        rect.y + (rect.height - label_surface.get_height()) // 2))
        pygame.display.update()

def recursive_division_maze_visual(grid, start, stops, end, draw):
    for row in grid:
        for node in row:
            if node not in [start] + stops + [end]:
                node.color = BACKGROUND
    def divide(x, y, w, h, orientation):
        if w < 3 or h < 3:
            return
        horizontal = orientation == 'H'
        if horizontal:
            wy = y + random.randrange(1, h - 1, 2)
            px = x + random.randrange(0, w, 2)
            for dx in range(w):
                node = grid[wy][x + dx]
                if (x + dx, wy) != (px, wy) and node not in [start] + stops + [end]:
                    node.color = OBSTACLE
                    draw()
            divide(x, y, w, wy - y, 'V')
            divide(x, wy + 1, w, y + h - wy - 1, 'V')
        else:
            wx = x + random.randrange(1, w - 1, 2)
            py = y + random.randrange(0, h, 2)
            for dy in range(h):
                node = grid[y + dy][wx]
                if (wx, y + dy) != (wx, py) and node not in [start] + stops + [end]:
                    node.color = OBSTACLE
                    draw()
            divide(x, y, wx - x, h, 'H')
            divide(wx + 1, y, x + w - wx - 1, h, 'H')
    for i in range(GRID_SIZE):
        for j in [0, GRID_SIZE-1]:
            if grid[i][j] not in [start] + stops + [end]:
                grid[i][j].color = OBSTACLE
                draw()
            if grid[j][i] not in [start] + stops + [end]:
                grid[j][i].color = OBSTACLE
                draw()
    divide(0, 0, GRID_SIZE, GRID_SIZE, 'H' if GRID_SIZE > GRID_SIZE else 'V')

def draw_instructions(screen, ready_for_obstacles, show=True):
    if not show:
        return
    font = pygame.font.SysFont(None, 28)
    if ready_for_obstacles:
        instr1 = font.render("Press R to add random obstacles", True, (0, 0, 0))
        instr2 = font.render("Press M to add a maze", True, (0, 0, 0))
        screen.blit(instr1, (20, WIDTH + 5))
        screen.blit(instr2, (20, WIDTH + 30))

def main():
    grid = make_grid()
    start = None
    stops = []
    num_stops = 0
    end = None
    running = True
    clock = pygame.time.Clock()
    drawing_obstacle = False
    erasing_obstacle = False
    placing_stops = False
    placing_end = False
    show_instructions = True
    draw_grid(grid)
    num_stops = input_number_modal(WIN, "How many stops?")
    while running:
        draw_grid(grid)
        ready_for_obstacles = (start is not None and len(stops) == num_stops and end is not None)
        draw_instructions(WIN, ready_for_obstacles, show=show_instructions)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_clicked_pos(event.pos)
                if row is None or col is None:
                    continue
                node = grid[row][col]
                if event.button == 1:  # Left click
                    if not start:
                        start = node
                        node.color = START
                        if num_stops == 0:
                            placing_stops = False
                            placing_end = True
                        else:
                            placing_stops = True
                    elif placing_stops and len(stops) < num_stops and node not in [start] + stops:
                        stops.append(node)
                        node.color = STOP
                        if len(stops) == num_stops:
                            placing_stops = False
                            placing_end = True
                    elif placing_end and not end and node not in [start] + stops:
                        end = node
                        node.color = END
                        placing_end = False
                    elif node not in [start] + stops + [end]:
                        node.color = OBSTACLE
                        drawing_obstacle = True
                elif event.button == 3:  # Right click
                    if node.color == OBSTACLE:
                        node.color = BACKGROUND
                        erasing_obstacle = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing_obstacle = False
                elif event.button == 3:
                    erasing_obstacle = False
            if event.type == pygame.MOUSEMOTION:
                row, col = get_clicked_pos(event.pos)
                if row is not None and col is not None:
                    node = grid[row][col]
                    if drawing_obstacle and node not in [start] + stops + [end]:
                        node.color = OBSTACLE
                    elif erasing_obstacle and node.color == OBSTACLE:
                        node.color = BACKGROUND
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start is not None and len(stops) == num_stops and end:
                    show_instructions = False
                    mode = vertical_menu(WIN, "Select Search Algorithm", SEARCH_OPTIONS)
                    draw_grid(grid)
                    pygame.display.update()
                    for row in grid:
                        for node in row:
                            if not node.is_special() and node.color != OBSTACLE:
                                node.color = BACKGROUND
                    points = [start] + stops + [end]
                    for i in range(len(points) - 1):
                        s, t = points[i], points[i + 1]
                        search_colors = SEARCH_COLORS[i % len(SEARCH_COLORS)]
                        if mode == 1:
                            path = bfs_visualize(grid, s, t, lambda: draw_grid(grid), preserve_colors=[PATH], search_colors=search_colors)
                        elif mode == 2:
                            path = bidirectional_bfs(grid, s, t, lambda: draw_grid(grid), preserve_colors=[PATH], search_colors=search_colors)
                        elif mode == 3:
                            path = dfs_visualize(grid, s, t, lambda: draw_grid(grid), preserve_colors=[PATH], search_colors=search_colors)
                        elif mode == 4:
                            path = greedy_best_first_search(grid, s, t, lambda: draw_grid(grid), preserve_colors=[PATH], search_colors=search_colors)
                        elif mode == 5:
                            path = astar_search(grid, s, t, lambda: draw_grid(grid), preserve_colors=[PATH], search_colors=search_colors)
                        else:
                            path = None
                        if path:
                            mark_path(path, lambda: draw_grid(grid))
                        else:
                            display_no_path_message(WIN, WIDTH, WIDTH)
                            break
                elif event.key == pygame.K_c:
                    start = None
                    stops = []
                    num_stops = 0
                    end = None
                    placing_stops = False
                    placing_end = False
                    show_instructions = True
                    grid = make_grid()
                elif event.key == pygame.K_r:
                    if start and len(stops) == num_stops and end:
                        show_instructions = False
                        clear_grid_except_special(grid, start, stops, end)
                        generate_random_obstacles(grid, start, stops, end)
                elif event.key == pygame.K_m:
                    if start and (len(stops) == num_stops) and end:
                        show_instructions = False
                        clear_grid_except_special(grid, start, stops, end)
                        recursive_division_maze_visual(grid, start, stops, end, lambda: draw_grid(grid))
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
