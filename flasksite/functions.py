from flasksite.models import User, Post, Container, Packing, Box, ContainerInstance, BoxInstance
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flasksite import app, db, bcrypt
import os
import pickle
import numpy as np
import sys

def generate_boxes(packing_id):
	a = 0
	#container = Container.query.filter_by(packing_id=packing_id).first()
	boxes = Box.query.filter_by(packing_id=packing_id).all()
	for b in boxes:
		for i in range(b.quantity):
			box_instance = BoxInstance(name=b.name, box_id = b.id, x=b.x, y=b.y, z=b.z, packed=0, weight=b.weight,
				  r_x = b.r_x, r_y = b.r_y, r_z = b.r_z, packing_id=packing_id)#todo hozzáadni a forgatási változókat, lehet azok kellenek
			db.session.add(box_instance)
			db.session.commit()
			a += 1

#create container
def create_container_instance(packing_id):

	container = Container.query.filter_by(packing_id=packing_id).first()

	x = container.x
	y = container.y
	z = container.z
	container_id = container.id
	weight_remaining = container.max_weight
	max_weight = container.max_weight
	space_remaining = x*y*z#köbcenti lesz
	container_instance = ContainerInstance(packing_id=packing_id, container_id=container_id, x=x, y=y, z=z,
										   space_remaining=space_remaining, weight_remaining=weight_remaining, max_weight=max_weight)
	db.session.add(container_instance)
	db.session.commit()
	#name = container.name
	container_instance_id = container_instance.instance_id
	#print(container_instance.instance_id, file=sys.stderr)
	array_boxes = np.zeros((int(x / 10), int(y / 10), int(z / 10)), dtype='int') #milliméter
	filename = "instance" + str(container_instance_id) + ".pkl"
	directory = 'containers/containers_' + str(packing_id)
	if not os.path.exists(directory):
		os.makedirs(directory)
	container_instance_id += 1

	path = directory + "/" + filename
	pickle.dump(array_boxes, open(path, "wb"))
	return path

	# pickle.dump(boxes_in, open(path_box, "wb"))

	# box_p = pickle.load(open(path_box), "rb")
	#data_p = pickle.load(open(path, "rb"))
	#full_weight = data_p[1][1][1]

#sort boxes -> dobozok rendezett listájával tér vissza

#sort containers by remaining space
#count remaining space
#updatepickle and boxinstance and containerinstance

def create_states(box):
	states = []
	#todo maybe get rid of the duplicated states, also check whether the side is banned
	#box.states[s][name] = "yzx"
	box_s = [0, 0, 0]
	#box.shape[2]#120
	#boxj = box.shape[1]
	i = 0
	#boxk = box.shape[0]
	if(box.r_z == False):
		states.append([box.x, box.y, box.z])
		i += 1
		box_s[0] = box.x
		box_s[1] = box.y
		box_s[2] = box.z

	#states.append(box_s)
	if (box.r_y == False):
		states.append([box.x, box.z, box.y])
		i += 1
		box_s[0] = box.x
		box_s[1] = box.z
		box_s[2] = box.y

	#states.append(box_s)
	if (box.r_z == False):
		states.append([box.y, box.x, box.z])
		i += 1
		box_s[0] = box.y
		box_s[1] = box.x
		box_s[2] = box.z

	#states.append(box_s)
	if (box.r_x == False):
		states.append([box.y, box.z, box.x])
		i += 1
		box_s[0] = box.y
		box_s[1] = box.z
		box_s[2] = box.x

	#states.append(box_s)
	if (box.r_y == False):
		states.append([box.z, box.x, box.y])
		i += 1
		box_s[0] = box.z
		box_s[1] = box.x
		box_s[2] = box.y

	#states.append(box_s)
	if (box.r_x == False):
		states.append([box.z, box.y, box.x])
	#i += 1
		box_s[0] = box.z
		box_s[1] = box.y
		box_s[2] = box.x

	#egyedi állapotok csak, így gyorsul
	for s in range(len(states)):
		for b in range(len(states)-1-s):
			if states[s] == states[s+b]:
				states.pop(s+b)
				break


	#states.append(box_s)
	print(len(states), file=sys.stderr)
	print("rovid", file=sys.stderr)
	np.vstack(set(map(tuple, states)))
	print(len(states), file=sys.stderr)
	return states


def putbox(container, box, container_path, id):  # box_id
	#mukodo funkcio, tesztelesnel majd be lehet kapcsolni, most meg zavaro
	if(container.weight_remaining<box.weight):return False
	if(container.space_remaining<(box.x*box.y*box.z)): return False
	#todo space remaining ellenőrzése még itt

	states = create_states(box)
	#print(states)
	with open(container_path, 'rb') as f:
		container_array = pickle.load(f)
	z = container_array.shape[2]#cols
	y = container_array.shape[1]#rows
	x = container_array.shape[0]#z

	#boxi = box.shape[2]  # 120
	#boxj = box.shape[1]
	#boxk = box.shape[0]

	i = 0
	j = 0
	k = 0
	#location = {"x_start": 0,
	#			"x_end": 0,
	#			"y_start": 0,
	#			"y_end": 0,
	#			"z_start": 0,
	#			"z_end": 0,
	#			"id": 0 }

			#print(container)

	while k < z:
		j = 0
		while j < y:
			while i < x:
					#print("belso while" + str(i) + str(j) + str(k))
					#input("jajjajj")
				if container_array[i][j][k] == 0:
					for s in states:
						#print(s, file=sys.stderr)
						if k + round(s[2]/10) <= z and j + round(s[1]/10) <= y and i + round(s[0]/10) <= x:  # ilyen kell majd minden forgatáshoz és ami alatta van


							if np.any(container_array[i:i + round(s[0]/10), [range(j, j + round(s[1]/10))], k:k + round(s[2]/10)]) == False:
									#print("itt isvvvvvvvvvvvvvvvvv")
									# itt vegul beadja a kettest oda is, ahova nem fer be
									#print(container[i:i + s[2], [range(j, j + s[1])], k:k + s[0]])
									#print("vege" + str(i) + str(j) + str(k))
								container_array[i:i + round(s[0]/10), [range(j, j + round(s[1]/10))], k:k + round(s[2]/10)] = 2
									#print(container)
									#input()
								#a = {"a":1, 'b':2}
								#location['x_start'] = i

								print(id, file=sys.stderr)
								#location['x_end'] = i + round(s[0]/10)#todo nem biztos hogy ezek kellenek ide
								#location['y_start'] = j
								#location['y_end'] = j + round(s[1]/10)
								#location['z_start'] = k
								#location['z_end'] = k + round(s[2]/10)
								#location['id'] = id
								#box_locations.append(location)
								box.x_start = i
								box.x_end = i + round(s[0]/10)
								print("x_start = " + str(box.x_start), file=sys.stderr)
								box.y_start = j
								box.y_end = j + round(s[1]/10)
								box.z_start = k
								box.z_end = k + round(s[2]/10)
								box.container_instance_id = id
								box.packed = 1
								container.weight_remaining -= box.weight
								container.space_remaining -= (box.x*box.y*box.z)
								db.session.commit()
								pickle.dump(container_array, open(container_path, "wb"))
								return True
				i += 1

			j += 1
			i = 0

		k += 1
		i = 0
	return False
	#return a