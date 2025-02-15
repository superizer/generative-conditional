import os
import cv2
import glob
import torch
import imageio
import numpy as np
import pandas as pd
import seaborn as sn
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from scipy.io import wavfile
from PIL import Image

def set_lr(optimizer, lrs):
	if(len(lrs) == 1):
		for param in optimizer.param_groups:
			param['lr'] = lrs[0]
	else:
		for i, param in enumerate(optimizer.param_groups):
			param['lr'] = lrs[i]

def get_lr(optimizer):
	optim_param_groups = optimizer.param_groups
	if(len(optim_param_groups) == 1):
		return optim_param_groups[0]['lr']
	else:
		lrs = []
		for param in optim_param_groups:
			lrs.append(param['lr'])
		return lrs

def histogram_sizes(img_dir, h_lim = None, w_lim = None):
	hs, ws = [], []
	for file in glob.iglob(os.path.join(img_dir, '**/*.*')):
		try:
			with Image.open(file) as im:
				h, w = im.size
				hs.append(h)
				ws.append(w)
		except:
			print('Not an Image file')

	if(h_lim is not None and w_lim is not None):
		hs = [h for h in hs if h<h_lim]
		ws = [w for w in ws if w<w_lim]

	plt.figure('Height')
	plt.hist(hs)

	plt.figure('Width')
	plt.hist(ws)

	plt.show()

	return hs, ws

def generate_noise(bs, nz, device):
	noise = torch.randn(bs, nz, 1, 1, device = device)
	return noise

def plot_multiple_images(images, h, w):
	fig = plt.figure(figsize=(8, 4))
	for i in range(1, h*w+1):
		img = images[i-1]
		fig.add_subplot(h, w, i)
		if(img.shape[2] == 1):
			img = img.reshape(img.shape[0], img.shape[1])
		#plt.axis('off')
		#plt.subplots_adjust(hspace=0, wspace=0)
		plt.axis('off')
		plt.imshow(img, cmap = 'gray', aspect='auto')
	#plt.axis('off')
	plt.subplots_adjust(hspace=0, wspace=0)
	plt.show()
	return fig

def save(filename, netD, netG, optD, optG):
	state = {
		'netD' : netD.state_dict(),
		'netG' : netG.state_dict(),
		'optD' : optD.state_dict(),
		'optG' : optG.state_dict()
	}
	torch.save(state, filename)

def load(filename, netD, netG, optD, optG):
	state = torch.load(filename)
	netD.load_state_dict(state['netD'])
	netG.load_state_dict(state['netG'])
	optD.load_state_dict(state['optD'])
	optG.load_state_dict(state['optG'])

def save_fig(filename, fig):
	fig.savefig(filename)

def get_sample_images_list(mode, inputs):
	if(mode == 'Conditional'):
		fixed_noise, fixed_one_hot_labels, n_classes, netG = inputs[0], inputs[1], inputs[2], inputs[3]
		with torch.no_grad():
			sample_fake_images = netG(fixed_noise, fixed_one_hot_labels).detach().cpu().numpy()
			sample_images_list = []
			for j in range(28): #(n_classes):
				cur_img = (sample_fake_images[j] + 1) / 2.0
				sample_images_list.append(cur_img.transpose(1, 2, 0))

	return sample_images_list