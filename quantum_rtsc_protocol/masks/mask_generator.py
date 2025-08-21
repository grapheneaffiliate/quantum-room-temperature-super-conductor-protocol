"""
Mask Generator for RTSC Protocol Devices

This script generates a GDSII file for fabricating four-probe devices,
van der Pauw structures, and optional Josephson junctions for the
Quantum RTSC Protocol.

Key Features:
- Parametric design for easy customization
- Generates multiple device geometries
- Includes alignment marks for lithography
- Outputs standard GDSII format for mask fabrication

Dependencies:
- gdstk
- numpy

Installation:
pip install gdstk numpy

Usage:
python mask_generator.py --output_file rtsc_protocol.gds
"""

import gdstk
import numpy as np
import argparse

def create_alignment_marks(lib, layer=0, size=100, cross_width=10):
    """Creates cross-style alignment marks."""
    cross = gdstk.cross((0, 0), size, cross_width, layer=layer)
    return cross

def create_four_probe_device(lib, x, y, bar_length=2000, bar_width=200, pad_size=200, layer=1):
    """Creates a four-probe (Hall bar) device."""
    cell = lib.new_cell(f'FourProbe_{bar_length}x{bar_width}')
    
    # Main bar
    main_bar = gdstk.rectangle((-bar_length / 2, -bar_width / 2), (bar_length / 2, bar_width / 2), layer=layer)
    cell.add(main_bar)

    # Voltage probes
    probe_spacing = bar_length / 3
    probe_width = bar_width * 1.5
    probe_length = pad_size
    
    v1_pos = -probe_spacing / 2
    v2_pos = probe_spacing / 2

    v1 = gdstk.rectangle((v1_pos - probe_width / 2, -bar_width / 2), (v1_pos + probe_width / 2, -bar_width / 2 - probe_length), layer=layer)
    v2 = gdstk.rectangle((v2_pos - probe_width / 2, -bar_width / 2), (v2_pos + probe_width / 2, -bar_width / 2 - probe_length), layer=layer)
    cell.add(v1, v2)

    # Current pads
    i_pad1 = gdstk.rectangle((-bar_length / 2 - pad_size, -pad_size / 2), (-bar_length / 2, pad_size / 2), layer=layer)
    i_pad2 = gdstk.rectangle((bar_length / 2, -pad_size / 2), (bar_length / 2 + pad_size, pad_size / 2), layer=layer)
    cell.add(i_pad1, i_pad2)

    # Voltage pads
    v_pad1 = gdstk.rectangle((v1_pos - pad_size / 2, -bar_width / 2 - probe_length - pad_size), (v1_pos + pad_size / 2, -bar_width / 2 - probe_length), layer=layer)
    v_pad2 = gdstk.rectangle((v2_pos - pad_size / 2, -bar_width / 2 - probe_length - pad_size), (v2_pos + pad_size / 2, -bar_width / 2 - probe_length), layer=layer)
    cell.add(v_pad1, v_pad2)

    return gdstk.Reference(cell, (x, y))

def create_vdp_device(lib, x, y, size=500, pad_size=200, layer=2):
    """Creates a van der Pauw device."""
    cell = lib.new_cell(f'VDP_{size}x{size}')
    
    # Main square
    main_square = gdstk.rectangle((-size / 2, -size / 2), (size / 2, size / 2), layer=layer)
    cell.add(main_square)

    # Pads at corners
    positions = [(-size / 2, -size / 2), (size / 2, -size / 2), (-size / 2, size / 2), (size / 2, size / 2)]
    for px, py in positions:
        pad = gdstk.rectangle((px - pad_size / 2, py - pad_size / 2), (px + pad_size / 2, py + pad_size / 2), layer=layer)
        cell.add(pad)
        
    return gdstk.Reference(cell, (x, y))

def create_dayem_bridge(lib, x, y, bridge_length=0.2, bridge_width=0.1, pad_size=100, layer=3):
    """Creates a Dayem bridge Josephson junction."""
    cell = lib.new_cell(f'Dayem_{bridge_length}x{bridge_width}')
    
    # Pads
    pad1 = gdstk.rectangle((-pad_size / 2 - bridge_length / 2, -pad_size / 2), (-bridge_length / 2, pad_size / 2), layer=layer)
    pad2 = gdstk.rectangle((bridge_length / 2, -pad_size / 2), (pad_size / 2 + bridge_length / 2, pad_size / 2), layer=layer)
    cell.add(pad1, pad2)

    # Bridge
    bridge = gdstk.rectangle((-bridge_length / 2, -bridge_width / 2), (bridge_length / 2, bridge_width / 2), layer=layer)
    cell.add(bridge)

    return gdstk.Reference(cell, (x, y))

def main():
    parser = argparse.ArgumentParser(description="Generate GDSII mask file for RTSC protocol devices.")
    parser.add_argument("--output_file", type=str, default="rtsc_protocol.gds", help="Output GDSII file name.")
    parser.add_argument("--chip_size", type=float, default=10000.0, help="Size of the chip in microns.")
    args = parser.parse_args()

    lib = gdstk.Library()
    main_cell = lib.new_cell('Main')

    # Chip boundary
    chip_boundary = gdstk.rectangle((-args.chip_size / 2, -args.chip_size / 2), (args.chip_size / 2, args.chip_size / 2), layer=10)
    main_cell.add(chip_boundary)

    # Alignment marks at corners
    mark_offset = args.chip_size / 2 - 500
    positions = [(-mark_offset, -mark_offset), (mark_offset, -mark_offset), (-mark_offset, mark_offset), (mark_offset, mark_offset)]
    for x, y in positions:
        mark = create_alignment_marks(lib)
        main_cell.add(gdstk.Reference(mark, (x, y)))

    # Device layout
    device_spacing = 3000
    
    # Four-probe devices
    fp1 = create_four_probe_device(lib, -device_spacing, device_spacing, bar_length=2000, bar_width=200)
    fp2 = create_four_probe_device(lib, 0, device_spacing, bar_length=1000, bar_width=100)
    fp3 = create_four_probe_device(lib, device_spacing, device_spacing, bar_length=500, bar_width=50)
    main_cell.add(fp1, fp2, fp3)

    # Van der Pauw devices
    vdp1 = create_vdp_device(lib, -device_spacing, 0, size=500)
    vdp2 = create_vdp_device(lib, 0, 0, size=250)
    vdp3 = create_vdp_device(lib, device_spacing, 0, size=100)
    main_cell.add(vdp1, vdp2, vdp3)

    # Dayem bridges
    db1 = create_dayem_bridge(lib, -device_spacing, -device_spacing, bridge_length=0.2, bridge_width=0.1)
    db2 = create_dayem_bridge(lib, 0, -device_spacing, bridge_length=0.1, bridge_width=0.05)
    db3 = create_dayem_bridge(lib, device_spacing, -device_spacing, bridge_length=0.5, bridge_width=0.2)
    main_cell.add(db1, db2, db3)

    # Save to GDS file
    lib.write_gds(args.output_file)
    print(f"Successfully generated GDS file: {args.output_file}")
    print("\nLayers used:")
    print("Layer 0: Alignment Marks")
    print("Layer 1: Four-Probe Devices")
    print("Layer 2: Van der Pauw Devices")
    print("Layer 3: Dayem Bridges")
    print("Layer 10: Chip Boundary")

if __name__ == "__main__":
    main()
