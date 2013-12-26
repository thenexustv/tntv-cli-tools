tntv-tools
==========

This is a terminal package for helping the producers of The Nexus be productive.

This package contains python tools for
* adding metadata to episode files
* uploading episode files to S3

To utilize this package, please follow the steps in ./setup.sh.

Tools
=====

All functionality is wrapped in the executable ```tntv``` python file.

The two primary commands are ```tntv meta``` and ```tntv upload```.

How To
======

```./setup``` should install required python libraries


Meta
----

```python tntv meta filename "Episode title"```
The arguments required are a file and a title, but there are optional arguments as well

* ```--members "member1" "member2" "..."``` - this will add additional names into the predefined configuration
* ```--show 'short name'``` - this will override autodection of which show this file belongs to
* ```--number n``` - this will override autodection of which number episode this file is
* ```--meta-config``` - this will allow the user to specify a different config-meta.yaml file

**Example**: ```python tntv meta ../raw/atn81/cleaned/atn110.mp3 "Micro Bleutoot Box" --members "Ian Buck"```

This would output an MP3 with "Ryan Rampersad, Matthew Petschl and Ian Buck" as the Track Artists, 110 as track number, title as "At The Nexus #110: Micro Bleutoot Box".

```tntv meta``` will fail on some conditions:
* no configuration file is available
* no album art folder is available
* the specified album art file is not available
* there is an error in writing the ID3 tags to the MP3 file

Upload
------

```python tntv upload filename```
There argument required is only a file. There are currently no options.

**Example**: ```python upload.py ../atn110/cleaned/atn110.mp3```

In addition, ```tntv upload``` can take multiple file arguments. Each file in this argument list will be uploaded in that order.

**Example**: ```python upload.py ../atn110/cleaned/atn110.mp3 ../atn110/tf191.mp3```

In this case ```atn110``` and ```tf191``` will be uploaded to their respective directories.

```tntv upload``` will fail on some conditions:
* unable to establish an S3 connection
* local file is not marked as an MP3
* local file has no file size
* the remote file already exists
