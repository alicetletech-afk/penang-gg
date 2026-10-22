# Hello, Penang — George Town artwork review

This focused revision continues the existing Penang map, coastline polygon, coordinate projection, and destination anchors. It adds a denser illustrated George Town fabric and dedicated close-up proofs. No website files, itinerary data, route lines, Three.js, or runtime 3D were added.

## George Town review proofs

- `george-town-final-label-free.png` — 1200 × 1200 close-up, labels omitted.
- `george-town-final-labeled.png` — same crop with restrained title-case landmark and neighborhood labels.
- `george-town-mobile-390.png` — static 390 × 844 viewport proof.
- `george-town-mobile-430.png` — static 430 × 932 viewport proof.
- `george-town-landmark-assets.png` — transparent Blender landmark render comparison.
- `george-town-placement-diagnostic.png` — fixed geographic anchors (blue), illustration bounds (red), and display-offset vectors.

The phone images are static composition proofs; their pictured controls are not functional. The placement report is `placement-diagnostics.json`. The generated views report zero asset/label bounding-box intersections; the test is a layout check, not a functional website test.

## Editable map and source

- `penang-base.svg` — label-free full-island SVG; the George Town fabric is also grouped under `george-town-urban`.
- `penang-george-town-urban.svg` — standalone, transparent George Town city-fabric SVG overlay using the same projection and island clip.
- `penang-labels.svg` — labels kept in separate full, north, George Town, and mobile viewport groups.
- `penang.blend` and `penang_scene.py` — editable Blender landmark scene and source script.
- `assets/landmarks/*.webp` — existing transparent Blender landmark renders.
- `build_penang_map.py`, `render_base.cjs`, and `build_previews.py` — map, raster and preview build scripts.
- `locations.json` — canonical latitude/longitude anchors, projected positions, per-view illustration offsets and size factors, viewports, and label policy.
- `data/penang-island.geojson` — retained OpenStreetMap-derived Penang Island polygon.
- `penang-map.png` and `penang-map.webp` — full-island raster exports from the same base map.

The city road/block illustration follows a simplified north-east street rhythm and is hand-drawn vector artwork. A live OpenStreetMap street query could not be retrieved in this environment, so these lines and block shapes are approximate and are not presented as surveyed street centerlines or building footprints. The island outline remains based on the retained OSM-derived data; attribution is © OpenStreetMap contributors, available under ODbL.

## Known placeholders and limitations

- The dense shophouse rows, road canyons, courtyards, Chinatown and Little India cues are editorial illustrations. Individual footprints and exact local street alignments are not geodata. The south/west of the island remains quieter than the north.
- Blender assets are stylized clay approximations. Town Hall/City Hall use a simplified civic mass with arches and a clock feature; Loop on Leith is a generic hotel mass; Hin Bus Depot is a simplified warehouse; the ferry museum and terminal are generic ferry/quay forms; Chew Jetty is a small cottage row and does not yet have a convincing stilt-house pier; the heritage group is a shared shophouse illustration for three nearby anchors. These assets remain the main architectural placeholders for a later art pass.
- Ferry/jetty display offsets are illustration-only. Blue anchors in the diagnostic remain at the unchanged geographic coordinates; the connections are illustrative rather than engineering-accurate waterfront infrastructure.
- Label visibility and collision-aware placements are prepared for these viewports only. No responsive behavior has been integrated into the original website.
- Pan, pinch zoom, double-tap zoom, functional fit-to-island, pins, modals, route lines, animation, and itinerary changes are not included.

## Rebuild

From this `outputs` directory, with Blender 5.x, Python 3 and Pillow, and Node.js with `sharp` available:

```sh
python3 build_penang_map.py
node render_base.cjs
blender -b --python penang_scene.py
python3 build_previews.py
```

`render_base.cjs` writes an intermediate raster to `../work/penang-base-preview.png`.
