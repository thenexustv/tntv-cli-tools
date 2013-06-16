
# To use this script, please install PyPi
# (like the rubygem package manager)
# and then install 'mutagen'
#
# skip the next three lines if you already have PyPi
# curl -O http://python-distribute.org/distribute_setup.py
# sudo python distribute_setup.py
# sudo easy_install pip
# sudo pip install mutagen


# related links:
# http://id3.org/id3v2.3.0
# http://mutagen.readthedocs.org/en/latest/api/id3.html
# https://code.google.com/p/mutagen/


# read the code below with a few comments

# mutagen can read and set MP3 tags;
# this demo is only for reading
from mutagen.mp3 import MP3

# set any MP3 file from The Nexus here
audio = MP3("ns20.mp3")

# this will just show all the data we can access
print audio.pprint()

# this is where we'll do real things
print "-- -- --"

print "title: ", audio["TIT2"] # title
print "album: ", audio["TALB"] # album
print "composor: ", audio["TCOM"] # composer
print "genre: ", audio["TCON"] # genre/category
print "year: ", audio["TDRC"] # year
print "track artist: ", audio["TPE1"] # track artists
print "album artist: ", audio["TPE2"] # album artist
print "track number: ", audio["TRCK"] # track number


# find the image tag
image = audio["APIC:"].data
# save it to a file (hopefully it's a PNG?)
f = open('image.png', 'w');
f.write( image );

print "-- finished --"