tntv-tools
==========

This is a terminal package for helping the producers of The Nexus be productive.

This package contains python tools for
* adding metadata to episode files
* uploading episode files to S3

To utilize this package, please follow the steps in ./setup.sh.

Tools
=====

* meta.py - adds ID3 meta-data to MP3 files
* upload.py - uploads MP3 files intelligently to S3 server

How To
======

```./setup``` should install required python libraries


Meta
----

```python meta.py filename "Episode title"```
The arguments required are a file and a title, but there are optional arguments as well.
* ```--members "member1" "member2" "..."``` - this will add additional names into the predefined configuration
* ```--show 'short name'``` - this will override autodection of which show this file belongs to
* ```--number n``` - this will override autodection of which number episode this file is
* ```--meta-data``` - this will allow the user to specify a different config-meta.yaml file

**Example**: ```python meta.py ../raw/atn81/cleaned/atn81.mp3 "DnDn Protagonist" --members "Sam Ebertz" "Ben Bears"```

This would output an MP3 with "Ryan Rampersad, Matthew Petschl, Sam Ebertz and Ben Bears" as the Track Artists, as well as 81 as track number, title as "At The Nexus #81: DnDn Protagonist".

Upload
------

```python upload.py filename```
There argument required is only a file. There are currently no options.

**Example**: ```python upload.py ../atn81/cleaned/atn81.mp3```

This will upload the specified MP3 episode to the S3 in the proper location. If a file is already using **atn81.mp3** as its file name, this will alert the user and stop the upload.
