
from sys import stdout
import boto
import boto.s3
from boto.s3.key import Key
import yaml

def get_data(file):
	f = open(file)
	data = yaml.load(f)
	return data;

# Hey look, in line file upload progress!
def percent_cb(complete, total):
	stdout.write( "\r%d" % round( ( float(complete) / float(total) ) * 100 ) )
	stdout.flush()

def main():
	data = get_data('config.yaml')
	connection = boto.connect_s3(data["aws_key"], data["aws_secret"])
	bucket = connection.get_bucket("the-nexus-tv")

	key = "album-art-003.zip"
	k = Key(bucket)
	k.key = key

	# Do not ever let files get _overwritten_
	# This is a core principle; it will always be worth doing it by hand
	# If there is any suspicion that a file already exists.
	if k.exists():
		print "The file already exists: ", key
		return; 

	k.set_contents_from_filename("album-art.zip", cb = 
		percent_cb, num_cb = 100)
	k.make_public()

	stdout.write("\n")


# ---
main()