import sys
import pickle
import math

graphmlfile = sys.argv[1]
statefile = graphmlfile.replace(".graphml", ".state")

with open(statefile, "rb") as f:
    state = pickle.load(f)

# et puis on trace la roue:

pos=state.draw(output="blockmodel_simple_filtered.png",vertex_text=state.g.vertex_properties['label'],vertex_text_position=1,output_size=(2048, 2048),vertex_size=1)
position=pos[2]

text_rot = state.g.new_vertex_property('double')
state.g.vertex_properties['text_rot'] = text_rot
for v in state.g.vertices():
    if position[v][0] >0:
        text_rot[v] = math.atan(position[v][1]/position[v][0])
    else:
        text_rot[v] = math.pi + math.atan(position[v][1]/position[v][0])

state.draw(output="hyphe_nested_bm_noncorr3_filteredcorr.png",vertex_text=state.g.vertex_properties['label'],vertex_text_rotation=state.g.vertex_properties['text_rot'],vertex_size=1,vertex_text_position=1,output_size=(3072, 3072))

print("Wheel drawn")

