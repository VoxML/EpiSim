import model
from episim import CONCEPT_HEIGHT, CONCEPT_WIDTH

gesture_image_mapping = {
    "posack": "thumbs_up.gif",
    "negack": "thumbs_down.gif",
    "point": "point.gif",
    "push": "push.gif",
    "grab": "claw.gif",
    "grasp": "claw.gif",
    "move": "move.gif",
    "right": "right.png",
    "left": "left.png",
    "up": "up.png",
    "down": "down.png",
    "forward": "forward.png",
    "back": "back.png",
    "block1": "block1.png",
    "block2": "block2.png",
    "block3": "block3.png",
    "block4": "block4.png",
    "block5": "block5.png",
    "block6": "block6.png",
    "block7": "block7.png",
    "block8": "block8.png",
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
        return '<img src="/static/gifs/{}" alt="{}" width="{}" height="{}">'.format(
            gesture_image_mapping[concept.name], concept_text, CONCEPT_WIDTH*0.9, CONCEPT_HEIGHT*0.9)
    except KeyError:
        return concept_text
