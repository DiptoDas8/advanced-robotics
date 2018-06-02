#!/usr/bin/env python2.7

from __future__ import print_function, division
from subprocess import Popen, PIPE
from os import environ
import time

image_dir = '/home/dipto/ros_workspaces/csc790_labs/src/lab06/lab06_vision/scripts/tmp/'
image_fnames = sorted([
    'barrel00.png', 'barrel05.png', 'barrel10.png',     'cone03.png',
    'barrel01.png', 'barrel06.png', 'barrel_only.png',  'cone04.png',
    'barrel02.png', 'barrel07.png', 'color_blocks.png', 'construction_barrel.png',
    'barrel03.png', 'barrel08.png', 'cone01.png',       'tulips.jpg',
    'barrel04.png', 'barrel09.png', 'cone02.png'
])

def run(command, env):
    preds = []
    process = Popen(command, stdin=PIPE, stdout=PIPE,
                    shell=True, bufsize=1, universal_newlines=True,
                    env=env, executable='/bin/bash')

    for fname in image_fnames:
        start_time = time.time()

        # Read prompt from fastai_dnn_helper
        print('>>', process.stdout.readline().rstrip('\n'))

        # Send filename to fastai_dnn_helper
        image_fullfile = image_dir + fname
        print('Sending:', image_fullfile)
        print(image_dir + fname, file=process.stdin)
        process.stdin.flush()

        # Read response from fastai_dnn_helper
        x = process.stdout.readline().rstrip('\n')
        # print(x)
        print('>>',x)
        preds.append(x)
        print('Elapsed time:', time.time() - start_time, '\n')

    # Read final prompt and send quit
    process.stdout.readline().rstrip('\n')
    print('quit', file=process.stdin)
    process.stdin.flush()
    return preds

def communicate(l_img, r_img):
    # print(l_img, r_img)
    global image_fnames
    image_fnames = []
    image_fnames.append(l_img)
    image_fnames.append(r_img)

    # print (res)

    return res

def identifier_main():
    fastai_env = environ.copy()
    fastai_env['PATH'] = '/home/dipto/anaconda3/bin:' + fastai_env['PATH']
    fastai_env['PYTHONPATH'] = ''
    run('source activate fastai-cpu && ./fastai_dnn_helper.py', fastai_env)