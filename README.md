# Wheat Head Counting Dataset

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-repo/wheat-head-counting)

A comprehensive dataset of wheat field images for head counting and detection, collected and organized for computer vision and deep learning research in agricultural applications.

**Project page**: `https://zenodo.org/records/5092309`

## TL;DR

- **Task**: Object Detection, Counting
- **Modality**: RGB
- **Platform**: Ground/Field
- **Real/Synthetic**: Real
- **Images**: ~1,602 wheat field images from 12+ countries
- **Resolution**: 1024×1024 pixels
- **Annotations**: CSV (per-image), JSON (per-image), COCO JSON (generated)
- **License**: CC BY 4.0
- **Citation**: see below

## Table of Contents

- [Download](#download)
- [Dataset Structure](#dataset-structure)
- [Sample Images](#sample-images)
- [Annotation Schema](#annotation-schema)
- [Stats and Splits](#stats-and-splits)
- [Quick Start](#quick-start)
- [Evaluation and Baselines](#evaluation-and-baselines)
- [Datasheet (Data Card)](#datasheet-data-card)
- [Known Issues and Caveats](#known-issues-and-caveats)
- [License](#license)
- [Citation](#citation)
- [Changelog](#changelog)
- [Contact](#contact)

## Download

**Original dataset**: `https://zenodo.org/records/5092309/files/gwhd_2021.zip?download=1`

This repo hosts structure and conversion scripts only; place the downloaded folders under this directory.

**Local license file**: See `LICENSE` in the root directory.

## Dataset Structure

```
wheat_head_counting/
├── wheat_heads/                          # Main category directory
│   ├── csv/                              # CSV annotation files (per-image)
│   ├── json/                             # JSON annotation files (per-image)
│   ├── images/                           # Image files
│   ├── labelmap.json                     # Label mapping file
│   └── sets/                             # Dataset split files
│       ├── train.txt                     # Training set image list
│       ├── val.txt                        # Validation set image list
│       ├── test.txt                       # Test set image list
│       ├── all.txt                        # All images list
│       └── train_val.txt                  # Train+val images list
│
├── annotations/                          # COCO format JSON files (generated)
│   ├── wheat_heads_instances_train.json
│   ├── wheat_heads_instances_val.json
│   └── wheat_heads_instances_test.json
│
├── scripts/                              # Utility scripts
│   ├── reorganize_dataset.py              # Reorganize dataset to standard structure
│   └── convert_to_coco.py                 # Convert CSV to COCO format
│
├── LICENSE                                # License file
├── README.md                              # This file
└── requirements.txt                       # Python dependencies
```

**Splits**: Splits provided via `wheat_heads/sets/*.txt`. List image basenames (no extension). If missing, all images are used.

## Sample Images

<table>
  <tr>
    <th>Category</th>
    <th>Sample</th>
  </tr>
  <tr>
    <td><strong>Wheat Heads</strong></td>
    <td>
      <img src="wheat_heads/images/0007634580386bd39d4d0d24df58893c3bb967e12d6fc065ce8659e9acacc928.png" alt="Wheat field image" width="260"/>
      <div align="center"><code>wheat_heads/images/0007634580386bd39d4d0d24df58893c3bb967e12d6fc065ce8659e9acacc928.png</code></div>
    </td>
  </tr>
</table>

## Annotation Schema

### CSV Format

Each image has a corresponding CSV annotation file in `wheat_heads/csv/{image_name}.csv`:

```csv
#item,x,y,width,height,label
0,99,692,61,72,1
1,641,27,56,88,1
```

- **Coordinates**: `x, y` - top-left corner of bounding box (pixels)
- **Dimensions**: `width, height` - bounding box dimensions (pixels)
- **Label**: Category ID (1=wheat_head)

### JSON Format (Per-Image)

Each image also has a corresponding JSON annotation file in `wheat_heads/json/{image_name}.json`:

```json
{
  "info": {
    "description": "Wheat head counting dataset",
    "version": "1.0",
    "year": 2025,
    "contributor": "Agricultural AI",
    "source": "augmented",
    "license": {
      "name": "Creative Commons Attribution 4.0 International",
      "url": "https://creativecommons.org/licenses/by/4.0/"
    }
  },
  "images": [
    {
      "id": 5740848120,
      "width": 1024,
      "height": 1024,
      "file_name": "0007634580386bd39d4d0d24df58893c3bb967e12d6fc065ce8659e9acacc928.png",
      "size": 453251,
      "format": "PNG",
      "url": "",
      "hash": "",
      "status": "success"
    }
  ],
  "annotations": [
    {
      "id": 1017940120,
      "image_id": 5740848120,
      "category_id": 1,
      "segmentation": [],
      "area": 3198,
      "bbox": [936, 4, 41, 78]
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "wheat_head",
      "supercategory": "cereal"
    }
  ]
}
```

### COCO Format

COCO format JSON files are generated in the `annotations/` directory. Example structure:

```json
{
  "info": {
    "year": 2025,
    "version": "1.0.0",
    "description": "wheat_head_counting wheat_heads train split",
    "url": "https://zenodo.org/records/5092309/files/gwhd_2021.zip?download=1"
  },
  "images": [
    {
      "id": 1,
      "file_name": "wheat_heads/images/0007634580386bd39d4d0d24df58893c3bb967e12d6fc065ce8659e9acacc928.png",
      "width": 1024,
      "height": 1024
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [936, 4, 41, 78],
      "area": 3198,
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "wheat_head",
      "supercategory": "cereal"
    }
  ],
  "licenses": []
}
```

### Label Maps

Label mapping file is located at `wheat_heads/labelmap.json`:

```json
[
  {
    "object_id": 0,
    "label_id": 0,
    "keyboard_shortcut": "0",
    "object_name": "background"
  },
  {
    "object_id": 1,
    "label_id": 1,
    "keyboard_shortcut": "1",
    "object_name": "wheat_head"
  }
]
```

## Stats and Splits

### Image Statistics

- **Total images**: ~1,602
- **Training set**: ~3,655 images (based on competition_train.csv)
- **Validation set**: ~1,476 images (based on competition_val.csv)
- **Test set**: ~1,381 images (based on competition_test.csv)

Note: The actual number of images may vary. Splits provided via `wheat_heads/sets/*.txt`. You may define your own splits by editing those files.

### Geographic Coverage

Images are collected from multiple research institutions worldwide:

- **Switzerland (ETHZ)**: Usask location, Filling stage
- **UK (RRes)**: Rothamsted location, Filling-Ripening stage
- **Belgium (ULiège-GxABT)**: Gembloux location, Ripening stage
- **Norway (NMBU)**: Multiple locations, Filling and Ripening stages
- **France (Arvalis, INRAE)**: Multiple locations across France
- **Canada (Usask)**: Saskatchewan location
- **US (KSU, Terraref)**: Multiple locations
- **Mexico (CIMMYT)**: Ciudad Obregon location
- **Japan (Utokyo, Ukyoto)**: Multiple locations
- **China (NAU)**: Baima location
- **Australia (UQ)**: Multiple locations
- **Sudan (ARC)**: Wad Medani location

### Development Stages

Images are captured at various wheat development stages:

- **Post-flowering**: Early development stage
- **Filling**: Grain filling stage
- **Ripening**: Mature wheat heads
- **Filling - Ripening**: Transitional stage

## Quick Start

### Load COCO Format Annotations

```python
from pycocotools.coco import COCO
import matplotlib.pyplot as plt

# Load COCO annotation file
coco = COCO('annotations/wheat_heads_instances_train.json')

# Get all image IDs
img_ids = coco.getImgIds()
print(f"Total images: {len(img_ids)}")

# Get all category IDs
cat_ids = coco.getCatIds()
print(f"Categories: {[coco.loadCats(cat_id)[0]['name'] for cat_id in cat_ids]}")

# Load a specific image and its annotations
img_id = img_ids[0]
img_info = coco.loadImgs(img_id)[0]
ann_ids = coco.getAnnIds(imgIds=img_id)
anns = coco.loadAnns(ann_ids)

print(f"Image: {img_info['file_name']}")
print(f"Annotations: {len(anns)}")
```

### Convert CSV to COCO Format

```bash
# Convert wheat_heads category to COCO format
python scripts/convert_to_coco.py --root . --out annotations \
    --category wheat_heads --splits train val test
```

### Dependencies

**Required**:
- Python 3.6+
- Pillow>=9.5

**Optional** (for COCO API):
- pycocotools>=2.0.7

Install dependencies:
```bash
pip install -r requirements.txt
```

## Evaluation and Baselines

### Metrics

- **mAP@[.50:.95]**: Mean Average Precision at IoU thresholds from 0.50 to 0.95
- **mAP@0.50**: Mean Average Precision at IoU threshold 0.50
- **mAP@0.75**: Mean Average Precision at IoU threshold 0.75
- **Counting Accuracy**: Accuracy of wheat head counting

### Baseline Results

(To be added)

## Datasheet (Data Card)

### Motivation

This dataset was created to support research in automated wheat head detection and counting, specifically for crop yield estimation and precision agriculture applications. The dataset enables the development and evaluation of computer vision models for agricultural applications.

### Composition

- **Image Types**: RGB images of wheat fields
- **Categories**: 1 class (wheat_head)
- **Image Format**: PNG
- **Image Size**: 1024×1024 pixels (standardized)
- **Annotation Format**: CSV (per-image), JSON (per-image), COCO JSON (generated)
- **Geographic Coverage**: 12+ countries, 15+ research institutions

### Collection Process

Images were collected from multiple research institutions worldwide as part of the Global Wheat Head Detection 2021 challenge. Each image was annotated with precise bounding boxes for wheat head detection and counting tasks.

### Preprocessing

- Images were standardized to 1024×1024 pixels
- Annotations were created with bounding boxes for each wheat head
- Dataset was split into train/val/test sets based on competition splits

### Distribution

The dataset is distributed under CC BY 4.0 license. See `LICENSE` file for details.

### Maintenance

This repository maintains the standardized structure and conversion scripts. Original data sources should be referenced appropriately.

## Known Issues and Caveats

1. **Image Resolution**: All images are standardized to 1024×1024 pixels. Original resolutions may vary.

2. **Annotation Format**: Bounding boxes are provided in COCO format `[x, y, width, height]` where `(x, y)` is the top-left corner.

3. **File Naming**: Image filenames use hash-based naming for uniqueness (SHA-256 hashes).

4. **Supercategory**: The supercategory is set to "cereal" (not "broccoli" as mentioned in some original documentation).

5. **Split Files**: Split files contain image basenames without extensions. Ensure proper handling when processing files.

6. **Data Source**: This dataset is based on the Global Wheat Head Dataset 2021 (GWHW 2021) challenge data.

## License

This dataset is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

Check the original dataset terms and cite appropriately.

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{wheat_head_counting_2021,
  title={Global Wheat Head Detection 2021},
  author={David, Etienne and Madec, Simon and Sadeghi-Tehran, Pouria and Aasen, Helge and Zheng, Bangyou and Liu, Shouyang and Kirchgessner, Norbert and Ishikawa, Goro and Nagasawa, Koji and Badhon, Minhajul A. and Pozniak, Curtis and de Solan, Benoit and Hund, Andreas and Chapman, Scott C. and Baret, Frédéric and Stavness, Ian and Guo, Wei},
  year={2021},
  url={https://zenodo.org/records/5092309}
}
```

## Changelog

- **V1.0.0** (2025): Initial standardized structure and COCO conversion utility

## Contact

**Maintainers**: Dataset maintainers

**Original authors**: Global Wheat Head Detection 2021 challenge organizers and participants

**Source**: `https://zenodo.org/records/5092309`
