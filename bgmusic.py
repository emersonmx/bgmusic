#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import shlex
import subprocess
import click

CONFIG_ROOT_PATH = os.path.join(os.path.expandvars('$HOME'), '.config/bgmusic')
CONFIG_PATH = os.path.join(CONFIG_ROOT_PATH, 'config.json')
PLAYLIST_PATH = os.path.join(CONFIG_ROOT_PATH, 'playlist.m3u')
DEFAULT_CONFIG = {
    'player': '/usr/bin/mpv',
    'args': '--volume=40 -vo=null --save-position-on-quit -shuffle --playlist={playlist}'
}

def _get_musics():
    with open(PLAYLIST_PATH, 'r') as f:
        return set([l.strip() for l in f.readlines()])
    return set()

def _save_musics(musics):
    with open(PLAYLIST_PATH, 'w') as f:
        for music in musics:
            f.write(music.strip() + '\n')

@click.group()
@click.pass_context
def cli(ctx):
    '''Script to play background musics.'''

    if not os.path.exists(CONFIG_ROOT_PATH):
        os.mkdir(CONFIG_ROOT_PATH)

    config = DEFAULT_CONFIG
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            loaded_config = json.load(f)
            config = {**DEFAULT_CONFIG, **loaded_config}

    if not os.path.exists(PLAYLIST_PATH):
        with open(PLAYLIST_PATH, 'a') as f:
            os.utime(PLAYLIST_PATH, None)

    ctx.obj = config

@cli.command()
@click.pass_context
def play(ctx):
    '''Play musics.'''

    musics = _get_musics()
    if not musics:
        click.echo('Empty music list.')
        return

    config = ctx.obj
    player = config['player']
    args = shlex.split(config['args'].format(playlist=PLAYLIST_PATH))
    subprocess.run([player, *args])

@cli.command(name='list')
@click.pass_context
def list_musics(ctx):
    '''List musics.'''
    musics = _get_musics()
    if not musics:
        click.echo('Empty music list.')
        return
    for i, music in enumerate(musics):
        click.echo('[{}] {}'.format(i+1, music))

@cli.command()
@click.argument('music', type=click.Path())
@click.pass_context
def add(ctx, music):
    '''Add music.'''
    music_path = os.path.realpath(music)

    musics = _get_musics()
    musics.add(music_path)
    _save_musics(musics)

    click.echo('"{}" added to playlist'.format(music))

@cli.command()
@click.option('--index', type=int, help='Index to remove')
@click.option('--all', is_flag=True, help='Remove ALL musics')
@click.pass_context
def remove(ctx, index, all):
    '''Remove music.'''
    if all:
        if click.confirm('Remove ALL musics?'):
            _save_musics([])
        return

    size = 0
    musics = list(_get_musics())

    if not musics:
        click.echo('Empty music list.')
        return

    if not index:
        ctx.invoke(list_musics)
        index = click.prompt('Music to remove', type=int)

    if 0 < index <= len(musics):
        del musics[index - 1]
        _save_musics(musics)
    else:
        raise click.UsageError('Invalid music')

if __name__ == '__main__':
    cli()
