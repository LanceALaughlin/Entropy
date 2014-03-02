import sys
import os
import getopt
from PIL import Image, ImageStat
import urllib
import cStringIO
import gtk, pygtk

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

	#Use GTK to get the screen resolution
	window = gtk.Window()
	global screen
	screen = window.get_screen()

	#Parse the arguments, then create a new image processor object with the value of the -i or --image argument as the image file to open
	p = ProcessImage(source)
	p.output()

#Class to handle image processing
#It inherits from the generic Python object
class ProcessImage(object):
	def __init__(self, source): #Pass in the argument image location
		#get the location of the image
		self.source = source

		#determine if the image is local or hosted, then open it
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

		self.imageWidth, self.imageHeight = self.image.size #Set width and height, which correspond to tuple values from self.image.size
		self.screenWidth, self.screenHeight = screen.get_width(), screen.get_height()

	def calcImageScore(self):
		return round(self.calcImageTemp()/40938*10,1)

	def calcImageTemp(self):
		totalTemp = 0
		for row in range(self.imageWidth):
			for col in range(self.imageHeight):
				totalTemp+=self.calcPixelTemp(self.image.getpixel((row,col)))

		return totalTemp/(self.imageWidth*self.imageHeight)

	def calcPixelTemp(self,RGB):
		R,G,B=RGB

		#http://dsp.stackexchange.com/questions/8949/how-do-i-calculate-the-color-temperature-of-the-light-source-illuminating-an-ima
		#Convert the RGB values to CIE tristimulus 3D color space coordinates
		X = ((-0.14282) * B) + ((1.54924) * G) + ((-0.95641) * B)
		Y = ((-0.32466) * R) + ((1.57837) * G) + ((-0.73191) * B) #illuminance
		Z = ((-0.68202) * R) + ((0.77073) * G) + (( 0.56332) * B)

		#Compute the Combined Color Temperature
		numerator =   ((0.23881) * R + ( 0.25499) * G + (-0.58291) * B)
		denominator = ((0.11109) * R + (-0.85406) * G + ( 0.52289) * B)

		if denominator == 0:
			CCT=0
		else:
			n=numerator/denominator
			CCT = (449 * (n**3)) + (3525 * (n**2) + (6823.3 * n) + 5520.33)

		return CCT

	def compareScreenSize(self):
		if(self.imageWidth < self.screenWidth or self.imageHeight < self.screenHeight):
			return "The image is smaller than the the screen resolution."
		else:
			return "The image is at least as big as the screen resolution! :)"

	def output(self): #Probably only print this in verbose mode in the future
		print '\033[0m' + "We're processing the image:" + self.source
		print '\033[0m' + "This", self.image.mode, "image is in the", self.image.format, "format"
		print '\033[0m' + "Image Size:", self.imageWidth, ",", self.imageHeight

		print '\033[95m' + "White: \tPixel (0,0) color temp:", self.calcPixelTemp(self.image.getpixel((0,0)))
		print '\033[94m' + "Blue: \tPixel (0,1) color temp:", self.calcPixelTemp(self.image.getpixel((0,1)))
		print '\033[91m' + "Red:\tPixel (1,0) color temp:", self.calcPixelTemp(self.image.getpixel((1,0)))
		print '\033[93m' + "Black: \tPixel (1,1) color temp:", self.calcPixelTemp(self.image.getpixel((1,1)))
		print "Average Image Temperature:", self.calcImageTemp()
		print "Screen Resolution: width = " + str(self.screenWidth) + ", height = " + str(self.screenHeight)
		print "Screen Size vs. Image Size: " + self.compareScreenSize()
		print "Image Score:", self.calcImageScore(),"/ 10"
	

#Python needs this to instantiate the program properly when it's executed from the command line
if __name__ == '__main__':
    main(sys.argv[1:])