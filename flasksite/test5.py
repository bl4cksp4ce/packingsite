import numpy as np

def order_boxes(boxes):
	sorted(boxes, key = lambda box:box.volume)

	for box in boxes:
		if box.up == 1:
			boxup.append(box)
		elif box.down == 1 :
			boxdown.append(box)
		else:
			boxgeneral.append(box)
	boxes = boxdown + boxgeneral + boxup


def count_states(box):
	#box.state_mark: [0][1][1]
	box.states_n = 6
	box.states_n -= [2*n for n in state_mark]
	#box.states_n = 6-box.states_n
def generate_states(box):
	s = 0
	if rotate_x == 0:
		#yzx, zyx
		box.states[s][name] = "yzx"
		box.states[s][x] = box.y
		box.states[s][y] = box.z
		box.states[s][z] = box.x
		s += 1

		box.states[s][name] = "zyx"
		box.states[s][x] = box.y
		box.states[s][y] = box.z
		box.states[s][z] = box.x
		s += 1
		
	if rotate_y == 0:
		#xzy, zxy
		box.states[s][name] = "xzy"
		box.states[s][x] = box.x
		box.states[s][y] = box.z
		box.states[s][z] = box.y
		s += 1

		box.states[s][name] = "zxy"
		box.states[s][x] = box.z
		box.states[s][y] = box.x
		box.states[s][z] = box.y
		s += 1

	if rotate_z = 0:
		#xyz, yxz
		box.states[s][name] = "xyz"
		box.states[s][x] = box.x
		box.states[s][y] = box.y
		box.states[s][z] = box.z
		s += 1

		box.states[s][name] = "yxz"
		box.states[s][x] = box.y
		box.states[s][y] = box.x
		box.states[s][z] = box.z
		s += 1

def rotate(box):
	#legeneralja mind a 6 allapotot, ha valamelyik nem lehetseges, azt jeloli
	#box:ban[x, y, z] 
	#tárolhatja az állapot számát
	#ahány 0 van a ban-ben 2* annyi állapot
	#current state, number of states
	count_states(box)
	generate_states(box)
	box.current_state += 1
	#a legenerált állapotokból veszi az x y z koordinátákat, ha sikerült lerakni,
	# akkor továbblép a következő csomagra, ha nem, akkor forgat, tehát a state countert növeli
	#innen szedi a koordinátát
	#még ki kell találni, ha bele akarom rakni h legyen prioritás a forgatások között,
	#azt hogy érdemes megcsinálni


def putbox(container, box):



	cols = container.shape[1]
	rows = container.shape[2]
	z = container.shape[0]


	y = 2
	boxi = box.shape[1]
	boxj = box.shape[2]
	boxk = box.shape[0]

	i = 0
	j = 0
	k = 0
	print(container)

	while i < cols:
		j = 0
		while j < rows:
			while k < z:
			#print(arr[i][j])
				print("eleje" + str(i) + str(j) + str(k))
				input("jajjajj")	
				if container[i][j][k] == 0:
					if (i, j, k) == (0, 2, 2) :
							print(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk])
							#megtalálja ezt
							input("seggfasz")
							print(cols, i+boxi, rows, j+boxj, z, k+boxk)
					if i + boxi <= z and j + boxj <= rows and k + boxk <= cols: #kicsereltem colt zvel most jo
						print("segg")
						#itt romlik el
						print("eleje" + str(i) + str(j) + str(k))
						if (i, j, k) == (0, 2, 2) :
							print(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk])
							input("seggfasz2")

						if np.any(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk]) == False :
							print("itt isvvvvvvvvvvvvvvvvv")
							#itt vegul beadja a kettest oda is, ahova nem fer be
							print(container[i:i+boxi, [range(j, j+boxj)], k:k+boxk])
							print("vege" + str(i) + str(j) + str(k))
							container[i:i+boxi, [range(j, j+boxj)], k:k+boxk] = 2
							print(container)
							input()
							return
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
			print("vege" + str(i) + str(j) + str(k))
			input()
			j += 1
			k = 0
			print("ittaj")
		i += 1
		k = 0
		#j = 0
	#j = 0
	#print(container)
	print("legvege" + str(i) + str(j) + str(k))

arr3d = np.array([[[1, 1, 0, 1],[0, 1, 0, 1],[0, 0, 1, 0],[0, 0, 0, 0]],
				[[1, 1, 0, 1],[0, 1, 0, 1],[0, 0, 0, 0],[0, 0, 0, 0]],
				[[1, 1, 0, 1],[0, 1, 0, 1],[0, 0, 0, 0],[0, 0, 0, 0]]])
box3d = np.array([[[1,1],[1, 1]],
				[[1,1],[1, 1]]])

putbox(arr3d, box3d)
print(arr3d)
putbox(arr3d, box3d)
print(arr3d)
#putbox(arr3d)