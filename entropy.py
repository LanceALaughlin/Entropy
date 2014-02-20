import sys
import os
import getopt
from PIL import Image

#Class to handle image processing
#It inherits from the generic Python object
class ProcessImage(object):

	def __init__(self, source): #Pass in the argument image location
		self.source = source
		self.image = Image.open(self.source)

	def output(self): #Probably only print this in verbose mode in the future
		print "We're processing the image: " + self.source
		print "This " + self.image.mode + " image is in the " + self.image.format + " format"
		print self.image.size

def main(argv):
	image = None
	try:
		opts, args = getopt.getopt(argv, "hiv:d", ["help", "image=", "verbose"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-v","--verbose"):
			global _verbose
			_verbose = 1
		elif opt == '-d':
			global _debug
			_debug = 1
		elif opt in ("-i", "--image"):
			image = arg           

	source = "".join(args)
	#Parse the arguments, then create a new image processor object with the value of the -i or --image argument as the image file to open
	p = ProcessImage(source)
	p.output()

#Python needs this to instantiate the program properly when it's executed from the command line
if __name__ == '__main__':
    main(sys.argv[1:])