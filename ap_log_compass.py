import re
import numpy as np
import matplotlib.pyplot as plt

def read_ap_log(filename):
	data = {'FMT': {}}
	with open(filename) as f:
		for line in f:
			fields = re.split(', *', line);
			type = fields.pop(0);
			if type == "FMT":
				type = fields[2];
				fields = fields[4:];
				data['FMT'][type] = fields;
			elif type in data:
				data[type].append(fields)
			else:
				data[type] = [fields]
	for field in data:
		lengths = np.unique([len(x) for x in data[field]])
		if len(lengths) != 1:
			print("unable to rotate field", field)
			continue
		local_data = np.transpose(data[field])
		try:
			local_data = local_data.astype(float);
		except:
			pass
		data[field] = dict(zip(data['FMT'][field], local_data))
	return data

data = read_ap_log('/Users/ben/Downloads/2018-11-05 12-39-01.log');

plt.ion()

mag1 = data['MAG']
mag2 = data['MAG2']
mag3 = data['MAG3']
gps = data['GPS2']
att = data['ATT']
mag_decl = 13 ; # looked up with USGS for the test site

# check that GPS GCrs data matches the expected conventions
gpsangle = np.arctan2(np.diff(gps['Lat']),np.diff(gps['Lng']))*180/np.pi
gpsangle = np.mod(90-gpsangle, 360)
plt.plot(gps['TimeUS'][1:], gpsangle, gps['TimeUS'], gps['GCrs'])
# yeah, it's pretty good.  next...

plt.figure();
plt.plot(mag1['TimeUS'], mag1['MagX'], mag1['TimeUS'], mag1['MagY'], mag1['TimeUS'], mag1['MagZ'])

plt.figure();
plt.plot(mag2['TimeUS'], mag2['MagX'], mag2['TimeUS'], mag2['MagY'], mag2['TimeUS'], mag2['MagZ'])

plt.figure();
plt.plot(mag3['TimeUS'], mag3['MagX'], mag3['TimeUS'], mag3['MagY'], mag3['TimeUS'], mag3['MagZ'])

# look, circles:
plt.figure(); plt.plot(mag1['MagX'],mag1['MagZ'], mag2['MagX'],mag2['MagY'], mag3['MagX'], mag3['MagY'])

# let's try deciphering mag1, arbitrarily, not being fancy and elliptical:
mag1x = (mag1['MagX']+28.5)/(190+247) # graphically determined
mag1z = (mag1['MagZ']+273)/(-46+500) # graphically determined again
magangle = np.arctan2(mag1x, mag1z)*180/np.pi
# just for fun, mag2 and mag3 as well:
mag2x = (mag2['MagX']+101.5)/(127+330) # graphically determined
mag2y = (mag2['MagY']+175)/(-17+333) # graphically determined again
mag3x = (mag3['MagX']-10.5)/(185+164) # graphically determined
mag3y = (mag3['MagY']+427)/(-273+581) # graphically determined again
magangle2 = 90-np.arctan2(mag2y, mag2x)*180/np.pi - 90 + mag_decl
magangle3 = 90-np.arctan2(mag3y, mag3x)*180/np.pi - 90 + mag_decl
#plot it!
plt.figure();
plt.plot(mag3['TimeUS'], np.mod(magangle3, 360), label='Manual Magnetometer Heading (int3)');
plt.plot(mag2['TimeUS'], np.mod(magangle2, 360), label='Manual Magnetometer Heading (int2)');
plt.plot(mag1['TimeUS'], np.mod(magangle-75,360), label='Manual Magnetometer Heading (ext)')
plt.plot(gps['TimeUS'], gps['GCrs'], label='GPS Ground Course');
plt.plot(att['TimeUS'], att['Yaw'], label='ATT Yaw');
plt.plot(data['AHR2']['TimeUS'], data['AHR2']['Yaw'], label='AHRS Yaw');
plt.legend()
plt.ylabel('Heading (degrees cw from N)')
plt.xlabel('Time [μs]')
