import gdspy, os

def make_hall_bar(L=50e-6, W=10e-6, pad=100e-6):
    lib = gdspy.GdsLibrary()
    cell = lib.new_cell("HALL_BAR")
    rect = gdspy.Rectangle((0, -W/2), (L, W/2), layer=1)
    # simple side pads
    pads = [
        gdspy.Rectangle((-pad, -pad), (0, pad), layer=2),
        gdspy.Rectangle((L, -pad), (L+pad, pad), layer=2),
    ]
    cell.add([rect, *pads])
    return lib

if __name__ == "__main__":
    os.makedirs("masks", exist_ok=True)
    lib = make_hall_bar()
    lib.write_gds("masks/demo.gds")
    print("Wrote masks/demo.gds")
