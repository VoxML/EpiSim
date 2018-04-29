import model
from episim import CONCEPT_HEIGHT, CONCEPT_WIDTH

LANGUAGE_FONTSIZE = 30

gesture_image_mapping = {
    "posack": "thumbs_up.gif",
    "negack": "thumbs_down.gif",
    "point": "point.gif",
    "push": "push.gif",
    "grab": "claw.gif",
    "grasp": "claw.gif",
    "move": "move.gif",
    "RIGHT": "right.png",
    "LEFT": "left.png",
    "UP": "up.png",
    "DOWN": "down.png",
    "FRONT": "forward.png",
    "BACK": "back.png",
    "block1": "block1.png",
    "block2": "block2.png",
    "block3": "block3.png",
    "block4": "block4.png",
    "block5": "block5.png",
    "block6": "block6.png",
    "block7": "block7.png",
    "block8": "block8.png",
    "RED": "red.png",
    "GREEN": "green.png",
    "YELLOW": "yellow.png",
    "ORANGE": "orange.png",
    "BLACK": "black.png",
    "PURPLE": "purple.png",
    "WHITE": "white.png",
}


def iconify(concept):
    if concept.modality == model.ConceptMode.G:
        return iconify_gesture(concept)
    elif concept.modality == model.ConceptMode.L:
        return iconify_language(concept)


def iconify_language(concept):
    return '<p style="font-size:{fs}px">{ctext}</p>'.format(
        fs=LANGUAGE_FONTSIZE,
        ctext=get_concept_text(concept))


def get_concept_text(concept):
    return concept.name + '-' + concept.modality.name


def iconify_gesture(concept):
    concept_text = get_concept_text(concept)
    try:
        return '<img src="/static/gifs/{}" alt="{}" width="{}" height="{}" border="1">'.format(
            gesture_image_mapping[concept.name], concept_text, CONCEPT_WIDTH*0.9, CONCEPT_HEIGHT*0.9)
    except KeyError:
        return iconify_language(concept)


