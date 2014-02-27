import sys
import os
import getopt
from PIL import Image, ImageStat
import urllib
import cStringIO

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

#Class to handle image processing
#It inherits from the generic Python object
class ProcessImage(object):

	def __init__(self, source): #Pass in the argument image location
		self.source = source
		if 'http' in self.source:
			print 'reading from url'
			file = cStringIO.StringIO(urllib.urlopen(self.source).read())
			self.image = Image.open(file)
		else:
			try:
				self.image = Image.open(self.source)
			except IOError:
				print "Cannot load image. Be sure to include 'http://'' if loading from a website"
				sys.exit()

		r,g,b = self.image.getpixel((1, 1))
		self.results = RGBtoK(r,g,b)

	def output(self): #Probably only print this in verbose mode in the future
		print "We're processing the image: " + self.source
		print "This " + self.image.mode + " image is in the " + self.image.format + " format"
		print "Image Size: "
		print self.image.size
		print "Color Temp of First Pixel: "
		print self.results.calcTemp()



#http://dsp.stackexchange.com/questions/8949/how-do-i-calculate-the-color-temperature-of-the-light-source-illuminating-an-ima
class RGBtoK(object):
	def __init__(self,r,g,b):
		self.R=r
		self.B=b
		self.G=g

	def calcTemp(self):
		#Convert the RGB values to CIE tristimulus 3D color space codinates
		X = ((-0.14282) * self.B) + ((1.54924) * self.G) + ((-0.95641) * self.B)
		Y = ((-0.32466) * self.R) + ((1.57837) * self.G) + ((-0.73191) * self.B) #illuminance
		Z = ((-0.68202) * self.R) + ((0.77073) * self.G) + ((0.56332) * self.B)

		#Compute the Combined Color Temperature
		n=((0.23881) * self.R+(0.25499) * self.G+(-0.58291) * self.B) / ((0.11109) * self.R+(-0.85406) * self.G+(0.52289) * self.B)
		CCT = (449 * (n**3)) + (3525 * (n**2) + (6823.3 * n) + 5520.33)
		return CCT

#Python needs this to instantiate the program properly when it's executed from the command line
if __name__ == '__main__':
    main(sys.argv[1:])