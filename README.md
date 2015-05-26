haello-rest-service
===================

An implementation of a RESTful web service used by the Android application [**haello**](https://github.com/2lastview/haello-Android-Application)
in order to extract and translate text from images. The HTTP server is implemented using [web.py](http://webpy.org/). A [Docker Container](https://registry.hub.docker.com/u/2lastview/haello-rest-service/)
has been created so yo can run the service effortlessly.

####Installation

To run the service python 2.7 or higher is required. The other required packages can be found in the [requirements.txt](https://github.com/2lastview/haello-Rest-Service/blob/master/requirements.txt)
file. If virtualenv is used these requirements can be installed by running the following command:

    pip install requirements.txt

First install Googles Tesseract-OCR engine and make sure that the tesseract command "tesseract" can be invoked.
This can be accomplished by following this [guide](https://code.google.com/p/tesseract-ocr/wiki/ReadMe). Required language
packs must also be installed. This step is also mentioned further down. In order for python to be able to
access the tesseract command a python wrapper called pytesseract has to be installed. This requirement is listed in
[requirements.txt](https://github.com/2lastview/haello-Rest-Service/blob/master/requirements.txt).

####Installation with Docker

The simplest way of running the service is by running it inside a docker container. First you need to install docker
by following the official [installation guide](https://docs.docker.com/installation/#installation). Then you can pull
the image, which is packaged in Ubuntu 14.04, by running the following command:

    docker pull 2lastview/haello-rest-service-a

To run the service execute:

    docker run -d -p 8080:8080 2lastview/haello-rest-service-a

The -d flag means that it will run in daemon mode. In the [Dockerfile](https://github.com/2lastview/haello-Rest-Service/blob/master/Dockerfile)
six language packs are added. You can change this list as you wish, but if you do, you will also have to change the supported
languages lists in [rest.py](https://github.com/2lastview/haello-Rest-Service/blob/master/src/rest.py).

####Starting the service

To start the service navigate to the src folder and execute the following command:

    python rest.py

Host and port can be specified by adding them to the command:

    python rest.py 127.0.0.1:8000

By default host and port are defined as 0.0.0.0:8080. When running the service the application will try to create a
folder called uploads, where the uploaded images will be stored.

####Send requests to the service

The RESTful web service provides a HTTP GET page for testing the API (the image is sent as part of the multipart/form-data):

    upload image: http://localhost:8080/enrich

There are a few different parameters which can be specified as part of the url or the text body. These arguments
are the folowing:

**source=**
This argument represents the source language. The code currently supports English (en), German (de) and Italian (it).
If this argument is not specified the application will extract the text from the image with tesseract, try to detect
the used language with goslate and then extract the text again. Supported languages for this case are English,
German, Italian, French, Spanish and Swedish. This list can be extended by adding [tesseract language packs](https://code.google.com/p/tesseract-ocr/downloads/list),
and by extending the supported languages lists in [rest.py](https://github.com/2lastview/haello-Rest-Service/blob/master/src/rest.py).

**target=**
This is the target language. Supported languages are English (en), German (de) and Italian (it). This list can also be modified
by changing supported languages in [rest.py](https://github.com/2lastview/haello-Rest-Service/blob/master/src/rest.py).

**filetype=jpg**

**text=**
There is also the possibility of just sending text to the service.

If all these arguments are provided correctly, the service will translate the text using goslate, detect the source language
and return a json similar to the following:

    {
        'detected': en,
        'text': the fox is lazy,
        'translation': der fuchs ist faul
    }

####Copyright and License

Author: Moritz Tomasi (moritz.tomasi at gmail dot com)

License: [Apache 2.0 License](https://github.com/2lastview/haello-Rest-Service/blob/master/LICENSE)
