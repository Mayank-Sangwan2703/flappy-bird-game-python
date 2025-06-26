def is_collide(player, upper_pipes, lower_pipes, sprites, ground_y):
    if player.y > ground_y - 25 or player.y < 0:
        return True

    player_rect = sprites['player'].get_rect(topleft=(player.x, player.y))
    player_rect.inflate_ip(-10, -10)  

    for pipe in upper_pipes:
        pipe_rect = sprites['pipe'][0].get_rect(topleft=(pipe['x'], pipe['y']))
        pipe_rect.inflate_ip(-5, -5) 
        if player_rect.colliderect(pipe_rect):
            return True

    for pipe in lower_pipes:
        pipe_rect = sprites['pipe'][1].get_rect(topleft=(pipe['x'], pipe['y']))
        pipe_rect.inflate_ip(-5, -5)
        if player_rect.colliderect(pipe_rect):
            return True

    return False
