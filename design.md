# Voxsim episteme visualizer

The goal of this application is to provide a separate visualization platform for epistemic models of virtual agents of the Voxsim simulation. 
The app will be developed as a web app using python (and flask library). Ruby was also considered, but ditched as not all ruby libraries seamlessly run on the Windows platform (which the Surface tablet runs on). Python and flask seem to be more robust on Windows, and relatively light-weight. 

## API

The app provides 4 entry points

* `/` : Main index page to provide visualization 
* `/init` : Accepting `POST` requests to initiate a model 
* `/update` : Accepting `POST` requests to update the model (boolean only)
* `/reset` : Accepting `POST` requests to reset the model (set all kowledge to 0s)

As far as we stick to a pre-designed static model (as we do in Nov demo), I won't be worrying about re-building a model on-the-fly.

## General Epistemic Model (in the block world setting)

In current context of the blocks world configuration, I suggest three types of concepts: 

1. Actions : verbs - *put*, *lift*, *push*, etc 
2. Entities : currently the only entities are blocks 
3. Properties : colors and sizes 

At this point, a "concept" is merely a pointer to an item in the vocabulary (linguistic or gestural). 

"Entities" class needs more development. For now, as we only have a single semantic group of properties - *color* properties, "entity" class don't seem to be needed. A "property" can directly indicate an object (e.g. "RED" can refer to the "red block" object). If you add sizes as properties ("BIG"/"LARGE" & "SMALL" are proposed), then we need pointers to the objects. ("BIG" and "RED" as properties, while "bigred block" as a separte pointer)

For each concept, we also need these attributes; 

1. Modality : be presented in audio or gestural form
2. Iconic representation : can be images, emojis, or animation (need more devlepment)
3. Awareness : boolean value to represent the agent's awareness of the concept

There are also relations between concepts in the same class, that can also be "aware"
    1. None - no relation
    1. 0 - unidirectional relation (e.g. depend on)
    1. 1 - bidirectional relation (e.g. equivalent)

For November demo, the model would be a user model and awareness would mean Diana's knowing that the counterpart (a naive user) knows the concept. 

## Data format 

* To avoid writing additional data parser code, I suggest JSON format via restful data transaction. 
* A request to `/init` should be able to pass all concepts (with some identifiers) and their attributes (except for iconic representation value - it is responsibility of the visualizer to come up with that value) as well as their relations. This will be then used to dynamically generate a HTML file with **some visual presence** of all concepts and relations that can finally be served via `/` index page. The `index.html` will be periodically jQeury-ing for new changes delivered to `/update`. The data can and should be fairly complex as it is for one-time initiation. 
    ```json 
    {
        "actions" : [ 
                        { "name": "X", "modality": "G|V", "aware": false }, 
                        ...
                    ], 
        "action-relations" : [ ["action1", "action2"], 
                               ["action2", "action1"], 
                               ["action5", "action7"], ...
                             ],
        "properties" : [ ... ], "entities" : [ ... ], 
        "property-relation" : [ ... ], "entity-relations" : [ ... ] 
    }
    ```

* Requests to `/update` would be rather simple. They will carry boolean values for updated awareness. However it has to have a way to be mapped into existing concepts, for example, fixed indices. At the same time, this has to be compact, as there would be frequent updates. 
    ```json 
    will use entire arrays and bool values 
    {
        "actions" : 00101001101, "action-relations" : 0101011, 
        "entities" : 00001111, "entity-relations" : 0011, 
        "properties" : 110101, "property-relations" : 011
    }
    ```
    or 

    ```json
    sends concept names, assuming that an update only changes awareness from 0 to 1
    {
        "actions" : ["push-v", "grasp-g"], "action-relations" : ["push-g", "push-v"]
    }
    ```

* Requests to `/reset` should be just a kill switch to turn all awareness values to 0. 
