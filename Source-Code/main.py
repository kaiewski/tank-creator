#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import sys
import random
import time

sys.path.insert(0, '../sources')

from tiles import *
from enemies import *
from shadows import *
from object_settings import *

pygame.init()

WIDTH = 1280
HEIGHT = 720
size = [WIDTH, HEIGHT]
win = pygame.display.set_mode((size), pygame.RESIZABLE)
pygame.display.set_caption(f"|  Tanks Creator  |")

clock = pygame.time.Clock()
game = True
FPS = 48

cam_x, cam_y = WIDTH/2, HEIGHT/2
x = y = 0

tiles = []
TILE_W, TILE_H = 64, 64

tick = 0
last_fps = 0
max_fps = 0
cent_fps = []
res_fps = 0

pygame.mouse.set_visible(False)

def collide_on_coordinates(objects, mouse_x, mouse_y, rect=None):
	if type(objects) == list:
		col_list = []
		if rect != None:
			for obj in objects:
				if rect.collidepoint((obj.rect.x, obj.rect.y)):
					col_list.append(obj)		
		else:
			for obj in objects:
				if obj.rect.collidepoint((mouse_x, mouse_y)):
					col_list.append(obj)
		return col_list		
	else:
		if objects.collidepoint((mouse_x, mouse_y)):
			return objects
	return False

def quick_sort(arr):
	if len(arr) <= 1:
		return arr
	pivot = arr[len(arr) // 2]
	left = [x for x in arr if x.tile_name < pivot.tile_name]
	middle = [x for x in arr if x.tile_name == pivot.tile_name]
	right = [x for x in arr if x.tile_name > pivot.tile_name]

	return quick_sort(left) + middle + quick_sort(right)

def save_level(objects_without, ground, cam_x, cam_y, screen_w, screen_h, offset_x, offset_y):
	try:
		with open('saves/saved_level', 'w+') as file:
			objects_without = quick_sort(objects_without)
			for tile in ground:
				file.write(f'{tile.rect.x} {tile.rect.y} {tile.rect.w} {tile.rect.h} {tile.angle} {tile.tile_name}|')			
			for obj in objects_without:
				if objects_without.index(obj) < len(objects_without)-1:
					file.write(f'{obj.rect.x} {obj.rect.y} {obj.rect.w} {obj.rect.h} {obj.angle} {obj.tile_name}|')
				else:
					file.write(f'{obj.rect.x} {obj.rect.y} {obj.rect.w} {obj.rect.h} {obj.angle} {obj.tile_name}')
			file.write(f'\n{cam_x, cam_y}'.replace('(','').replace(')',''))
			file.write(f'\n{screen_w, screen_h}'.replace('(','').replace(')',''))
			file.write(f'\n{offset_x, offset_y}'.replace('(','').replace(')',''))

	except FileNotFoundError:
		with open('saves/saved_level', 'r+') as file:
			pass
	print('Saved at: ./saves with name "saved_level"')

def load_level(path):
	try:		
		with open(path, 'r+') as file:
			data = file.read().split('\n')
			tiles = data[0].split('|')

			camera = data[-3].strip().replace('.0', '').replace(' ', '').split(',')
			screen = data[-2].strip().split(',')
			offset = data[-1].strip().split(',')
			rect_list = []
			health = None

			for i in tiles:
				tile = i.split(' ')

				x = int(tile[0])
				y = int(tile[1])
				width = int(tile[2])
				height = int(tile[3])
				angle = int(tile[4])
				if obj_to_health[tile[5]] != None:
					health = int(obj_to_health[tile[5]])

				image_directory = f'../images/tiles/{tile[5].lower()}.png'
				if tile[5] in enemies_to_list:
					if tile[5] == 'Turret':
						new_object = Tile(x, y, width, height, '../images/tiles/enemies/static_turret/static_turret_gun.png', tile[5], angle)
					if tile[5] == 'Machinegun':
						new_object = Tile(x, y, width, height, '../images/tiles/enemies/machinegun/machinegun_gun.png', tile[5], angle)
					if tile[5] == 'Launcher':
						new_object = Tile(x, y, width, height, '../images/tiles/enemies/grenade_launcher/grenade_launcher_gun.png', tile[5], angle)
				else:
					new_object = Tile(x, y, width, height, image_directory, tile[5], angle)

				new_object.health = health
				rect_list.append(new_object)

			cam_x, cam_y = int(camera[0]), int(camera[1])
			screen_w, screen_h = int(screen[0]), int(screen[1])
			offset_x, offset_y = float(offset[0]), float(offset[1])
			return (rect_list, cam_x, cam_y, screen_w, screen_h, offset_x, offset_y)

	except Exception as e:

		print(f'Error in Function load_level: ', e)
		return [], 0, 0, 0, 0, 0, 0

level_info = load_level('saves/saved_level')
if level_info[0] != []:
	[tiles, cam_x, cam_y, WIDTH, HEIGHT, offset_x, offset_y] = level_info
	
ground_tile = Tile(0,0,64,64,'../images/tiles/ground.png', 'Ground')
water_tile = Tile(0,0,64,64,'../images/tiles/water.png', 'Water')
bush_tile = Tile(0,0,64,64,'../images/tiles/bush.png', 'Bush')
wall_tile = Tile(0,0,64,64,'../images/tiles/wall.png', 'Wall')
box_tile = Tile(0,0,64,64,'../images/tiles/box.png', 'Box')
ammo_box_tile = Tile(0,0,64,64,'../images/tiles/ammo_box.png', 'Ammo_Box')
brick_tile = Tile(0,0,64,64,'../images/tiles/brick.png', 'Brick')
tank_tile = Tile(0,0,64,64,'../images/tiles/tank_spawn.png', 'Tank_Spawn')
turret_tile = Tile(0,0,64,64,'../images/tiles/enemies/static_turret/static_turret_gun.png', 'Turret')
machinegun_tile = Tile(0,0,64,64,'../images/tiles/enemies/machinegun/machinegun_gun.png', 'Machinegun')
launcher_tile = Tile(0,0,64,64,'../images/tiles/enemies/grenade_launcher/grenade_launcher_gun.png', 'Launcher')
finish_tile = Tile(0,0,64,64,'../images/tiles/finish.png', 'Finish')
rock_tile = Tile(0,0,64,64,'../images/tiles/rocks.png', 'Rocks')
asphalt_tile = Tile(0,0,64,64,'../images/tiles/asphalt.png', 'Asphalt')
barricade_tile = Tile(0,0,64,64,'../images/tiles/barricade.png', 'Barricade')
barricade_falled_tile = Tile(0,0,64,64,'../images/tiles/barricade_falled.png', 'Barricade_Falled')
mine_tile = Tile(0,0,64,64,'../images/tiles/mine.png', 'Mine')
manhole_tile = Tile(0,0,64,64,'../images/tiles/manhole.png', 'Manhole')

new_obj_tile = ground_tile
tiles_obj = [
			ground_tile, 
			water_tile, 
			bush_tile, 
			wall_tile, 
			box_tile, 
			brick_tile, 
			tank_tile, 
			turret_tile, 
			finish_tile, 
			machinegun_tile, 
			launcher_tile, 
			rock_tile, 
			asphalt_tile, 
			barricade_tile, 
			barricade_falled_tile, 
			mine_tile, 
			ammo_box_tile,
			manhole_tile
			]

dy = 0
dx = 0
angle = 0
ctrl_is_down = False

for tile in tiles_obj:
	tile.rect.y += dy 
	tile.rect.x += dx
	dy += 75
	if (dy  > 600):
		dy = 0
		dx = 75
	
if __name__ == '__main__':
	while game:
		prev_cam_x, prev_cam_y = cam_x, cam_y
		if cam_x != 0 and cam_y != 0:
			offset_x = (cam_x % TILE_W)
			offset_y = (cam_y % TILE_H)

		key = pygame.key.get_pressed()
		mouse = pygame.mouse.get_pressed()
		mouse_move = pygame.mouse.get_rel() 
		mouse_x, mouse_y = pygame.mouse.get_pos()
		start_time = time.time()
		shadows = []
		tick += 1

		if mouse[0] and pygame.mouse.get_visible():
			mx, my = pygame.mouse.get_pos()
			collision = collide_on_coordinates(tiles_obj, mx, my)
			if collision == False or collision == []:
				collision = collide_on_coordinates(tiles, mx, my)
			if collision != False and collision != []:
				new_obj_tile = Tile(collision[0].rect.x, collision[0].rect.y, collision[0].rect.w, collision[0].rect.h, collision[0].image_directory, collision[0].tile_name, angle)
				TILE_W = new_obj_tile.rect.w
				TILE_H = new_obj_tile.rect.h
				angle = 0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
				sys.exit()
				game = False

			if event.type == pygame.VIDEORESIZE:
				WIDTH, HEIGHT = pygame.display.get_surface().get_size()
				size = [WIDTH, HEIGHT]

			if event.type == pygame.MOUSEMOTION and mouse[1]:
				cam_x -= prev_cam_x - cam_x + mouse_move[0]
				cam_y -= prev_cam_y - cam_y + mouse_move[1]

			if event.type == pygame.MOUSEMOTION and not(mouse[1]):
				x = int(mouse_x / 64)
				y = int(mouse_y / 64)
				x = x * 64 - offset_x
				y = y * 64 - offset_y

			if mouse[0] and not(mouse[1]) and not(pygame.mouse.get_visible()):
				x = int(mouse_x / 64)
				y = int(mouse_y / 64)
				x = x * 64 - offset_x
				y = y * 64 - offset_y
				collision = collide_on_coordinates(tiles, x,y+TILE_H/2)

				if collision:
					for i in collision:
						if new_obj_tile.tile_name in non_full_objects:
							col = collide_on_coordinates(tiles, x,y+TILE_H/2)
							for obj in col:
								del tiles[tiles.index(obj)]

							if i.tile_name == "Ground":
								new_tile = Tile(x, y+TILE_H/2, TILE_W, TILE_H, "../images/tiles/ground.png", "Ground", 0)
								tiles.append(new_tile)

							if i.tile_name == "Asphalt":
								new_tile = Tile(x, y+TILE_H/2, TILE_W, TILE_H, f"../images/tiles/asphalt.png", "Asphalt", 0)
								tiles.append(new_tile)

							new_tile = Tile(x, y+TILE_H/2, TILE_W, TILE_H, new_obj_tile.image_directory, new_obj_tile.tile_name, angle)
							tiles.append(new_tile)
						else:
							del tiles[tiles.index(i)]
							new_tile = Tile(x, y+TILE_H/2, TILE_W, TILE_H, new_obj_tile.image_directory, new_obj_tile.tile_name, angle)
							tiles.append(new_tile)						

				if not(collision):
					new_tile = Tile(x, y+TILE_H/2, TILE_W, TILE_H, new_obj_tile.image_directory, new_obj_tile.tile_name, angle)
					tiles.append(new_tile)

			if mouse[2] and not(pygame.mouse.get_visible()):
				rect = pygame.Rect(x,y+new_obj_tile.rect.h/4, new_obj_tile.rect.w, new_obj_tile.rect.h)
				collision = collide_on_coordinates(tiles, x, y, rect)
				if collision:
					for i in collision:
						del tiles[tiles.index(i)]

			if event.type == pygame.KEYUP: 
				if event.key == pygame.K_s:
					ground_tiles = []
					tiles_without_ground = []
					for i in tiles:
						if i.tile_name == "Ground":
							ground_tiles.append(i)
						else:
							tiles_without_ground.append(i)

					save_level(tiles_without_ground, ground_tiles, cam_x, cam_y, WIDTH, HEIGHT, offset_x, offset_y)
				if event.key == pygame.K_r:
					angle -= 90
					if angle < -360:
						angle = -90
					new_img = pygame.transform.rotate(new_obj_tile.image, (-90))
					new_obj_tile.image = new_img
					new_obj_tile.rect = pygame.Rect(new_obj_tile.image.get_rect())

			if event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL:
				pygame.mouse.set_visible(True)
				ctrl_is_down = True
			if event.type == pygame.KEYUP and event.key == pygame.K_LCTRL:
				pygame.mouse.set_visible(False)
				ctrl_is_down = False

		for tile in tiles:
			tile.check_visibility(WIDTH, HEIGHT)

		visible_tiles = [tile for tile in tiles if tile.visibility]

		mouse_x -= cam_x
		mouse_y -= cam_y

		for rect in tiles:
			rect.rect.x += prev_cam_x - cam_x
			rect.rect.y += prev_cam_y - cam_y

		win.fill((250,80,0))

		for tile in visible_tiles:
			if tile.tile_name in non_shadow_objects:
				win.blit(tile.image, (tile.rect.x, tile.rect.y, tile.rect.w, tile.rect.h))

		for tile in visible_tiles:
			if not(tile.tile_name in non_shadow_objects):
				new_shadow = Shadow(tile.rect.x, tile.rect.y+tile.rect.h-2, tile.rect.w, tile.rect.h/4, (0,0,0,64))
				shadows.append(new_shadow)

		for shadow in shadows:
			shadow.draw(win)

		for tile in visible_tiles:
			if not(tile.tile_name in non_shadow_objects):
				win.blit(tile.image, (tile.rect.x, tile.rect.y, tile.rect.w, tile.rect.h))

		if not(pygame.mouse.get_visible()):
			win.blit(new_obj_tile.image, (x,y+TILE_H/2, TILE_W, TILE_H))
			pygame.draw.rect(win, (255,0,0), (x+16,y+16+TILE_H/2,32,32))

		if ctrl_is_down:
			for tile in tiles_obj:
				tile.draw(win)

		if tick // FPS and time.time() != start_time:
			if max_fps < last_fps:
				max_fps = last_fps
			cent_fps.append(last_fps)

			for i in range(len(cent_fps)):
				res_fps += cent_fps[i-1]
			res_fps //= len(cent_fps)
			pygame.display.set_caption(f"|  Tanks Creator  |      FPS: {int(1.0 / (time.time() - start_time))}       Max: {max_fps}      Average: {res_fps}       Objects: {len(tiles)}")
			last_fps = int(1.0 / (time.time() - start_time))
			tick = 0

		pygame.display.update()
		clock.tick(FPS)

