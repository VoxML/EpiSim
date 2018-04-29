from flask import Flask, render_template, jsonify, request

from iconify import anigif
from model import Concepts, Concept, ConceptType, ConceptMode, PropertyType

# some constants
CONCEPT_ID_SEP = ':'
CONCEPT_CERTAINTY_SEP = '::'
JSON_SUBGROUP_SUFFIX = '-subgroups'
JSON_RELATION_SUFFIX = '-relations'
JSON_RELATION_CONNECTOR = '-'
INIT_XOFFSET = 100
INIT_YOFFSET = 200
CONCEPT_WIDTH = 150
CONCEPT_HEIGHT = 150
VER_INTERVAL = 120
ANCHOR_AMEND = 10
BOX_PAD = 6
HOR_INTERVAL = int(CONCEPT_WIDTH * 0.2)
PROP_GROUP_LEGEND_FONTSIZE = 30
UNAWARE_COLOR = "238,200,200"
AWARE_COLOR = "20,200,238"

# initialize global variables
all_concepts = {}
initialized = False
queue = {}

# and initialize flask app
app = Flask(__name__)


def get_xoffset(cidx):
    return INIT_XOFFSET + int(cidx) * (CONCEPT_WIDTH + HOR_INTERVAL)


def get_yoffset(ctype, cmode=ConceptMode(0)):
    return INIT_YOFFSET * (ctype.value + 1) + ((CONCEPT_HEIGHT*2 + VER_INTERVAL) * ctype.value) + (VER_INTERVAL + CONCEPT_HEIGHT) * cmode.value


def get_anchor(ctype, cmode, cidx):
    x = get_xoffset(cidx) + CONCEPT_WIDTH / 2 - ANCHOR_AMEND
    y = get_yoffset(ctype, cmode) + CONCEPT_HEIGHT * (-cmode.value + 1) - ANCHOR_AMEND
    return {'x': str(x), 'y': str(y)}


def get_group_box_anchors(ctype, cmode, begin_idx, end_idx):
    topleft = {'x': get_xoffset(begin_idx) - BOX_PAD,
               'y': get_yoffset(ctype, cmode) - PROP_GROUP_LEGEND_FONTSIZE}
    bottomright = {'x': get_xoffset(end_idx) + CONCEPT_WIDTH + BOX_PAD, # * 2 for compensate padding at topleft point
                   'y': get_yoffset(ctype, cmode) + CONCEPT_HEIGHT }
    return topleft, bottomright


def get_all_relations_svgs():
    all_lines = []
    for ctype in all_concepts:
        all_lines.extend([get_relation_line(ctype, relation)
                          for relation in all_concepts[ctype].relations.items()])
    return render_template('relation-svg.html',
                           x=0,
                           y=0,
                           width=8000,
                           height=CONCEPT_HEIGHT*3*3+INIT_YOFFSET*3,
                           lines='\n'.join(all_lines))


def get_relation_line(ctype, relation):
    """ ctype is ConceptType enum, relation is a tuple of ((c1, c2), relation_type)
     where relation_type is either None=no relation, 0 = uni, 1 = bi-direction"""
    def prep(x):
        prepped = {}
        type = x.type
        mode = x.modality
        idx = all_concepts[ctype].get_index(x)
        prepped['ctype'] = type.value
        prepped['cmode'] = mode.value
        prepped['cidx'] = idx
        prepped.update(get_anchor(type, mode, idx))
        return prepped
    orig, dest = map(lambda x: prep(x), relation[0])
    return render_template('relation-line.html',
                           ori=orig,
                           dest=dest,
                           color=UNAWARE_COLOR,
                           bidirectional=relation[1] == 1)


def get_property_grouping_boxes():
    # for the time being, let's just handle PROP only
    # also currently only handle modality 0, which is language (no gestural properties)

    boxes = []

    ctype = ConceptType.PROPERTY
    subgroups = all_concepts[ctype].prop_groups
    for cmode in [ConceptMode.L, ConceptMode.G]:
        # pass un-grouped concepts
        cur_box = len(subgroups[0].members[cmode.value])
        for group_num, subgroup in enumerate(subgroups[1:]):
            concepts_in_group = len(subgroup.members[cmode.value])
            if concepts_in_group > 0:
                b,e = get_group_box_anchors(ctype, cmode, cur_box, -1 + cur_box + concepts_in_group)
                boxes.append(render_template('subgroup-div.html',
                                             ctype=ctype.value,
                                             cmode=cmode.value,
                                             gnum=group_num,
                                             begin=b,
                                             end=e,
                                             gtext=str(subgroup),
                                             fs=PROP_GROUP_LEGEND_FONTSIZE
                                             ))
            cur_box += concepts_in_group
    if len(boxes) > 0:
        return '\n'.join(boxes)
    return ''

def get_prop_group_legend(text):
    return '<legend style = "font-size:{fs}px;' \
           'color:black;' \
           'font-weight:thin;' \
           '"> {text} < / legend >'.format(fs=PROP_GROUP_LEGEND_FONTSIZE, text=text)


def get_all_concepts_divs():
    divs = []
    labels = {}
    for ctype, typed_concepts in all_concepts.items():
        for cmode, moded_concepts in typed_concepts.concepts.items():
            for cidx, concept in enumerate(moded_concepts):
                if ctype == ConceptType.PROPERTY:
                    divs.append(get_concept_div(ctype, typed_concepts.reindex(concept), cmode, get_representation(concept)))
                else:
                    divs.append(get_concept_div(ctype, cidx, cmode, get_representation(concept)))
                if not (ctype, cmode) in labels:
                    labels[(ctype, cmode)] = get_modality_label(ctype, cmode)
                    # using -1 for cmode of linkages
                    if not (ctype, -1) in labels and (ctype, ConceptMode(0)) in labels and (
                            ctype, ConceptMode(1)) in labels:
                        labels[(ctype, -1)] = get_linkage_label(ctype)
    divs.extend(labels.values())
    return '\n'.join(divs)


def get_modality_label(ctype, cmode):
    return '<div id="label-{ctype}-{cmode}" style="' \
           'width: {w}px;' \
           'line-height: {h}px;' \
           'left: {x}px;' \
           'top: {y}px;' \
           'background: rgba(20,20,20,0);' \
           'border: 1px solid red;' \
           'border-radius: 5px;' \
           'text-align: center;' \
           'font-style: italic;' \
           'font-color: #20a020;' \
           'font-size: {fs}px;' \
           'position: absolute;' \
           '">{label}</div>'.format(
        ctype=ctype.value,
        cmode=cmode.value,
        w=CONCEPT_WIDTH * 0.5,
        h=CONCEPT_HEIGHT * 0.9,
        x=max(10, get_xoffset(0) - CONCEPT_WIDTH * 0.7),
        y=get_yoffset(ctype, cmode) + CONCEPT_HEIGHT * 0.05,
        label=ConceptMode(cmode).name,
        fs=CONCEPT_WIDTH * 0.5
    )


def get_linkage_label(ctype):
    return '<div id="label-{ctype}-l" style="' \
           'width: {w}px;' \
           'line-height: {h}px;' \
           'left: {x}px;' \
           'top: {y}px;' \
           'background: rgba(20,20,20,0);' \
           'border: 1px solid red;' \
           'border-radius: 5px;' \
           'text-align: center;' \
           'font-style: italic;' \
           'font-color: #20a020;' \
           'font-size: {fs}px;' \
           'position: absolute;' \
           '">{label}</div>'.format(
        ctype=ctype.value,
        w=CONCEPT_WIDTH * 0.5,
        h=VER_INTERVAL * 0.9,
        x=max(10, get_xoffset(0) - CONCEPT_WIDTH * 0.7),
        y=get_yoffset(ctype) + CONCEPT_HEIGHT * 1.05,
        label='A',
        fs=CONCEPT_WIDTH * 0.5
    )


def get_concept_div(ctype, cidx, cmode, ctext):
    return render_template('concept-div.html',
                           ctype=str(ctype.value),
                           cmode=str(cmode.value),
                           cid=str(cidx),
                           cwidth=CONCEPT_WIDTH,
                           cheight=CONCEPT_HEIGHT,
                           xoffset=get_xoffset(cidx),
                           yoffset=get_yoffset(ctype, cmode),
                           color=UNAWARE_COLOR,
                           ctext=ctext)


def get_representation(concept):
    return anigif.iconify(concept)


@app.route('/init', methods=['POST'])
def init():
    global initialized
    global all_concepts

    inp_json = request.get_json()
    all_concepts[ConceptType.ACTION] = get_concepts(inp_json, 'ACTION')
    all_concepts[ConceptType.OBJECT] = get_concepts(inp_json, 'OBJECT')
    all_concepts[ConceptType.PROPERTY] = get_concepts(inp_json, 'PROPERTY')
    initialized = True
    return str(initialized)


def get_concepts(concept_json, concept_type):
    if concept_type == 'PROPERTY':
        return get_propery_concepts(concept_json, concept_type)
    else:
        return get_general_concepts(concept_json, concept_type)


def get_propery_concepts(concept_json, concept_type):
    """ Currently we have no gestural vocabulary for properties.
    Thus, I don't worry about reordering indices for relation linking. """
    concepts = Concepts()

    for subgroup in concept_json[concept_type + JSON_SUBGROUP_SUFFIX]:
        concepts.add_prop_group(subgroup['name'], PropertyType[subgroup['type']])

    for concept in concept_json[concept_type]:
        new_concept = Concept(concept['name'],
                              ConceptType[concept_type],
                              ConceptMode[concept['modality']])
        try:
            new_concept.subgroup(concept['subgroup'])
        except KeyError:
            # as subgroup is set to None by default
            pass
        concepts.add(new_concept)
    return concepts


def get_general_concepts(concept_json, concept_type):
    concepts = Concepts()
    for concept in concept_json[concept_type]:
        concepts.add(Concept(concept['name'],
                             ConceptType[concept_type],
                             ConceptMode[concept['modality']]))

    for relation in concept_json[concept_type + JSON_RELATION_SUFFIX]:
        nodes = []
        for node in relation.split(JSON_RELATION_CONNECTOR):
            cmode, cidx = node.split(CONCEPT_ID_SEP)
            nodes.append(concepts.get_concept(ConceptMode[cmode], int(cidx)))
        concepts.add_relation(nodes[0], nodes[1])
    return concepts


def reindex(ctype, cmode, cidx):
    c_collection = all_concepts[ConceptType(int(ctype))]
    concept = c_collection.get_concept(ConceptMode(cmode), int(cidx))
    return c_collection.get_index(concept)


@app.route('/aware', methods=['POST'])
def enqueue():
    global queue
    try:
        for key, val in request.get_json().items():
            # using a set would be more efficient, 
            # however it would cause more problems when serializing it
            # using flask.jsonify
            queue[key] = queue.get(key, [])
            for item in val:
                if key == 'c':
                    c_id, certainty = item.split(CONCEPT_CERTAINTY_SEP)
                    ctype, cmode, cidx = map(int, c_id.split(JSON_RELATION_CONNECTOR))
                    item = '{}{}{}'.format(JSON_RELATION_CONNECTOR.join(map(str, [ctype, cmode, reindex(ctype, cmode, cidx)])),
                                           CONCEPT_CERTAINTY_SEP,
                                           certainty)
                if key == 'r':
                    r_id, certainty = item.split(CONCEPT_CERTAINTY_SEP)
                    ctype, omode, oidx, dmode, didx = map(int, r_id.split(JSON_RELATION_CONNECTOR))
                    item = '{}{}{}'.format(JSON_RELATION_CONNECTOR.join(map(str, [ctype, omode, reindex(ctype, omode, oidx), dmode, reindex(ctype, dmode, didx)])),
                                           CONCEPT_CERTAINTY_SEP,
                                           certainty)

                if item not in queue[key]:
                    queue[key].append(item)
        return "200"
    except:
        return "500"


@app.route('/loop')
def loop():
    global queue
    if len(queue) > 0:
        jsonified = jsonify(queue)
    else:
        jsonified = jsonify(c=[], r=[])
    queue = {}
    return jsonified


@app.route('/')
def index():
    global initialized
    global all_concepts
    enqueue()
    #  init()

    if initialized:
        return render_template('visualize.html',
                               defaultcolor=UNAWARE_COLOR,
                               highlightcolor=AWARE_COLOR,
                               concept_divs=get_all_concepts_divs(),
                               relation_svg=get_all_relations_svgs(),
                               property_boxes=get_property_grouping_boxes(),
                               hr=INIT_YOFFSET*2.5 + CONCEPT_HEIGHT*4 + VER_INTERVAL*2 - ANCHOR_AMEND)
    else:
        return "hello world: " + str(initialized)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        '-p', '--port',
        default=5000,
        type=int,
        action='store',
        nargs='?',
        help='Specify port number to run the app.'
    )
    parser.add_argument(
        '-s', '--host',
        default='127.0.0.1',
        action='store',
        nargs='?',
        help='Specify host name for EpiSim to listen to.'
    )
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
