def dot_cube_collision(dot, cube):
    collideX = dot[0] >= cube.rect.x and cube.rect.x + cube.rect.w >= dot[0]
    collideY = dot[1] >= cube.rect.y and cube.rect.y + cube.rect.h >= dot[1]
    return collideX and collideY