import sys

def waypoints_to_file(lat, lon, outfile=sys.stdout):
    print("QGC WPL 110", file=outfile)
    print("0\t1\t0\t16\t0\t0\t0\t0\t{}\t{}\t20\t1".format(lat[0],lon[0]), file=outfile)
    for i,lat_ in enumerate(lat):
        print("{}\t0\t3\t16\t0\t0\t0\t0\t{}\t{}\t1\t1".format(i+1, lat_, lon[i]), file=outfile)

if __name__ == '__main__':
	for filename in sys.argv[1:]:
		lat = []
		lon = []
		with open(filename) as file:
			for line in file:
				lat_, lon_ = line.split(',')
				lat.append(float(lat_))
				lon.append(float(lon_))
		with open(filename + '.waypoints', 'w') as outfile:
			waypoints_to_file(lat, lon, outfile)
