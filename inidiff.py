#!/usr/bin/env python

from argparse import ArgumentParser
from os.path  import isfile
from sys      import exit

# ------------------------------------------------------------------------------

parser = ArgumentParser(description='INI file diff utility.')
parser.add_argument('file1')
parser.add_argument('file2')
options = parser.parse_args()

if not isfile(options.file1):
	print "Cannot read file %s" % options.file1
	exit(1)
#endif

if not isfile(options.file2):
	print "Cannot read file %s" % options.file2
	exit(1)
#endif

# ------------------------------------------------------------------------------

data1 = {}

with open(options.file1, 'r') as f:
	section = None
	
	for line in f:
		line = line.strip()

		""" Empty line """
		if not line:
			continue
		#endif

		""" Comment, skip it """
		if line[0] in [';', '#']:
			continue
		#endif

		""" Section """
		if line[0] == '[':
			section = line[1:-1]
			data1[section] = {}
			continue
		#endif

		""" Item """
		line = line.split('=')
		data1[section][line[0].strip()] = ''.join(line[1:]).strip()
	#endfor
#endwith

# ------------------------------------------------------------------------------

data2 = {}

with open(options.file2, 'r') as f:
	section = None

	for line in f:
		line = line.strip()

		""" Empty line """
		if not line:
			continue
		#endif

		""" Comment, skip it """
		if line[0] in [';', '#']:
			continue
		#endif

		""" Section """
		if line[0] == '[':
			section = line[1:-1]
			data2[section] = {}
			continue
		#endif

		""" Item """
		line = line.split('=')
		key = line[0].strip()
		val = ''.join(line[1:]).strip()

		if section not in data1:
			""" Missing section """
			data2[section][key] = val
		elif key not in data1[section]:
			""" Added item """
			data2[section][key] = val
		elif data1[section][key] != val:
			""" Different values """
			data2[section][key] = val
		else:
			""" Same values """
			del data1[section][key]
		#endif
	#endfor
#endwith

# ------------------------------------------------------------------------------

for section in data1:
	""" Whole section is missing """
	if section not in data2:
		print "- [%s]" % section
		for item in  data1[section]:
			print "- %s = %s" % (item, data1[section][item])
		#endfor
		print ""
		continue
	#endif

	""" Both sections are same """
	if not data1[section] and not data2[section]:
		continue
	#endif

	print "[%s]" % section
	
	for item in data1[section]:
		if item not in data2[section]:
			""" Item is missing """
			print "- %s = %s" % (item, data1[section][item])
		else:
			""" Item is not equal """
			print "< %s = %s" % (item, data1[section][item])
			print "> %s = %s" % (item, data2[section][item])
		#endif
	#endfor

	for item in data2[section]:
		if item not in data1[section]:
			""" Item is added """
			print "+ %s = %s" % (item, data2[section][item])
		#endif
	#endfor

	print ""
#endfor

# ------------------------------------------------------------------------------

for section in data2:
	""" Whole section is added """
	if section not in data1:
		print "+ [%s]" % section
		for item in  data2[section]:
			print "+ %s = %s" % (item, data2[section][item])
		#endfor
		print ""
	#endif
#endfor
