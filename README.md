haello-rest-service
===================

An implementation of RESTful web service, used by the Android application [**haello**](https://github.com/2lastview/haello-Android-Application).
The HTTP server is implemented using [web.py](http://webpy.org/). A [Docker Container](https://registry.hub.docker.com/u/2lastview/haello-rest-service/)
has been created, so yo can run the service effortlessly.

####Installation

To run the service python 2.7 or higher is required. The other required packages can be found in the [requirements.txt](https://github.com/2lastview/haello-Rest-Service/blob/master/requirements.txt)
file. If virtualenv is used these requirements can be installed by running the following command:

    pip install requirements.txt

Googles Tesseract-OCR engine has been installed and you must be able to invoke the tesseract command "tesseract".
This can be accomplished by following this [guide](https://code.google.com/p/tesseract-ocr/wiki/ReadMe). Different
language packs must also be installed. This step is mentioned further down. In order for python to be able to
access this command the python wrapper pytesseract has to be installed. This requirement is listed in
[requirements.txt](https://github.com/2lastview/haello-Rest-Service/blob/master/requirements.txt).

####Installation with Docker

The simplest way for running the service is by running it inside a docker container. First you need to install docker
by following the official [installation guide](https://docs.docker.com/installation/#installation). Then you can pull
the image, which is packaged in Ubuntu 14.04, by running the following command:

    docker pull 2lastview/haello-rest-service

To run the service simply execute:

    docker run -d -p 8080:8080 2lastview/haello-rest-service

The -d flag means that it will run in daemon mode.

####Starting the service

To start the service simply navigate to the src folder and execute the following command:

    python rest.py

Host and port can be specified by simply adding them to the command:

    python rest.py 127.0.0.1:8000

By default host and port are defined as 0.0.0.0:8080. When running the service the application will try to create a
folder called uploads, where the uploaded images will be stored.

####Send requests to the service

The RESTful web service provides a HTTP GET page for testing the API (the image is sent as part of the multipart/form-data):

    upload image: http://localhost:8080/enrich

There are a few different parameters which can be specified as part of the url or the text body. These arguments
are the folowing:

**source=**
This is the source language of the text in the image. The code supports English (en), German (de) and Italian (it).
If this argument is not specified the application will extract the text from the image with tesseract, try to detect
the used language with goslate and then extract the text again. Supported languages for this case are English,
German, Italian, French, Spanish and Swedish. This list can be extended by adding [tesseract language packs and](https://code.google.com/p/tesseract-ocr/downloads/list)
extending the supported languages lists in [rest.py](https://github.com/2lastview/haello-Rest-Service/blob/master/src/rest.py).

**target=**
This is the target language. Supported languages are English (en), German (de) and Italian (it). This list can also be modified
by changing supported languages in [rest.py](https://github.com/2lastview/haello-Rest-Service/blob/master/src/rest.py).

**filetype=jpg**

**text=**
There is also the possibility of just sending text to the service. In this case it is still possible to send an image,
but not necessary.

If all these arguments are provided correctly, the service will translate the text using goslate, detect the used language
and then return a json similar to the following:

    {
        'detected': en,
        'text': the fox is lazy,
        'translation': der fuchs ist faul
    }

####Copyright and License

Author: Moritz Tomasi (moritz.tomasi at gmail dot com)
License: [Apache 2.0 License](https://github.com/2lastview/haello-Rest-Service/blob/master/LICENSE)
