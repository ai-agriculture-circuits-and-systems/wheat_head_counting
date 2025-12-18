#!/usr/bin/env python3
"""
Convert wheat_head_counting dataset annotations to COCO JSON format.
Based on the standardized dataset structure specification.

License: CC BY 4.0 (see LICENSE). This script is distributed alongside the
dataset and follows the same usage terms. Cite the original dataset in publications.

Usage examples:
    python scripts/convert_to_coco.py --root . --out annotations --category wheat_heads \
        --splits train val test
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image


def _lower_keys(mapping: Dict[str, str]) -> Dict[str, str]:
    """Return a case-insensitive mapping by lowering keys."""
    return {k.lower(): v for k, v in mapping.items()}


def _read_split_list(split_file: Path) -> List[str]:
    """Read image base names (without extension) from a split file."""
    if not split_file.exists():
        return []
    lines = [line.strip() for line in split_file.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def _image_size(image_path: Path) -> Tuple[int, int]:
    """Return (width, height) for an image path using PIL."""
    try:
        with Image.open(image_path) as img:
            return img.width, img.height
    except Exception as e:
        print(f"Warning: Cannot read image {image_path}: {e}")
        # Return default size for corrupted images
        return 1024, 1024


def _parse_csv_boxes(csv_path: Path) -> List[Dict]:
    """Parse a single per-image CSV file and return COCO-style bboxes.
    
    The parser is resilient to header variants by using case-insensitive
    lookups. Supported schemas:
      - Rectangle: x, y, w/h or dx/dy or width/height
      - Circle: x, y, r (converted to rectangle)
    """
    if not csv_path.exists():
        return []
    
    boxes: List[Dict] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return boxes
        
        header = _lower_keys({k: k for k in reader.fieldnames})
        
        def get(row: Dict[str, str], *keys: str) -> Optional[float]:
            for key in keys:
                if key in row and row[key] not in (None, ""):
                    try:
                        return float(row[key])
                    except ValueError:
                        continue
            return None
        
        for raw_row in reader:
            row = {k.lower(): v for k, v in raw_row.items()}
            x = get(row, "x", "xc", "x_center")
            y = get(row, "y", "yc", "y_center")
            # Circle
            r = get(row, "r", "radius")
            # Rectangle sizes
            w = get(row, "w", "width", "dx")
            h = get(row, "h", "height", "dy")
            label = get(row, "label", "class", "category_id")
            
            if x is None or y is None:
                continue
            
            category_id = int(label) if label is not None else 1
            
            if r is not None:
                # Convert circle to rectangle
                bbox = [x - r, y - r, 2 * r, 2 * r]
                area = (2 * r) * (2 * r)
            elif w is not None and h is not None:
                bbox = [x, y, w, h]
                area = w * h
            else:
                continue
            
            boxes.append({
                "bbox": bbox,
                "area": area,
                "category_id": category_id,
            })
    
    return boxes


def _collect_annotations_for_split(
    category_root: Path,
    split: str,
    category_name: str,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Collect COCO dictionaries for images, annotations, and categories."""
    images_dir = category_root / "images"
    annotations_dir = category_root / "csv"
    sets_dir = category_root / "sets"
    
    split_file = sets_dir / f"{split}.txt"
    image_stems = set(_read_split_list(split_file))
    
    if not image_stems:
        # Fall back to all images if no split file
        image_stems = {p.stem for p in images_dir.glob("*.jpg")}
        image_stems.update({p.stem for p in images_dir.glob("*.png")})
        image_stems.update({p.stem for p in images_dir.glob("*.bmp")})
    
    images: List[Dict] = []
    anns: List[Dict] = []
    categories: List[Dict] = [
        {"id": 1, "name": category_name, "supercategory": "cereal"}
    ]
    
    image_id_counter = 1
    ann_id_counter = 1
    
    for stem in sorted(image_stems):
        img_path = images_dir / f"{stem}.png"
        if not img_path.exists():
            # Try JPG fallback
            img_path = images_dir / f"{stem}.jpg"
            if not img_path.exists():
                # Try BMP fallback
                img_path = images_dir / f"{stem}.bmp"
                if not img_path.exists():
                    continue
        
        try:
            width, height = _image_size(img_path)
            images.append({
                "id": image_id_counter,
                "file_name": f"{category_root.name}/images/{img_path.name}",
                "width": width,
                "height": height,
            })
        except Exception as e:
            print(f"Warning: Skipping image {img_path}: {e}")
            continue
        
        csv_path = annotations_dir / f"{stem}.csv"
        for box in _parse_csv_boxes(csv_path):
            anns.append({
                "id": ann_id_counter,
                "image_id": image_id_counter,
                "category_id": box["category_id"],
                "bbox": box["bbox"],
                "area": box["area"],
                "iscrowd": 0,
            })
            ann_id_counter += 1
        
        image_id_counter += 1
    
    return images, anns, categories


def _build_coco_dict(
    images: List[Dict],
    anns: List[Dict],
    categories: List[Dict],
    description: str,
) -> Dict:
    """Build a complete COCO dict from components."""
    return {
        "info": {
            "year": 2025,
            "version": "1.0.0",
            "description": description,
            "url": "https://zenodo.org/records/5092309/files/gwhd_2021.zip?download=1",
        },
        "images": images,
        "annotations": anns,
        "categories": categories,
        "licenses": [],
    }


def convert(
    root: Path,
    out_dir: Path,
    category: str,
    splits: List[str],
) -> None:
    """Convert selected category and splits to COCO JSON files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    
    category_root = root / category
    
    for split in splits:
        images, anns, categories = _collect_annotations_for_split(
            category_root, split, "wheat_head"
        )
        desc = f"wheat_head_counting {category} {split} split"
        coco = _build_coco_dict(images, anns, categories, desc)
        out_path = out_dir / f"{category}_instances_{split}.json"
        out_path.write_text(json.dumps(coco, indent=2), encoding="utf-8")
        print(f"Generated {out_path} with {len(images)} images and {len(anns)} annotations")


def main() -> int:
    """Entry point for the converter CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Dataset root containing category subfolders (default: dataset root)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "annotations",
        help="Output directory for COCO JSON files (default: <root>/annotations)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="wheat_heads",
        help="Category to convert (default: wheat_heads)",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        type=str,
        default=["train", "val", "test"],
        choices=["train", "val", "test"],
        help="Dataset splits to generate (default: train val test)",
    )
    
    args = parser.parse_args()
    
    convert(
        root=Path(args.root),
        out_dir=Path(args.out),
        category=args.category,
        splits=args.splits,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


