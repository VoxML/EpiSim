from flask import Flask, render_template, jsonify, request
from model import Concepts, Concept, ConceptType, ConceptMode
from iconify import stillframe

# some constants
CONCEPT_ID_SEP = ':'
JSON_RELATION_SUFFIX = '-relations'
JSON_RELATION_CONNECTOR = '-'
INIT_XOFFSET = 100
INIT_YOFFSET = 200
CONCEPT_WIDTH = 80
CONCEPT_HEIGHT = 80
HOR_INTERVAL = int(CONCEPT_WIDTH * 0.1)
UNAWARE_COLOR = "238,200,200"
AWARE_COLOR = "20,200,238"

# initialize global variables
concepts = {}
initialized = False
queue = {}

# and initialize flask app
app = Flask(__name__)


def get_xoffset(cidx):
    return INIT_XOFFSET + int(cidx) * (CONCEPT_WIDTH + HOR_INTERVAL)


def get_yoffset(ctype, cmode=ConceptMode(0)):
    return INIT_YOFFSET * (ctype.value + 1) + (CONCEPT_HEIGHT * ctype.value * 3) + (CONCEPT_HEIGHT * cmode.value * 2)


def get_anchor(ctype, cidx, cmode):
    x = get_xoffset(cidx) + CONCEPT_WIDTH / 2 - 10
    y = get_yoffset(ctype, cmode) + CONCEPT_HEIGHT * (-cmode.value + 1) - 10
    return {'x': str(x), 'y': str(y)}


def get_all_relations_svgs():
    all_lines = []
    for ctype in concepts:
        all_lines.extend([get_relation_line(ctype, relation)
                          for relation in concepts[ctype].relations.items()])
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
        idx = concepts[ctype].get_index_or_add(x)
        prepped['ctype'] = type.value
        prepped['cmode'] = mode.value
        prepped['cidx'] = idx
        prepped.update(get_anchor(type, idx, mode))
        return prepped
    orig, dest = map(lambda x: prep(x), relation[0])
    return render_template('relation-line.html',
                           ori=orig,
                           dest=dest,
                           color=UNAWARE_COLOR,
                           bidirectional=relation[1] == 1)


def get_all_concepts_divs():
    divs = []
    for ctype in concepts:
        for cmode in concepts[ctype].concepts:
            for cidx, concept in enumerate(concepts[ctype].concepts[cmode]):
                divs.append(get_concept_div(ctype, cidx, cmode, get_representation(concept)))
    return '\n'.join(divs)


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
    return stillframe.iconify(concept)


@app.route('/init', methods=['POST'])
def init():
    global initialized
    global concepts

    inp_json = request.get_json()
    concepts[ConceptType.ACTION] = get_concepts(inp_json, 'ACTION')
    concepts[ConceptType.OBJECT] = get_concepts(inp_json, 'OBJECT')
    concepts[ConceptType.PROPERTY] = get_concepts(inp_json, 'PROPERTY')
    initialized = True
    return str(initialized)


def get_concepts(concept_json, concept_type):
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
    global concepts
    enqueue()
    #  init()

    if initialized:
        return render_template('visualize.html',
                               defaultcolor=UNAWARE_COLOR,
                               highlightcolor=AWARE_COLOR,
                               divs=get_all_concepts_divs(),
                               svg=get_all_relations_svgs())
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
