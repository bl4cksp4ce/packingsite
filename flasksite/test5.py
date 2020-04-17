import numpy as np

#def order_boxes(boxes):
#	sorted(boxes, key = lambda box:box.volume)
#
#	for box in boxes:
#		if box.up == 1:
#			boxup.append(box)
#		elif box.down == 1 :
#			boxdown.append(box)
#		else:
#			boxgeneral.append(box)
#	boxes = boxdown + boxgeneral + boxup



def create_states(box):
	states = []

	#box.states[s][name] = "yzx"
	box_s = [0, 0, 0]
	#box.shape[2]#120
	#boxj = box.shape[1]
	#boxk = box.shape[0]
	box_s[0] = box.shape[0]
	box_s[1] = box.shape[1]
	box_s[2] = box.shape[2]

	states.append(box_s)
	box_s[0] = box.shape[0]
	box_s[1] = box.shape[2]
	box_s[2] = box.shape[1]

	states.append(box_s)
	box_s[0] = box.shape[1]
	box_s[1] = box.shape[0]
	box_s[2] = box.shape[2]

	states.append(box_s)
	box_s[0] = box.shape[1]
	box_s[1] = box.shape[2]
	box_s[2] = box.shape[0]

	states.append(box_s)
	box_s[0] = box.shape[2]
	box_s[1] = box.shape[0]
	box_s[2] = box.shape[1]

	states.append(box_s)
	box_s[0] = box.shape[2]
	box_s[1] = box.shape[1]
	box_s[2] = box.shape[0]

	states.append(box_s)
	return states


def putbox(container, box, box_locations, id):  # box_id


	states = create_states(box)
	#print(states)
	cols = container.shape[2]
	rows = container.shape[1]
	z = container.shape[0]

	y = 2
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
				"id": 0}

			#print(container)

	while i < cols:
		j = 0
		while j < rows:
			while k < z:
					#print("belso while" + str(i) + str(j) + str(k))
					#input("jajjajj")
				if container[i][j][k] == 0:
					for s in states:
						if i + s[2] <= cols and j + s[1] <= rows and k + s[0] <= z:  # ilyen kell majd minden forgatáshoz és ami alatta van
								# itt romlik el
								#print("eleje" + str(i) + str(j) + str(k))


							if np.any(container[i:i + s[2], [range(j, j + s[1])], k:k + s[0]]) == False:
									#print("itt isvvvvvvvvvvvvvvvvv")
									# itt vegul beadja a kettest oda is, ahova nem fer be
									#print(container[i:i + s[2], [range(j, j + s[1])], k:k + s[0]])
									#print("vege" + str(i) + str(j) + str(k))
								container[i:i + s[2], [range(j, j + s[1])], k:k + s[0]] = 2
									#print(container)
									#input()
								location['x_start'] = i
								location['x_end'] = i + s[2]
								location['y_start'] = j
								location['y_end'] = j + s[1]
								location['z_start'] = k
								location['z_end'] = k + s[0]
								box_locations.append(location)
								return
				k += 1
				#print("vege" + str(i) + str(j) + str(k))
			input()
			j += 1
			k = 0
				#print("ittaj")
		i += 1
		k = 0
		#print("legvege" + str(i) + str(j) + str(k))
#putbox(arr3d)
