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
from typing import List

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
        pass

    def _annotate(self, mmif: Mmif, **parameters) -> Mmif:
        self.mmif = mmif if isinstance(mmif, Mmif) else Mmif(mmif)
        self.text_doc = self.mmif.get_documents_by_type(DocumentTypes.TextDocument)
        assert len(self.text_doc) == 1, "There should be exactly one TextDocument in the MMIF file"

        labels = parameters["contain_labels"]
        label_set = set([label.strip() for label in labels.split(',')] if labels else [])

        new_view = self.mmif.new_view()
        self.sign_view(new_view, parameters)

        for tf_view in self.mmif.get_all_views_contain(AnnotationTypes.TimeFrame):
            tf_anns_in_view = tf_view.get_annotations(AnnotationTypes.TimeFrame)
            for tf_ann in tf_anns_in_view:
                if not label_set or tf_ann._get_label() in label_set:
                    start_time = self.mmif.get_start(tf_ann) 
                    end_time = self.mmif.get_end(tf_ann) 
                    sliced_text = new_view.new_textdocument(text_document_helper.slice_text(self.mmif, start_time, end_time))
                    new_align = new_view.new_annotation(at_type=AnnotationTypes.Alignment,
                                                        properties={'source': tf_ann.id, 'target': sliced_text.id}) 

        return self.mmif

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
