import os
import sys
import math
import pickle

def draw_from_state(statefile, img_width):
    with open(statefile, "rb") as f:
        state = pickle.load(f)

    imgfile = statefile.replace(".state", "") + "-%spx.png" % (img_width)
    tmp_wheel = statefile.replace(".state", "-blockmodel_simple_filtered-%spx.png" % (img_width))
    pos = state.draw(
        output=tmp_wheel,
        vertex_text=state.g.vertex_properties['label'],
        vertex_size=1,
        vertex_text_position=1,
        output_size=(1, 1)
    )
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

    state.draw(
        output=imgfile,
        vertex_text=state.g.vertex_properties['label'],
        #vertex_font_size=8,
        vertex_text_rotation=state.g.vertex_properties['text_rot'],
        vertex_size=1,
        vertex_text_position=1,
        output_size=(img_width, img_width)
    )

    print("Wheel drawn")


if __name__ == "__main__":
    statefile = sys.argv[1]
    if len(sys.argv) > 2:
        img_width = int(sys.argv[2])
    else:
        img_width = 3072
    draw_from_state(statefile, img_width)
