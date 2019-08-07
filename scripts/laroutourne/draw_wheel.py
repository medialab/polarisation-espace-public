import os
import sys
import math
import pickle

graphmlfile = sys.argv[1]

if len(sys.argv) > 2:
    NB_ITERS = int(sys.argv[2])
else:
    NB_ITERS = 200000

if len(sys.argv) > 3:
    IMG_WIDTH = int(sys.argv[3])
else:
    IMG_WIDTH = 3072

statefile = graphmlfile.replace(".graphml", "") + "-%s.state" % NB_ITERS

with open(statefile, "rb") as f:
    state = pickle.load(f)

tmp_wheel = "blockmodel_simple_filtered-%s-%s.png" % (NB_ITERS, IMG_WIDTH)
pos=state.draw(output=tmp_wheel, vertex_text=state.g.vertex_properties['label'], vertex_text_position=1, output_size=(1, 1), vertex_size=1)
position = pos[2]
os.remove(tmp_wheel)

print("Temp wheel drawn...")

text_rot = state.g.new_vertex_property('double')
state.g.vertex_properties['text_rot'] = text_rot
for v in state.g.vertices():
    if position[v][0] > 0 :
        text_rot[v] = math.atan(position[v][1]/position[v][0])
    else:
        text_rot[v] = math.pi + math.atan(position[v][1]/position[v][0])

state.draw(output="hyphe_nested_bm_noncorr3_filteredcorr-%s-%s.png" % (NB_ITERS, IMG_WIDTH), vertex_text=state.g.vertex_properties['label'], vertex_text_rotation=state.g.vertex_properties['text_rot'], vertex_size=1, vertex_text_position=1, output_size=(IMG_WIDTH, IMG_WIDTH))

print("Wheel drawn")

