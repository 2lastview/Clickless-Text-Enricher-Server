import web
import uuid
import logging
from PIL import Image
import pytesseract

LOGGER = logging.getLogger('rest')

urls = ('/enrich', 'Enrich')

supported_filetypes = ['jpg', 'tiff', 'png']
supported_languages = ['eng', 'deu', 'ita']

class Enrich:

    def GET(self):
        LOGGER.info('GET in Enrich called.')

        return """<html><head></head><body>
            <form method="POST" enctype="multipart/form-data" action="">
            <input type="file" name="image" /><input type="submit" />
            </form></body></html>"""


    def POST(self):
        LOGGER.info('POST in Enrich called.')

        lang_from = None
        lang_to = None
        enrich = True

        data = web.input(image={})

        if 'image' in data:
            image = data.image

            if len(image.value) == 0:
                LOGGER.debug('No image to process.')
                raise web.badrequest(message='400 Bad Request: No image to process. No value.')

            if len(image.filename) == 0:
                LOGGER.debug('No image to process.')
                raise web.badrequest(message='400 Bad Request: No image to process. No filename.')

            if 'filetype' in data:
                filetype = str(data.filetype).lower()

                if filetype not in supported_filetypes:
                    LOGGER.debug('No support for this filetype.')
                    raise web.badrequest(message='400 Bad Request: No support for this filetype.')
            else:
                LOGGER.debug('No filetype specified.')
                raise web.badrequest(message='400 Bad Request: No filetype specified.')

            image_dir = 'uploads'
            image_id = str(uuid.uuid4())
            image_name = image_id + '.' + filetype

            try:
                out = open(image_dir + '/' + image_name, 'w')
                out.write(image.file.read())
                out.close()
            except:
                LOGGER.warning('Could not store image.')
                raise web.internalerror(message='500 Internal Server: Could not store image.')
            finally:
                final_image_path = image_dir + '/' + image_name

            LOGGER.debug('Image saved in ' + image_dir + '/' + image_name)
        else:
            LOGGER.debug('No image object created.')
            raise web.badrequest(message='400 Bad Request: No image object created.')

        if 'langfrom' in data:
            lang_from = str(data.langfrom).lower()

            if lang_from not in supported_languages:
                lang_from = None

        if 'langto' in data:
            lang_to = str(data.langto)
        else:
            LOGGER.debug('No language to translate to specified.')
            raise web.badrequest(message='400 Bad Request: No language to translate into specified.')

        if 'enrich' in data:
            if str(data.enrich).lower() == 'false':
                enrich = False
            elif str(data.enrich).lower() == 'true':
                enrich = True
            else:
                LOGGER.debug('Enrich is not True or False.')
                raise web.badrequest(message='400 Bad Request: Enrich is not True or False.')

        return self.textFromImage(final_image_path, lang_from)

    def textFromImage(self, image_path, lang_from=None):
        LOGGER.info('getTextFromImage in Enrich called with parameters: image_path=' + image_path + ' and lang_from=' + str(lang_from))

        if image_path == None or len(image_path) == 0:
            LOGGER.warning('500 Internal Server: Path to image is not valid.')
            raise web.internalerror(message='500 Internal Server: Path to image is not valid.')

        try:
            image = Image.open(image_path)
        except:
            LOGGER.warning('Could not open image.')
            raise web.internalerror(message='500 Internal Server: Could not open image.')

        return pytesseract.image_to_string(image, lang_from)


def main():
    logging.basicConfig(format='%(levelname)s - %(module)s - [%(asctime)s] "%(message)s"', datefmt='%d/%h/%Y %H:%M:%S', level=logging.DEBUG)
    LOGGER.info('Main called for CTE REST Server.')

    app = web.application(urls, globals())
    app.run()

    LOGGER.info('REST Server for CTE shutdown.')


if __name__ == '__main__':
    main()