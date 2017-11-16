#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program is to:

"""


__author__ = 'krim'
__date__ = '10/24/2017'
__email__ = 'krim@brandeis.edu'

from enum import Enum


class ConceptType(Enum):
    ACTION = 0
    OBJECT = 1
    PROPERTY = 2


class ConceptMode(Enum):
    L = 0
    G = 1


class Concept(object):

    def __init__(self, name, ctype, cmode):
        super().__init__()
        self.name = name
        self.type = ctype
        self.modality = cmode

    def __eq__(self, other):
        return isinstance(other, Concept) \
               and self.type == other.type \
               and self.modality == other.modality \
               and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name + self.modality.name)


class Concepts(object):

    def __init__(self):
        super().__init__()
        self.concepts = {modality: [] for modality in ConceptMode}
        # stores relations between entities
        # keys are tuples of two entity names
        # values can be 0 for unidirectional, 1 for bidirectional
        self.relations = {}

    def __len__(self):
        return sum(len(v) for _, v in self.concepts)

    def get_concept(self, cmode, cidx):
        return self.concepts[cmode][cidx]

    def get_index_or_add(self, concept):
        try:
            return self.concepts[concept.modality].index(concept)
        except ValueError:
            self.add(concept)
            return len(self.concepts[concept.modality])

    def add(self, concept):
        self.concepts[concept.modality].append(concept)

    def add_relation(self, c1, c2):
        if (c2, c1) in self.relations:
            self.relations[(c2, c1)] = 1
        else:
            self.relations[(c1, c2)] = 0

    def has_relation(self, e1, e2):
        """
        See of two entities are related.

        :param e1:
        :param e2:
        :return: None if not related at all,
                0 for unidirectional relation (depend on),
                1 for bidirectional one (equivalent)
        """
        return self.relations.get((e1, e2), self.relations.get((e2, e1), None))

