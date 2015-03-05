import os
import web
import uuid
import logging
from PIL import Image
import pytesseract
import goslate
import json

LOGGER = logging.getLogger('rest')

urls = ('/enrich', 'Enrich')

supported_filetypes = ['jpg', 'tiff', 'png']
supported_languages = ['eng', 'deu', 'ita']
supported_languages_google_translate = {'eng':'en', 'deu':'de', 'ita':'it'}

gs = goslate.Goslate()

class Enrich:

    def GET(self):
        LOGGER.info('GET in Enrich called.')

        return """<html><head></head><body>
            <form method="POST" enctype="multipart/form-data" action="">
            <input type="file" name="image" /><input type="submit" />
            </form></body></html>"""

    def POST(self):
        LOGGER.info('POST in Enrich called.')

        source_lang = None
        target_lang = None
        enrich = True
        corrected_text = None
        corrected = False

        data = web.input(image={})

        if 'text' in data:
            corrected_text = data.text
            corrected = True

        if 'image' in data and not corrected:
            image = data.image

            if len(image.value) == 0:
                LOGGER.debug('400 Bad Request: No image to process. No value.')
                raise web.badrequest(message='No image to process. No value.')

            if len(image.filename) == 0:
                LOGGER.debug('400 Bad Request: No image to process. No filename.')
                raise web.badrequest(message='No image to process. No filename.')

            if 'filetype' in data:
                filetype = str(data.filetype).lower()

                if filetype not in supported_filetypes:
                    LOGGER.debug('400 Bad Request: No support for this filetype.')
                    raise web.badrequest(message='No support for this filetype.')
            else:
                LOGGER.debug('400 Bad Request: No file-type specified.')
                raise web.badrequest(message='No file-type specified.')

            image_dir = 'uploads'
            image_id = str(uuid.uuid4())
            image_name = image_id + '.' + filetype

            try:
                out = open(image_dir + '/' + image_name, 'w')
                out.write(image.file.read())
                out.close()
            except:
                LOGGER.warning('500 Internal Server: Could not store image.')
                raise web.internalerror(message='Server: Could not store image.')
            finally:
                final_image_path = image_dir + '/' + image_name
                text_from_image = self.getText(final_image_path, source_lang)

            LOGGER.debug('Image saved in ' + image_dir + '/' + image_name)

        if 'source' in data:
            source_lang = str(data.source).lower()

            if source_lang not in supported_languages:
                source_lang = None

        if 'target' in data:
            target_lang = str(data.target).lower()

            if target_lang not in supported_languages:
                LOGGER.debug('400 Bad Request: This target language is not supported.')
                raise web.badrequest(message='This target language is not supported.')

            if source_lang == None:
                if not corrected:
                    translation = self.getTranslation(text_from_image, supported_languages_google_translate[target_lang])
                else:
                    translation = self.getTranslation(corrected_text, supported_languages_google_translate[target_lang])
            else:
                if not corrected:
                    translation = self.getTranslation(text_from_image, supported_languages_google_translate[target_lang], supported_languages_google_translate[source_lang])
                else:
                    translation = self.getTranslation(corrected_text, supported_languages_google_translate[target_lang], supported_languages_google_translate[source_lang])

            if not corrected:
                detected_lang = self.getLanguage(text_from_image)
            else:
                detected_lang = self.getLanguage(corrected_text)
        else:
            LOGGER.debug('400 Bad Request: No language to translate into specified.')
            raise web.badrequest(message='No language to translate into specified.')

        if 'enrich' in data:
            if str(data.enrich).lower() == 'true':
                enrich = True
                enriched_text = self.enrich()

        if not corrected:
            return self.getJson(text_from_image, translation, detected_lang, target_lang, enrich, source_lang)
        else:
            return self.getJson(corrected_text, translation, detected_lang, target_lang, enrich, source_lang)

    def getText(self, image_path, source_lang=None):
        LOGGER.info('getText in Enrich called with parameters: image_path=' + image_path + ' and source_lang=' + str(source_lang))

        if image_path == None or len(image_path) == 0:
            LOGGER.warning('500 Internal Server: Path to image is not valid.')
            raise web.internalerror(message='Path to image is not valid.')

        try:
            image = Image.open(image_path)
        except:
            LOGGER.warning('500 Internal Server: Could not open image.')
            raise web.internalerror(message='Could not open image.')

        try:
            if source_lang == None:
                text = pytesseract.image_to_string(image)
            else:
                text = pytesseract.image_to_string(image, source_lang)
        except:
            LOGGER.warning('500 Internal Server: Could not extract text from image.')
            raise web.internalerror(message='Could not extract text from image.')

        if len(text) <= 0:
            LOGGER.debug('404 Bad Request: No text detected in image.')
            raise web.notfound(message='No text detected in image.')

        LOGGER.debug('\n---------- Text ----------\n' + text + '\n---------- /Text ----------')
        return text

    def getTranslation(self, text, target_lang, source_lang=None):
        LOGGER.info('getTranslation in Enrich called with text and parameters: target_lang=' + target_lang + ' and source_lang=' + str(source_lang))

        if target_lang == None or len(target_lang) == 0:
            LOGGER.warning('500 Internal Server: Target language is not valid.')
            raise web.internalerror(message='Target language is not valid.')

        try:
            if source_lang == None:
                translation = gs.translate(text, target_lang)
            else:
                translation = gs.translate(text, target_lang, source_lang)
        except:
            LOGGER.warning('500 Internal Server: Could not translate image.')
            raise web.internalerror(message='Could not translate image.')

        LOGGER.debug('\n---------- Translation ----------\n' + translation + '\n---------- /Translation ----------')
        return translation

    def getLanguage(self, text):
        LOGGER.info('getLanguage in Enrich called with text.')

        languages = gs.get_languages()
        language = gs.detect(text)

        if language in languages:
            detected_lang = languages[language]
        else:
            detected_lang = 'No language detected.'

        LOGGER.debug('Detected language: ' + detected_lang)

        return detected_lang

    def enrich(self):
        pass

    def getJson(self, text, translation, detected_lang, target_lang, enrich, source_lang=None):
        LOGGER.info('getJson in Enrich called with text, translation and parameters: detected_lang=' + detected_lang + ' and target_lang=' + target_lang + ' and source_lang=' + str(source_lang))

        data = {
            'detected':detected_lang,
            'text':text,
            'translation':translation,
        }

        return json.dumps(data)


def main():
    logging.basicConfig(format='%(levelname)s - %(module)s - [%(asctime)s] "%(message)s"', datefmt='%d/%h/%Y %H:%M:%S', level=logging.DEBUG)
    LOGGER.info('Main called for CTE REST Server.')

    if not (os.path.isdir('uploads') and os.path.exists('uploads')):
        os.makedirs('uploads')

    app = web.application(urls, globals())
    app.run()

    LOGGER.info('REST Server for CTE shutdown.')


if __name__ == '__main__':
    main()