"""
Mask Generator for RTSC Protocol
Generates GDSII layout for microbridge and loop structures.
"""

import gdspy

def generate_supercon_mask(filename="supercon.gds"):
    lib = gdspy.GdsLibrary()
    cell = lib.new_cell("RTSC_SUPERCON")

    # Microbridge parameters
    bridge_length = 2e-6   # 2 µm
    bridge_width = 200e-9  # 200 nm

    # Create microbridge rectangle
    bridge = gdspy.Rectangle((0, 0), (bridge_length, bridge_width))
    cell.add(bridge)

    # Add loop (for Little-Parks)
    loop_outer = gdspy.Round((5e-6, 5e-6), 2.5e-6, number_of_points=128)
    loop_inner = gdspy.Round((5e-6, 5e-6), 2.0e-6, number_of_points=128)
    loop = gdspy.boolean(loop_outer, loop_inner, "not")
    cell.add(loop)

    # Save to GDS file
    lib.write_gds(filename)
    print(f"GDS mask saved to {filename}")

if __name__ == "__main__":
    generate_supercon_mask()
