

from mutagen.mp3 import MP3
from mutagen.id3 import *

# set any MP3 file from The Nexus here
audio = ID3("ns20.mp3")

print audio.pprint()

print "adding data to the mp3 file ---"

title = TIT2(encoding=3, text="Nexus Special #55: Huge Week")

audio.add(title)

audio.save()

print "reading file now ---"

audio2 = MP3("ns20.mp3")
print audio2.pprint()