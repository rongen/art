#!/usr/bin/python

# import dicom
import pydicom
# from dicom.errors import InvalidDicomError
from pydicom.errors import InvalidDicomError

import numpy as np
from PIL import Image, ImageDraw

import csv
import os
import random
# import matplotlib.pyplot as plt


def parse_contour_file(filename):
	"""Parse the given contour filename

	:param filename: filepath to the contourfile to parse
	:return: list of tuples holding x, y coordinates of the contour
	"""

	coords_lst = []

	with open(filename, 'r') as infile:
		for line in infile:
			coords = line.strip().split()

			x_coord = float(coords[0])
			y_coord = float(coords[1])
			coords_lst.append((x_coord, y_coord))

	return coords_lst


def parse_dicom_file(filename):
	"""Parse the given DICOM filename

	:param filename: filepath to the DICOM file to parse
	:return: dictionary with DICOM image data
	"""

	try:
#         dcm = dicom.read_file(filename)
		dcm = pydicom.read_file(filename)
		dcm_image = dcm.pixel_array

		try:
			intercept = dcm.RescaleIntercept
		except AttributeError:
			intercept = 0.0
		try:
			slope = dcm.RescaleSlope
		except AttributeError:
			slope = 0.0

		if intercept != 0.0 and slope != 0.0:
			dcm_image = dcm_image*slope + intercept
		dcm_dict = {'pixel_data' : dcm_image}
		return dcm_dict
	except InvalidDicomError:
		return None


def poly_to_mask(polygon, width, height):
	"""Convert polygon to mask

	:param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
	 in units of pixels
	:param width: scalar image width
	:param height: scalar image height
	:return: Boolean mask of shape (height, width)
	"""

	# http://stackoverflow.com/a/3732128/1410871
	img = Image.new(mode='L', size=(width, height), color=0)
	ImageDraw.Draw(img).polygon(xy=polygon, outline=0, fill=1)
	mask = np.array(img).astype(bool)
	return mask


def link_files(link_file):
	# use the link.csv to obtain the number of patients, and to determine which contours belong to which dicom images
	num_patients = -1
	patient_id = []
	contour_id = []
	with open(link_file, 'rb') as linkage:
		for line in linkage:
			num_patients += 1
			if line.split()[0].split(',')[0] != 'patient_id':
				patient_id.append(line.split()[0].split(',')[0])
				contour_id.append(line.split()[0].split(',')[1])
		return num_patients, patient_id, contour_id


def get_contour_files(patient_index, contour_dir):
	contour_list = os.listdir(contour_dir + contour_id[patient_index] + "/i-contours/")
	return(contour_list)


def get_contour_id(contour_list):
	# get the contour id, which refers to the running number that forms part of the contour filename
	contour_files = []
	for i in range(len(contour_list)):
		contour_files.append(contour_list[i][8:12].lstrip("0"))
	return(contour_files)


def get_dicom_files(contour_ids, patient_index, dicom_dir):
	# given the contour id, we can find the corresponding dicom file
	dicom_with_contour = []
	for i in range(len(contour_ids)):
		dicom_with_contour.append(dicom_dir + patient_id[patient_index] + "/" + contour_ids[i] + ".dcm")
	return(dicom_with_contour)


def parse_ct_file(contour_list, patient_index, dicom_with_contour, contour_dir, img_size_x, img_size_y):
	# obtain boolean mask based on contour
	parsed_contours = []
	for i in range(len(contour_list)):
		single_contour = parse_contour_file(contour_dir + contour_id[patient_index] + "/i-contours/" + contour_list[i])
		boolean_mask = poly_to_mask(single_contour, img_size_x, img_size_y)
		parsed_contours.append([str(contour_id[patient_index] + "/" + contour_list[i]), parse_dicom_file(dicom_with_contour[i])['pixel_data'], boolean_mask])
	return parsed_contours


def split_into_batches(data, batch_size):
	# randomly split the dataset into batches
	array = np.array(data, dtype = 'object')
	number_of_batches = int(np.ceil(len(data) / batch_size))
	batched_data = np.zeros(number_of_batches, dtype = 'object')
	for i in range(number_of_batches):
		batched_data[i] = [array[i * batch_size : (i + 1) * batch_size, 1], array[i * batch_size : (i + 1) * batch_size, 2]]
	return batched_data

	
def parse_data(dicom_dir, contour_dir, batch_size):
	# Part 1
	parsed = []
	for patient_index in range(num_patients):
		contour_list = get_contour_files(patient_index, contour_dir)
		contour_ids = get_contour_id(contour_list)
		dicom_with_contour = get_dicom_files(contour_ids, patient_index, dicom_dir)
		
		# obtain dicom image dimensions
		img_size_x = pydicom.dcmread(dicom_with_contour[0]).pixel_array.shape[0]
		img_size_y = pydicom.dcmread(dicom_with_contour[0]).pixel_array.shape[1]
		parsed.extend(parse_ct_file(contour_list, patient_index, dicom_with_contour, contour_dir, img_size_x, img_size_y))
		
	# Part 2
	np.random.seed = 0
	np.random.shuffle(parsed)
	batched_data = split_into_batches(parsed, batch_size)
	return batched_data


if __name__ == '__main__':
	num_patients, patient_id, contour_id = link_files("final_data/link.csv")
	batched_data = parse_data("final_data/dicoms/", "final_data/contourfiles/", 8)
	print('The data has been split into batches of dicom images and boolean masks:')
	print(batched_data)
	print('All done!')