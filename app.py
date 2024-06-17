"""
DELETE THIS MODULE STRING AND REPLACE IT WITH A DESCRIPTION OF YOUR APP.

app.py Template

The app.py script does several things:
- import the necessary code
- create a subclass of ClamsApp that defines the metadata and provides a method to run the wrapped NLP tool
- provide a way to run the code as a RESTful Flask service


"""

import argparse
import logging

# Imports needed for Clams and MMIF.
# Non-NLP Clams applications will require AnnotationTypes

from clams import ClamsApp, Restifier
from mmif import Mmif, View, Annotation, Document, AnnotationTypes, DocumentTypes

# For an NLP tool we need to import the LAPPS vocabulary items
from lapps.discriminators import Uri

from mmif.utils import text_document_helper


class TextSlicer(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        # see https://sdk.clams.ai/autodoc/clams.app.html#clams.app.ClamsApp._load_appmetadata
        # Also check out ``metadata.py`` in this directory.
        # When using the ``metadata.py`` leave this do-nothing "pass" method here.
        pass

    def _annotate(self, mmif: Mmif, **parameters) -> Mmif:
        start_time = parameters["start_time"]
        end_time = parameters["end_time"]
        unit = parameters["unit"]

        self.mmif = mmif if isinstance(mmif, Mmif) else Mmif(mmif)
        new_view = self._add_new_view(parameters)
        self._run_nlp_tool(start_time, end_time, unit, new_view)
        return self.mmif

    def _add_new_view(self, runtime_config):
        view = self.mmif.new_view()
        view.metadata.app = self.metadata.identifier
        self.sign_view(view, runtime_config)
        view.new_contain(DocumentTypes.TextDocument)
        return view

    def _run_nlp_tool(self, s, e, unit, new_view):
        sliced_texts = text_document_helper.slice_text(self.mmif, s, e, unit)
        ntd = new_view.new_textdocument(sliced_texts)

        # for tf_view in mmif.get_all_views_contain(AnnotationTypes.TimeFrame):
        #     if Uri.TOKEN in tf_view.metadata.contains:
        #         asr_vid = tf_view.id
        #         break
        # sliced_texts = []
        # for ann in mmif.get_annotations_between_time(start_time, end_time, unit):
        #     if ann.is_type(Uri.TOKEN) and ann.long_id.startswith(asr_vid):
        #         sliced_texts.append(ann.get('word'))
        # new_view = mmif.new_view()
        # self.sign_view(new_view, parameters)
        # ntd = new_view.new_textdocument(' '.join(sliced_texts))
        # return mmif

        # see https://sdk.clams.ai/autodoc/clams.app.html#clams.app.ClamsApp._annotate


def get_app():
    """
    This function effectively creates an instance of the app class, without any arguments passed in, meaning, any
    external information such as initial app configuration should be set without using function arguments. The easiest
    way to do this is to set global variables before calling this.
    """
    # for example:
    return TextSlicer()
    # raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", action="store", default="5000", help="set port to listen")
    parser.add_argument("--production", action="store_true", help="run gunicorn server")
    # add more arguments as needed
    # parser.add_argument(more_arg...)

    parsed_args = parser.parse_args()

    # create the app instance
    # if get_app() call requires any "configurations", they should be set now as global variables
    # and referenced in the get_app() function. NOTE THAT you should not change the signature of get_app()
    app = get_app()

    http_app = Restifier(app, port=int(parsed_args.port))
    # for running the application in production mode
    if parsed_args.production:
        http_app.serve_production()
    # development mode
    else:
        app.logger.setLevel(logging.DEBUG)
        http_app.run()
