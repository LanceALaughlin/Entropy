#!/usr/bin/env python
import sys
import os
import getopt
from PIL import Image, ImageStat, ImageCms
import urllib
import cStringIO

def main(argv):
	image = None
	
	try:
		opts, args = getopt.getopt(argv, "hi:v", ["help", "image=", "verbose"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	global _verbose
	global _image
	_verbose = False
	_image = None

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-v","--verbose"):
			_verbose = True
		elif opt in ("-i", "--image"):
			_image = arg

	#Pull screen data from xrandr
	global screen
	screen = os.popen("xrandr -q -d :0").readlines()[0]
	p = ProcessImage(_image)
	p.output()

def aspectRatio(width, height):
	return round(float(width) / float(height), 2)

def numPixels(width, height):
	return width * height

#Return number mapped to range 0 to 10
def normalizeNumber(x, xmin, xmax):
	return (float((x - xmin)) / float((xmax - xmin))) * 10

#Return number clamped to allowed min/max values
def clampNumber(num, minimum, maximum):
	 return min(max(minimum, num), maximum)

#Print this help when run with the -h flag or when the user entered bad flags
def usage():
	print "\nEntropy is a tool to rate wallpapers based on image attributes.\n\n" + \
	"Usage:\n" + \
	"=========================================\n" + \
	"python entropy.py -i \"filename\"\n" + \
	"Process the image (local or URL) and print a rating.\n" + \
	"-----------------\n" + \
	"python entropy.py -i \"filename\" -v\n" + \
	"Process the image and print verbose technical output.\n"
	
#Class to handle image processing
#It inherits from the generic Python object
class ProcessImage(object):
	def __init__(self, source): #Pass in the argument image location
		#get the location of the image
		self.source = source

		#determine if the image is local or hosted, then open it
		if 'http' in self.source:
			if(_verbose):
				print 'Reading from URL'
			file = cStringIO.StringIO(urllib.urlopen(self.source).read())
			self.image = Image.open(file)
		else:
			try:
				self.image = Image.open(self.source)
			except IOError:
				print self.source
				print "Cannot load image. Be sure to include 'http://'' if loading from a website!"
				sys.exit()

		sRGB = ImageCms.createProfile("sRGB")
		pLab = ImageCms.createProfile("LAB")
		t = ImageCms.buildTransform(sRGB, pLab, "RGB", "LAB")
		self.labImage = ImageCms.applyTransform(self.image, t)
		self.imageWidth, self.imageHeight = self.image.size #Set width and height, which correspond to tuple values from self.image.size
		self.screenWidth, self.screenHeight = int(screen.split()[7]), int(screen.split()[9][:-1])
		self.lost_res = 0.0
		self.lost_aspect = 0.0
		self.temp_rating = self.calcAvgImageTemp()
		self.final_rating = self.calcImageScore()

	#Generate a score for the image
	def calcImageScore(self):
		score = 0.0
		score += self.temp_rating #Initially base score on average image temp
		#Factor in size differences
		pixelDiff = self.calcPixelDiff()
		aspectDiff = self.calcAspectDiff()
		if(pixelDiff > 0): #Only take away points if the screen is a higher res than the image
			i = pixelDiff
			while(i > 0):
				score -= 0.0001 #For every pixel of difference there is between image and screen res, take away this many points
				self.lost_res += 0.0001
				i -= 1
		i = aspectDiff
		while(i > 0):
			score -= 1 #For how big the difference in aspect ratio is, take away this many points
			self.lost_aspect += 1
			i -= 1

		#Make sure we don't go below 0
		score = max(0.0, score)
		return round(score, 1) #Round to 1 decimal place

	#Determine a color temperature score based on the temperature
	#In Lab color, a higher L correlates to a brigher image
	#higher a and b values correlate to warmer colors
	def calcAvgImageTemp(self):
		totalTemp = 0.0
		#We rate each pixel, combine the rating, and average it over the image dimensions for a mean rating
		for row in range(self.imageWidth):
			for col in range(self.imageHeight):
				pixel = self.labImage.getpixel((row,col))
				#Certain colors when converted from RGB can go outside the L,a,b range, so we need to clamp them
				L,a,b = pixel
				L = normalizeNumber(clampNumber(L, 0, 100), 0, 100) / 3.333
				a = normalizeNumber(clampNumber(a, -128, 127), -128, 127) / 3.333
				b = normalizeNumber(clampNumber(b, -128, 127), -128, 127) / 3.333
				totalTemp += (L + a + b) #The individual ratings for L, a, and b comprise 33.3% of each per-pixel rating
				#Perhaps in the future, L could have a lower weight, since "brighter" doesn't always mean "warmer"
		return totalTemp/(self.imageWidth * self.imageHeight) #Average per-pixel rating for image

	def calcPixelDiff(self):
		return numPixels(self.screenWidth, self.screenHeight) - numPixels(self.imageWidth, self.imageHeight)

	def calcAspectDiff(self):
		return abs(aspectRatio(self.screenWidth, self.screenHeight) - aspectRatio(self.imageWidth, self.imageHeight))

	def compareScreenSize(self):
		if(self.imageWidth < self.screenWidth or self.imageHeight < self.screenHeight):
			return "The image is smaller than the the screen resolution."
		else:
			return "The image is at least as big as the screen resolution! :)"

	def output(self):

		if(self.final_rating < 4):
			color = '\033[91m'
		elif(self.final_rating < 7):
			color = '\033[93m'
		else:
			color = '\033[92m'

		if(_verbose):
			print '\033[0m' + "We're processing the image:" + self.source
			print '\033[0m' + "This", self.image.mode, "image is in the", self.image.format, "format"
			print '\033[0m' + "Image Size:", self.imageWidth, ",", self.imageHeight
			print "Screen Resolution: width = " + str(self.screenWidth) + ", height = " + str(self.screenHeight)
			print "Per-Pixel Average Image Temperature Rating:", self.temp_rating
			print "Aspect ratio Difference: " + str(self.calcAspectDiff())
			print "Screen Size vs. Image Size: " + self.compareScreenSize()
		
		print "Image Score:", color, self.final_rating, "/ 10"

		if(_verbose):
			print "This image lost " + str(self.lost_res) + " points due to the resolution difference"
			print "This image lost " + str(self.lost_aspect) + " points due to the aspect ratio difference"
	

#Python needs this to instantiate the program properly when it's executed from the command line
if __name__ == '__main__':
    main(sys.argv[1:])