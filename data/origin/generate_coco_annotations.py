import csv
import json
import os
import random
import time
from PIL import Image
import glob

def generate_unique_id():
    """Generate unique ID: 7 random digits + 3 timestamp digits"""
    random_part = random.randint(1000000, 9999999)
    timestamp_part = int(time.time()) % 1000
    return int(f"{random_part}{timestamp_part:03d}")

def parse_boxes_string(boxes_string):
    """Parse boxes string format: 'x1 y1 x2 y2;x1 y1 x2 y2;...'"""
    if not boxes_string or boxes_string == '':
        return []
    
    boxes = []
    box_strings = str(boxes_string).split(';')
    
    for box_str in box_strings:
        if box_str.strip():
            try:
                coords = [int(x) for x in box_str.strip().split()]
                if len(coords) == 4:
                    x1, y1, x2, y2 = coords
                    # Convert to COCO format: [x, y, width, height]
                    bbox = [x1, y1, x2 - x1, y2 - y1]
                    area = (x2 - x1) * (y2 - y1)
                    boxes.append({
                        'bbox': bbox,
                        'area': area
                    })
            except (ValueError, IndexError):
                continue
    
    return boxes

def create_coco_annotation(image_path, image_name, boxes_data, image_id, annotation_id):
    """Create COCO format annotation for a single image"""
    
    # Get image dimensions
    try:
        with Image.open(image_path) as img:
            width, height = img.size
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        width, height = 512, 512  # Default size
    
    # Create COCO format
    coco_data = {
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
                "id": image_id,
                "width": width,
                "height": height,
                "file_name": image_name,
                "size": os.path.getsize(image_path),
                "format": "PNG",
                "url": "",
                "hash": "",
                "status": "success"
            }
        ],
        "annotations": [],
        "categories": [
            {
                "id": 1,
                "name": "wheat_head",
                "supercategory": "broccoli"
            }
        ]
    }
    
    # Add annotations for each box
    for i, box_data in enumerate(boxes_data):
        annotation = {
            "id": annotation_id + i,
            "image_id": image_id,
            "category_id": 1,
            "segmentation": [],
            "area": box_data['area'],
            "bbox": box_data['bbox']
        }
        coco_data["annotations"].append(annotation)
    
    return coco_data

def read_csv_data(filename):
    """Read CSV file and return dictionary mapping image_name to boxes_string"""
    data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'image_name' in row and 'BoxesString' in row:
                    data[row['image_name']] = row['BoxesString']
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return data

def main():
    # Read CSV files
    train_data = read_csv_data('competition_train.csv')
    val_data = read_csv_data('competition_val.csv')
    test_data = read_csv_data('competition_test.csv')
    
    # Combine all data
    all_data = {**train_data, **val_data, **test_data}
    
    # Get all image files
    image_files = glob.glob('images/*.png')
    image_names = [os.path.basename(f) for f in image_files]
    
    print(f"Found {len(image_files)} images")
    print(f"Found {len(all_data)} annotations")
    
    # Process each image
    for image_file in image_files:
        image_name = os.path.basename(image_file)
        
        # Find corresponding annotation data
        boxes_string = all_data.get(image_name)
        
        if boxes_string is None:
            print(f"No annotation found for {image_name}")
            continue
        
        # Parse boxes string
        boxes_data = parse_boxes_string(boxes_string)
        
        # Generate unique IDs
        image_id = generate_unique_id()
        annotation_id = generate_unique_id()
        
        # Create COCO annotation
        coco_data = create_coco_annotation(
            image_file, 
            image_name, 
            boxes_data, 
            image_id, 
            annotation_id
        )
        
        # Save JSON file in the same directory as the image
        json_filename = os.path.splitext(image_name)[0] + '.json'
        json_path = os.path.join(os.path.dirname(image_file), json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, indent=2, ensure_ascii=False)
        
        print(f"Generated {json_path} with {len(boxes_data)} annotations")

if __name__ == "__main__":
    main() 