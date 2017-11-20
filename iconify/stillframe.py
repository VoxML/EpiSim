import model
from episim import CONCEPT_HEIGHT, CONCEPT_WIDTH

gesture_image_mapping = {
    "posack": "thumbs_up.png",
    "negack": "thumbs_down.png",
    "grasp": "claw.png",
    "point": "point.png",
    "push_left": "push_side.png",
    "push_right": "push_side.png",
    "push_forward": "push_front.png",
    "push_back": "push_back.png",
}


def iconify(concept):
    if concept.modality == model.ConceptMode.G:
        return iconify_gesture(concept)
    elif concept.modality == model.ConceptMode.L:
        return iconify_language(concept)


def iconify_language(concept):
    return get_concept_text(concept)


def get_concept_text(concept):
    return concept.name + '-' + concept.modality.name


def iconify_gesture(concept):
    concept_text = get_concept_text(concept)
    try:
        return '<img src="/static/images/{}" alt="{}" width="{}" height="{}">'.format(
            gesture_image_mapping[concept.name], concept_text, CONCEPT_WIDTH*0.9, CONCEPT_HEIGHT*0.9)
    except KeyError:
        return concept_text
