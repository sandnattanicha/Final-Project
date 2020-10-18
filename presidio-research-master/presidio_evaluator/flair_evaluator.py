from typing import List

try:
    from flair.data import Sentence, build_spacy_tokenizer
    from flair.models import SequenceTagger
except ImportError:
    print("Flair is not installed by default")

from presidio_evaluator import ModelEvaluator, InputSample
import spacy

from presidio_evaluator.data_objects import PRESIDIO_SPACY_ENTITIES


class FlairEvaluator(ModelEvaluator):

    def __init__(self,
                 model=None,
                 model_path: str = None,
                 entities_to_keep: List[str] = None,
                 verbose: bool = False,
                 labeling_scheme: str = "BIO",
                 compare_by_io: bool = True,
                 translate_to_spacy_entities=True):
        """
        Evaluator for Flair models
        :param model: model of type SequenceTagger
        :param model_path:
        :param entities_to_keep:
        :param verbose:
        :param labeling_scheme:
        :param compare_by_io:
        :param translate_to_spacy_entities:
        """
        super().__init__(entities_to_keep=entities_to_keep,
                         verbose=verbose,
                         labeling_scheme=labeling_scheme,
                         compare_by_io=compare_by_io)

        if model is None:
            if model_path is None:
                raise ValueError("Either model_path or model object must be supplied")
            self.model = SequenceTagger.load(model_path)
        else:
            self.model = model

        self.spacy_tokenizer = build_spacy_tokenizer(model=spacy.blank('en'))
        self.translate_to_spacy_entities = translate_to_spacy_entities

        if self.translate_to_spacy_entities:
            print("Translating entities using this dictionary: {}".format(PRESIDIO_SPACY_ENTITIES))

    def predict(self, sample: InputSample) -> List[str]:
        if self.translate_to_spacy_entities:
            sample.translate_input_sample_tags()
        sentence = Sentence(text=sample.full_text, use_tokenizer=self.spacy_tokenizer)
        self.model.predict(sentence)

        tags = self.get_tags_from_sentence(sentence)
        if len(tags) != len(sample.tokens):
            print("mismatch between previous tokens and new tokens")
        return tags

    @staticmethod
    def get_tags_from_sentence(sentence):
        tags = []
        for token in sentence:
            tags.append(token.get_tag('ner').value)

        new_tags = []
        for tag in tags:
            new_tags.append("PERSON" if tag == "PER" else tag)

        return new_tags
