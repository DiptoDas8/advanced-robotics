#!/usr/bin/env python
from __future__ import print_function
from __future__ import division

import sys

sys.path.append("/home/dipto/fastai")

from fastai.imports import *
from fastai.transforms import *
from fastai.conv_learner import *
from fastai.model import *
from fastai.dataset import *
from fastai.sgdr import *
from fastai.plots import *

PATH = '/home/dipto/ros_workspaces/csc790_labs/src/lab06_radeeb/lab06_radeeb_vision/Scripts/barrel/'
arch = resnet34
size = 200

data = ImageClassifierData.from_paths(PATH, tfms=tfms_from_model(arch,size))
learn = ConvLearner.pretrained(arch, data)
learn.precompute = False

learn.load('barrel_model')


trn_fms, val_tfms = tfms_from_model(arch, size)

def run_bob():
	while True:
		image_fullfile = 'cam_img.png'
		try:
			im = val_tfms(open_image(image_fullfile))
		except:
			continue
		preds = learn.predict_array(im[None])
		probs = np.exp(preds)
		print(probs)

		sys.stdout.flush()


if __name__ == '__main__':
	run_bob()
