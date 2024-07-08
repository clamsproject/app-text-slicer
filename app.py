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

from mmif.utils import text_document_helper as tdh
from collections import defaultdict


class TextSlicer(ClamsApp):

    def __init__(self):
        super().__init__()

    def _appmetadata(self):
        pass

    def _annotate(self, mmif: Mmif, **parameters) -> Mmif:
        self.mmif = mmif if isinstance(mmif, Mmif) else Mmif(mmif)
        self.text_doc = self.mmif.get_documents_by_type(DocumentTypes.TextDocument)
        assert len(self.text_doc) == 1, "There should be exactly one TextDocument in the MMIF file"

        # Read in user-chosen runtime parameters
        label_set = set(parameters["containLabel"])
        run_mode = parameters["runMode"]

        # Register a new View in mmif object
        new_view = self.mmif.new_view()
        self.sign_view(new_view, parameters)

        label_to_tf = defaultdict(list)
        for tf_view in self.mmif.get_all_views_contain(AnnotationTypes.TimeFrame):
            tf_anns = tf_view.get_annotations(AnnotationTypes.TimeFrame)
            for ann in tf_anns:
                label = ann.get_property('label')
                if label in label_set:
                    label_to_tf[label].append(ann)

        for _, tfs in label_to_tf.items():
            if run_mode == 'regular':
                for tf in tfs:
                    sliced_text = new_view.new_textdocument(tdh.slice_text(self.mmif, tf.get('start'), tf.get('end')))
                    new_alignment = new_view.new_annotation(at_type=AnnotationTypes.Alignment,
                                                            properties={'source': tf.long_id, 'target': sliced_text.long_id})
            elif run_mode == 'enrich':
                for tf1, tf2 in zip(tfs[:-1], tfs[1:]):
                    sliced_text = new_view.new_textdocument(tdh.slice_text(self.mmif, tf1.get('start'), tf2.get('start')))
                    #FIXME: Current idea is to align both timeframes to the same sliced text. This may not be the best! 
                    first_new_alignment = new_view.new_annotation(at_type=AnnotationTypes.Alignment,
                                                            properties={'source': tf1.long_id, 'target': sliced_text.long_id})
                    second_new_alignment = new_view.new_annotation(at_type=AnnotationTypes.Alignment,
                                                            properties={'source': tf2.long_id, 'target': sliced_text.long_id})
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
