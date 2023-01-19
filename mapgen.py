LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
dirs = [LEFT,RIGHT,UP,DOWN]
import random
def mgnh_corridor(sx,sy,tdir,len):
	res=[]
	if tdir == LEFT:
		for i in range(0,len):
			res.append((sx-i,sy))
	elif tdir == RIGHT:
		for i in range(0,len):
			res.append((sx+i,sy))
	elif tdir == UP:
		for i in range(0,len):
			res.append((sx,sy-i))
	elif tdir == DOWN:
		for i in range(0,len):
			res.append((sx,sy+i))
	return res
		
def mapgen(preseed="",map_iter=0,mapsize=[5,10]):
	random.seed(str(preseed)+str(map_iter))
	mx = (random.randint(mapsize[0],mapsize[1])//2) * 2
	my = mx
	res = [["." for i in range(mx)] for j in range(my)]
	sx,sy = random.randint(1,mx-2),random.randint(1,my-2)
	rsx,rsy=sx,sy
	roads=[]
	stype = random.randint(0,10)
	tdir = random.choice(dirs)
	if stype > 700:
		roads+=[
		(sx+1,sy),
		(sx-1,sy),
		(sx,sy-1),
		(sx,sy+1),
		(sx+1,sy-1),
		(sx+1,sy+1),
		(sx-1,sy-1),
		(sx-1,sy+1)
		]
	elif stype < 10:
		pass
	else:
		roads+=[
		(sx+1,sy),
		(sx-1,sy),
		(sx,sy-1),
		(sx,sy+1),
		]
	corlen=1
	if tdir == RIGHT:
		sx+=1
	if tdir == LEFT:
		sx-=1
	if tdir == DOWN:
		sy+=1
	if tdir == UP:
		sy-=1
	rrsx,rrsy=sx,sy
	cou=0
	while corlen:
		cou+=1
		if tdir == LEFT:
			corlen = min(sx - 1,random.randint(0,sx))
		if tdir == RIGHT:
			corlen = min(mx - sx - 1,random.randint(0,mx - sx))
		if tdir == UP:
			corlen = min(sy - 1, random.randint(0,sy))
		if tdir == DOWN:
			corlen = min(my - sy - 1,random.randint(0,my - sy))
		roads += mgnh_corridor(sx,sy,tdir,corlen)
		if tdir == LEFT:
			sx-=corlen
		if tdir == RIGHT:
			sx+=corlen
		if tdir == UP:
			sy-=corlen
		if tdir == DOWN:
			sy+=corlen
		ndirs = dirs.copy()
		ndirs.remove(tdir)
		tdir = random.choice(ndirs)
	if(len(roads)<10):
		for i in range(-3,3):
			for j in range(-3,3):
				nx=rsx
				ny=rsy
				nx+=i
				ny+=i
				nx = max(0,nx)
				ny = max(0,ny)
				nx = min(nx,mx-1)
				ny = min(ny,my-1)
				roads.append((nx,ny))
	for i in range(0,my):
		if random.randint(0,100) < random.randint(0,30):
			for j in range(0,mx):
				res[i][j] = "0"
		for j in range(0,mx):
			if random.randint(0,100) < random.randint(0,30):
				res[i][j] = "0"
	for j in range(0,mx):
		if random.randint(0,100) < random.randint(0,30):
			for i in range(0,mx):
				res[i][j] = "0"
	for i in roads:
		res[i[1]][i[0]] = "0"
	res[rsy][rsx] = "&"
	res[rrsy][rrsx] = "*"
	rrrsx=rrsx
	rrrsy=rrsy
	treasure = 1
	while(1):
		a = random.choice(roads)
		i,j=a[1],a[0]
		d = res[i][j]
		if d == "0":
			res[i][j] = "?"
			break
	for i in range(my):
		for j in range(mx):
			d = res[i][j]
			if d == "0" and random.randint(0, 100) < 50:
				d = random.choice("1111122244556677788")
			if random.randint(0,100) < 2 and treasure:
				d = "9"
				treasure = 0
			res[i][j] = d
	return res
"""
def mapgen_test():
	preseed = "aaa"
	levels = 2
	mrt = [5,10]
	map=[]
	print("press enter to get a random map with a seed attached to it. Press A + enter to enter a specific seed")
	print()
	print("two example maps N/s:")
	for i in range(0,levels):
		map.append(mapgen(preseed,i,mrt))
	for i in map:
		for j in i:
			print("".join(j))
		print()
	while(1):
		random.seed()
		nato = ["alpha","bravo","charlie","delta"]
		seed = random.choice(nato) + "-" + str(random.randint(1000,9999))
		print("seed: %s" % seed)
		res = mapgen(seed,0,mrt)
		for j in res:
			print("".join(j))
		print()
		if input().lower()=="a":
			print("Enter manual seed: ")
			seed = input()
			res = mapgen(seed,0,mrt)
			for j in res:
				print("".join(j))
			print()
			print("press enter to continue")
			input()
if __name__ == "__main__":
	mapgen_test()
"""
