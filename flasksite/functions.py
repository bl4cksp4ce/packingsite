from flasksite.models import User, Post, Container, Packing, Box, ContainerInstance, BoxInstance
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flasksite import app, db, bcrypt
import os
import pickle
import numpy as np
import sys

def generate_boxes(packing_id):
	a = 0
	#print(a)
	#container = Container.query.filter_by(packing_id=packing_id).first()
	boxes = Box.query.filter_by(packing_id=packing_id).all()
	#packing = Packing.query.get_or_404(packing_id)
	for b in boxes:#itt a quantityt kell nézni, ami még nincs a box modellben és annyi kell belőle, most mindből csak egyet csinál, belül lehet még egy for ami nullától a quantityig megy
		for i in range(b.quantity):
			box_instance = BoxInstance(name=b.name, x=b.x, y=b.y, z=b.z, packed=0, weight=b.weight,
				  packing_id=packing_id)
			db.session.add(box_instance)
			db.session.commit()
			a +=1

#create container
def create_container_instance(packing_id):
	#a = 0
	container = Container.query.filter_by(packing_id=packing_id).first()

	#container_type = container.id
	#packing_id = packing_id
	#create container instance as well
	x = container.x
	y = container.y
	z = container.z
	container_id = container.id
	weight_remaining = container.max_weight
	space_remaining = x*y*z/1000#köbcenti lesz
	container_instance = ContainerInstance(packing_id=packing_id, container_id=container_id, x=x, y=y, z=z,
										   space_remaining=space_remaining, weight_remaining=weight_remaining)
	db.session.add(container_instance)
	db.session.commit()
	#name = container.name
	container_instance_id = container_instance.instance_id
	print(container_instance.instance_id, file=sys.stderr)
	array_boxes = np.zeros((int(x / 10), int(y / 10), int(z / 10)), dtype='int') #milliméter
	filename = "instance" + str(container_instance_id) + ".pkl"
	directory = 'containers/containers_' + str(packing_id)
	if not os.path.exists(directory):
		os.makedirs(directory)
	container_instance_id += 1  # for the next instance

	path = directory + "/" + filename
	pickle.dump(array_boxes, open(path, "wb"))  # létrejön példányoításkor, címeiket valahol tárolni kéne
	return path

	# pickle.dump(boxes_in, open(path_box, "wb"))

	# box_p = pickle.load(open(path_box), "rb")
	#data_p = pickle.load(open(path, "rb"))
	#full_weight = data_p[1][1][1]

#sort boxes -> dobozok rendezett listájával tér vissza

#sort containers by remaining space
#count remaining space
#updatepickle and boxinstance and containerinstance

'''def putbox(container, box, container_path):
	with open(container_path, 'rb') as f:
		# load using pickle de-serializer
		container_array = pickle.load(f)

	#container_array = pickle.load(open(container_path), "rb")

	cols = container.y
	rows = container.z
	z = container.x


	id = box.id
	boxi = box.y
	boxj = box.z
	boxk = box.x

	i = 0
	j = 0
	k = 0
	#print(container)

	while i < cols:
		j = 0
		while j < rows:
			while k < z:
			#print(arr[i][j])
				#print("eleje" + str(i) + str(j) + str(k))
				#input("jajjajj")
				if container_array[i][j][k] == 0:
					#if (i, j, k) == (0, 2, 2) :
							#print(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk])
							#megtalálja ezt
							#input("seggfasz")
							#print(cols, i+boxi, rows, j+boxj, z, k+boxk)
					if i + boxi <= z and j + boxj <= rows and k + boxk <= cols: #kicsereltem colt zvel most jo
						#print("segg")
						#itt romlik el
						#print("eleje" + str(i) + str(j) + str(k))
						#if (i, j, k) == (0, 2, 2) :
							#print(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk])
							#input("seggfasz2")

						if np.any(container_array[i:i+boxi, [range(j, j+boxj)], k:k+boxk]) == False :
							#print("itt isvvvvvvvvvvvvvvvvv")
							#itt vegul beadja a kettest oda is, ahova nem fer be
							#print(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk])
							#print("vege" + str(i) + str(j) + str(k))
							container_array[i:i+boxi, [range(j, j+boxj)], k:k+boxk] = id
							pickle.dump(container_array, open(container_path, "wb"))
							#print(container)
							#input()
							return True
						#else :
							#print(arr[i][j])
							#print("g")
							#while container[i][j][k] == 0:###
								#print(i,j)
								#k +=1
								#if i == rows or j == cols:
									#print(str(i)+ "rows")
									#break
							#print('itt nem')
							#print(str(i) + " " + str(x[i]))
							#i += 1
					#else: k +=1
				#if k < z : k += 1
				k += 1
			#print("vege" + str(i) + str(j) + str(k))
			#input()
			j += 1
			k = 0
			#print("ittaj")
		i += 1
		k = 0'''
def create_states(box):
	states = []
	#box.states[s][name] = "yzx"
	box_s = [0, 0, 0]
	#box.shape[2]#120
	#boxj = box.shape[1]
	#boxk = box.shape[0]
	box_s[0] = box.x
	box_s[1] = box.y
	box_s[2] = box.z

	states.append(box_s)
	box_s[0] = box.x
	box_s[1] = box.z
	box_s[2] = box.y

	states.append(box_s)
	box_s[0] = box.y
	box_s[1] = box.x
	box_s[2] = box.z

	states.append(box_s)
	box_s[0] = box.y
	box_s[1] = box.z
	box_s[2] = box.x

	states.append(box_s)
	box_s[0] = box.z
	box_s[1] = box.x
	box_s[2] = box.y

	states.append(box_s)
	box_s[0] = box.z
	box_s[1] = box.y
	box_s[2] = box.x

	states.append(box_s)
	return states


def putbox(container, box, container_path, box_locations, id, a):  # box_id


	states = create_states(box)
	#print(states)
	with open(container_path, 'rb') as f:
		container_array = pickle.load(f)
	cols = container_array.shape[2]
	rows = container_array.shape[1]
	z = container_array.shape[0]

	#boxi = box.shape[2]  # 120
	#boxj = box.shape[1]
	#boxk = box.shape[0]

	i = 0
	j = 0
	k = 0
	location = {"x_start": 0,
				"x_end": 0,
				"y_start": 0,
				"y_end": 0,
				"z_start": 0,
				"z_end": 0,
				"id": 0 }

			#print(container)

	while i < cols:
		j = 0
		while j < rows:
			while k < z:
					#print("belso while" + str(i) + str(j) + str(k))
					#input("jajjajj")
				if container_array[i][j][k] == 0:
					for s in states:
						if i + round(s[2]/10) <= cols and j + round(s[1]/10) <= rows and k + round(s[0]/10) <= z:  # ilyen kell majd minden forgatáshoz és ami alatta van
								# itt romlik el
								#print("eleje" + str(i) + str(j) + str(k))


							if np.any(container_array[i:i + round(s[2]/10), [range(j, j + round(s[1]/10))], k:k + round(s[0]/10)]) == False:
									#print("itt isvvvvvvvvvvvvvvvvv")
									# itt vegul beadja a kettest oda is, ahova nem fer be
									#print(container[i:i + s[2], [range(j, j + s[1])], k:k + s[0]])
									#print("vege" + str(i) + str(j) + str(k))
								container_array[i:i + round(s[2]/10), [range(j, j + round(s[1]/10))], k:k + round(s[0]/10)] = 2
									#print(container)
									#input()
								#a = {"a":1, 'b':2}
								location['x_start'] = i
								location['x_end'] = i + round(s[2]/109)
								location['y_start'] = j
								location['y_end'] = j + round(s[1]/10)
								location['z_start'] = k
								location['z_end'] = k + round(s[0]/10)
								location['id'] = id
								box_locations.append(location)
								pickle.dump(container_array, open(container_path, "wb"))
								a = True
								return True
				k += 1
				#print("vege" + str(i) + str(j) + str(k))
			#input()
			j += 1
			k = 0
				#print("ittaj")
		i += 1
		k = 0
	#a = {"a":11111, 'b':2}
	return False
	#return a