# main.py

import pygame
import sys
import os
import json
import random
from game import FPS, SCREENWIDTH, SCREENHEIGHT, GROUNDY
from player import Player
from pipe import Pipe
from utils import is_collide

HIGHSCORE_FILE = 'data/highscore.json'
GAME_MODES = {
    'Endless': {'pipe_speed': -4, 'gap': 150, 'score_enabled': True,  'double_bird': False, 'pipes': True},
    'Hard':    {'pipe_speed': -6, 'gap': 100, 'score_enabled': True,  'double_bird': False, 'pipes': True},
    'Zen':     {'pipe_speed': 0,  'gap': 0,   'score_enabled': False, 'double_bird': False, 'pipes': False},
    'Double':  {'pipe_speed': -4, 'gap': 150, 'score_enabled': True,  'double_bird': True,  'pipes': True}
}

def load_assets(theme='day'):
    sprites = {
        'numbers':    [pygame.image.load(f'assets/sprites/{i}.png').convert_alpha() for i in range(10)],
        'message':    pygame.image.load('assets/sprites/message.png').convert_alpha(),
        'base':       pygame.image.load('assets/sprites/base.png').convert_alpha(),
        'pipe': (
            pygame.transform.rotate(pygame.image.load('assets/sprites/pipe.png').convert_alpha(), 180),
            pygame.image.load('assets/sprites/pipe.png').convert_alpha()
        ),
        'background': pygame.image.load(f'assets/sprites/background_{theme}.png').convert(),
        'player':     pygame.image.load('assets/sprites/bird.png').convert_alpha(),
        'gameover':   pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    }

    sounds = {
        'die':        pygame.mixer.Sound('assets/audio/die.wav'),
        'hit':        pygame.mixer.Sound('assets/audio/hit.wav'),
        'point':      pygame.mixer.Sound('assets/audio/point.wav'),
        'swoosh':     pygame.mixer.Sound('assets/audio/swoosh.wav'),
        'wing':       pygame.mixer.Sound('assets/audio/wing.wav'),
        'game_over':  pygame.mixer.Sound('assets/audio/game_over.wav')
    }
    return sprites, sounds

def load_high_score():
    os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    with open(HIGHSCORE_FILE) as f:
        return json.load(f).get("high_score", 0)

def save_high_score(score):
    os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump({"high_score": score}, f)

def select_mode(screen, clock):
    font = pygame.font.SysFont('Arial', 30, bold=True)
    modes = list(GAME_MODES.keys()); idx = 0
    while True:
        screen.fill((0,0,0))
        screen.blit(font.render("Select Mode", True, (255,255,255)), (SCREENWIDTH//2-100, 60))
        for i, m in enumerate(modes):
            color = (255,255,0) if i == idx else (255,255,255)
            t = font.render(m, True, color)
            screen.blit(t, (SCREENWIDTH//2 - t.get_width()//2, 150 + i*40))
        pygame.display.update(); clock.tick(30)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN: idx = (idx+1)%len(modes)
                elif e.key == pygame.K_UP: idx = (idx-1)%len(modes)
                elif e.key == pygame.K_RETURN: return modes[idx]

def select_theme(screen, clock):
    font = pygame.font.SysFont('Arial', 28, bold=True)
    themes = ['day','night']; idx = 0
    while True:
        screen.fill((0,0,0))
        screen.blit(font.render("Select Theme", True, (255,255,255)), (SCREENWIDTH//2-100, 60))
        for i, t in enumerate(themes):
            color = (255,255,0) if i == idx else (200,200,200)
            txt = font.render(t.capitalize(), True, color)
            screen.blit(txt, (SCREENWIDTH//2 - txt.get_width()//2, 150 + i*40))
        pygame.display.update(); clock.tick(30)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN: idx = (idx+1)%2
                elif e.key == pygame.K_UP: idx = (idx-1)%2
                elif e.key == pygame.K_RETURN: return themes[idx]

def smooth_transition(screen, from_bg, to_bg, duration=1000):
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    overlay = pygame.Surface((SCREENWIDTH, SCREENHEIGHT)); overlay.blit(to_bg, (0,0))
    while True:
        t = pygame.time.get_ticks() - start
        if t >= duration: break
        alpha = int((t/duration)*255)
        screen.blit(from_bg, (0,0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0,0))
        pygame.display.update(); clock.tick(FPS)

def welcome_screen(screen, sprites, clock):
    px, py = SCREENWIDTH//5, SCREENHEIGHT//2
    mx = (SCREENWIDTH - sprites['message'].get_width())//2
    my = SCREENHEIGHT*0.13
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key in [pygame.K_SPACE, pygame.K_UP]: return
        screen.blit(sprites['background'], (0, 0))
        screen.blit(sprites['player'], (px, py))
        screen.blit(sprites['message'], (mx, my))
        screen.blit(sprites['base'], (0, GROUNDY))
        pygame.display.update(); clock.tick(FPS)

def main_game(screen, sprites, sounds, clock, high_score, mode):
    cfg = GAME_MODES[mode]
    score = 0
    player = Player(SCREENWIDTH//5, SCREENHEIGHT//2, sprites['player'])
    player2 = Player(SCREENWIDTH//2, SCREENHEIGHT//2, sprites['player']) if cfg['double_bird'] else None
    pipes, base_x = [], 0
    base_w = sprites['base'].get_width()

    def newpipe(): return Pipe(sprites['pipe'], sprites['base'], gap=cfg['gap'])
    if cfg['pipes']:
        pipes = [newpipe(), newpipe()]
        pipes[1].upper['x'] += SCREENWIDTH//2; pipes[1].lower['x'] += SCREENWIDTH//2

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if cfg['double_bird']:
                    if e.key == pygame.K_LSHIFT:
                        player.flap(); sounds['wing'].play()
                    elif e.key == pygame.K_RSHIFT and player2:
                        player2.flap(); sounds['wing'].play()
                else:
                    if e.key in [pygame.K_SPACE, pygame.K_UP]:
                        player.flap(); sounds['wing'].play()

        player.move(GROUNDY)
        if player2: player2.move(GROUNDY)

        if cfg['pipes']:
            for p in pipes: p.move(cfg['pipe_speed'])
            if pipes[0].upper['x'] + sprites['pipe'][0].get_width() < 0: pipes.pop(0)
            if pipes[-1].upper['x'] < SCREENWIDTH - 150: pipes.append(newpipe())

            upp = [p.upper for p in pipes]; low = [p.lower for p in pipes]
            collided = is_collide(player, upp, low, sprites, GROUNDY) or (player2 and is_collide(player2, upp, low, sprites, GROUNDY))
            if collided:
                sounds['hit'].play()
                sounds['game_over'].play()
                if cfg['score_enabled'] and score > high_score:
                    high_score = score; save_high_score(high_score)
                pygame.time.wait(500)
                return high_score

            pmid = player.x + sprites['player'].get_width() / 2
            for p in pipes:
                mid = p.upper['x'] + sprites['pipe'][0].get_width() / 2
                if cfg['score_enabled'] and mid <= pmid < mid + 4:
                    score += 1; sounds['point'].play()
        else:
            # Zen mode ground collision
            if player.y + sprites['player'].get_height() >= GROUNDY or (player2 and player2.y + sprites['player'].get_height() >= GROUNDY):
                sounds['hit'].play()
                sounds['game_over'].play()
                pygame.time.wait(500)
                return high_score

        base_x = (base_x - 4) % -base_w
        screen.blit(sprites['background'], (0,0))
        if cfg['pipes']:
            for p in pipes: p.draw(screen)
        screen.blit(sprites['base'], (base_x, GROUNDY))
        screen.blit(sprites['base'], (base_x + base_w, GROUNDY))
        player.draw(screen)
        if player2: player2.draw(screen)

        if cfg['score_enabled']:
            digs = [int(d) for d in str(score)]
            tw = sum(sprites['numbers'][d].get_width() for d in digs)
            x0 = (SCREENWIDTH - tw) / 2
            for d in digs:
                screen.blit(sprites['numbers'][d], (x0, SCREENHEIGHT * 0.08))
                x0 += sprites['numbers'][d].get_width()

        font = pygame.font.SysFont('Arial', 20, bold=True)
        txt = font.render(f"High: {high_score}", True, (255,255,255))
        r = txt.get_rect()
        bg = pygame.Surface((r.width + 16, r.height + 10), pygame.SRCALPHA)
        bg.fill((0,0,0,150))
        screen.blit(bg, (8,8))
        screen.blit(txt, (16,13))

        pygame.display.update(); clock.tick(FPS)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption("Flappy Bird – Theme & Modes")
    clock = pygame.time.Clock()
    high_score = load_high_score()

    while True:
        mode = select_mode(screen, clock)
        theme = select_theme(screen, clock)
        bg_prev = pygame.image.load(f'assets/sprites/background_{"day" if theme=="night" else "night"}.png').convert()
        bg_new  = pygame.image.load(f'assets/sprites/background_{theme}.png').convert()
        smooth_transition(screen, bg_prev, bg_new)
        sprites, sounds = load_assets(theme=theme)
        welcome_screen(screen, sprites, clock)
        high_score = main_game(screen, sprites, sounds, clock, high_score, mode)

if __name__ == "__main__":
    main()
