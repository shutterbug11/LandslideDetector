"""
Utility script to clip the nationwide WorldPop population raster to the North Eastern Region (NER).
Run once offline. The clipped output (data/ner_population_2020.tif) is compact (<30MB)
and committed to the repository for production/deployment use.
"""

import os
import sys

NER_BBOX = (88.0, 21.5, 97.5, 29.5)  # minx, miny, maxx, maxy (covers Sikkim & 7 Sister States)

CANDIDATES = [
    os.path.join("data", "raw", "ind_ppp_2020_UNadj_constrained.tif"),
    r"C:\Users\AGNIV GHOSH\Downloads\ind_ppp_2020_UNadj_constrained.tif",
]

def clip_ner_raster(output_path: str = os.path.join("data", "ner_population_2020.tif")):
    import rasterio
    from rasterio.windows import from_bounds

    src_path = None
    for cand in CANDIDATES:
        if os.path.exists(cand):
            src_path = cand
            break

    if not src_path:
        print(f"Error: Source WorldPop raster not found. Looked in: {CANDIDATES}", file=sys.stderr)
        sys.exit(1)

    print(f"Opening source raster: {src_path} ...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with rasterio.open(src_path) as src:
        print(f"Source metadata: {src.meta}")
        window = from_bounds(*NER_BBOX, transform=src.transform).round_offsets().round_shape()
        print(f"Extracting window for bbox {NER_BBOX}: {window} ...")
        
        data = src.read(1, window=window)
        win_transform = src.window_transform(window)
        
        profile = src.profile.copy()
        profile.update({
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": win_transform,
            "compress": "deflate",
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
        })

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(data, 1)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Successfully wrote clipped raster to {output_path}")
    print(f"Output shape: {data.shape}, file size: {file_size_mb:.2f} MB")

if __name__ == "__main__":
    clip_ner_raster()
