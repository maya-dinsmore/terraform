import pygame as pg
from os import walk

def load_img(path):
    img = pg.image.load(path).convert_alpha()
    return img

def load_folder(path): # useful for animations with numeric file names 
    imgs = []
    for folder_path, subfolders, file_names in walk(path):
        for name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
            imgs.append(pg.image.load(folder_path + '/' + name).convert_alpha())
    return imgs

def load_folder_dict(path): # key = file name, value = surface, useful for collections of non-animated imgs
    imgs = {}
    for folder_path, subfolders, file_names in walk(path):
        for name in file_names:
            imgs[name.split('.')[0]] = pg.image.load(folder_path + '/' + name).convert_alpha()

    return imgs

def load_subfolders(path): # {'folder name': [surf1, surf2, ...]}
    imgs = {}
    for _, subfolders, __ in walk(path):
        if subfolders:
            for subfolder in subfolders:
                imgs[subfolder] = load_folder(path + '/' + subfolder)
    
    return imgs
