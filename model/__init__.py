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
    PROPERTY = 1
    OBJECT = 2


class ConceptMode(Enum):
    L = 0
    G = 1


class PropertyType(Enum):
    Nominal = 0
    Ordinal = 1


class PropertyGroup(object):
    def __init__(self, name, ptype):
        super().__init__()
        self.name = name;
        self.ptype = ptype
        self.members = [[], []]

    def add_member(self, property_mode, property_idx):
        self.members[property_mode.value].append(property_idx)

    def is_ungrouped(self):
        return not self.name and not self.ptype

    def __repr__(self):
        return '{}: {}'.format(self.name, self.ptype.name)


class Concept(object):

    def __init__(self, name, ctype, cmode):
        super().__init__()
        self.name = name
        self.type = ctype
        self.modality = cmode
        self.subgroup_name = None

    def __eq__(self, other):
        return isinstance(other, Concept) \
               and self.type == other.type \
               and self.modality == other.modality \
               and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name + self.modality.name)

    def __repr__(self):
        return '{}::{}::{}::{}'.format(self.name, self.type, self.modality, self.subgroup_name)

    def subgroup(self, subgroup_name):
        if self.type != ConceptType.PROPERTY:
            raise ValueError(self.__class__.__name__ + "cannot have different a " + ctype.__class__.__name__)
        self.subgroup_name = subgroup_name


class Concepts(object):

    def __init__(self):
        super().__init__()
        self.concepts = {modality: [] for modality in ConceptMode}
        # stores relations between entities
        # keys are tuples of two entity names
        # values can be 0 for unidirectional, 1 for bidirectional
        self.relations = {}
        self.prop_groups = [PropertyGroup(None, None)]

    def __len__(self):
        return sum(len(v) for _, v in self.concepts)

    def add_prop_group(self, name, type):
        self.prop_groups.append(PropertyGroup(name, type))

    def get_prop_group(self, name):
        for prop_group in self.prop_groups:
            if prop_group.name == name:
                return prop_group
        return None

    def get_concept(self, cmode, cidx):
        return self.concepts[cmode][cidx]

    def get_index(self, concept):
        if concept.type is not ConceptType.PROPERTY:
            return self.concepts[concept.modality].index(concept)
        else:
            return self.reindex(concept)

    def reindex(self, concept):
        """
        only for property type - order of concepts in the internal list and that on screen are diff
        :param concept:
        :return:
        """
        ori_idx = self.concepts[concept.modality].index(concept)
        idx = 0
        for group in self.prop_groups:
            if group.name != concept.subgroup_name:
                idx += len(group.members[concept.modality.value])
            else:
                idx += group.members[concept.modality.value].index(ori_idx)
                break
        return idx

    def add(self, concept):
        concept_idx = len(self.concepts[concept.modality])
        self.concepts[concept.modality].append(concept)
        if concept.type == ConceptType.PROPERTY:
            self.get_prop_group(concept.subgroup_name).add_member(concept.modality, concept_idx)

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

