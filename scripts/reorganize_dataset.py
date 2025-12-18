#!/usr/bin/env python3
"""
Reorganize wheat_head_counting dataset to standard structure.
This script:
1. Creates CSV annotation files for each image from competition_*.csv
2. Moves images to wheat_heads/images/
3. Moves JSON files to wheat_heads/json/
4. Creates sets/*.txt files from competition_*.csv
"""

import csv
import os
import shutil
from pathlib import Path

def parse_boxes_string(boxes_string):
    """Parse boxes string format: 'x1 y1 x2 y2;x1 y1 x2 y2;...' to CSV format"""
    if not boxes_string or boxes_string == '':
        return []
    
    boxes = []
    box_strings = str(boxes_string).split(';')
    
    for item_id, box_str in enumerate(box_strings):
        if box_str.strip():
            try:
                coords = [float(x) for x in box_str.strip().split()]
                if len(coords) == 4:
                    x1, y1, x2, y2 = coords
                    # Convert to COCO format: [x, y, width, height]
                    x = x1
                    y = y1
                    width = x2 - x1
                    height = y2 - y1
                    boxes.append({
                        'item': item_id,
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'label': 1
                    })
            except (ValueError, IndexError) as e:
                print(f"Warning: Failed to parse box '{box_str}': {e}")
                continue
    
    return boxes

def create_csv_annotation(image_name, boxes_data, output_dir):
    """Create CSV annotation file for an image"""
    csv_path = output_dir / f"{Path(image_name).stem}.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['#item', 'x', 'y', 'width', 'height', 'label'])
        
        for box in boxes_data:
            writer.writerow([
                box['item'],
                box['x'],
                box['y'],
                box['width'],
                box['height'],
                box['label']
            ])
    
    return csv_path

def read_csv_data(filename):
    """Read CSV file and return dictionary mapping image_name to boxes_string"""
    data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'image_name' in row and 'BoxesString' in row:
                    image_name = row['image_name']
                    boxes_string = row['BoxesString']
                    data[image_name] = boxes_string
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return data

def main():
    root_dir = Path(__file__).parent.parent
    images_dir = root_dir / 'images'
    wheat_heads_dir = root_dir / 'wheat_heads'
    csv_dir = wheat_heads_dir / 'csv'
    json_dir = wheat_heads_dir / 'json'
    images_output_dir = wheat_heads_dir / 'images'
    sets_dir = wheat_heads_dir / 'sets'
    
    # Read CSV files
    train_data = read_csv_data(root_dir / 'competition_train.csv')
    val_data = read_csv_data(root_dir / 'competition_val.csv')
    test_data = read_csv_data(root_dir / 'competition_test.csv')
    
    # Create sets files
    train_images = set(train_data.keys())
    val_images = set(val_data.keys())
    test_images = set(test_data.keys())
    all_images = train_images | val_images | test_images
    
    # Write sets files (without extension)
    with open(sets_dir / 'train.txt', 'w', encoding='utf-8') as f:
        for img_name in sorted(train_images):
            f.write(f"{Path(img_name).stem}\n")
    
    with open(sets_dir / 'val.txt', 'w', encoding='utf-8') as f:
        for img_name in sorted(val_images):
            f.write(f"{Path(img_name).stem}\n")
    
    with open(sets_dir / 'test.txt', 'w', encoding='utf-8') as f:
        for img_name in sorted(test_images):
            f.write(f"{Path(img_name).stem}\n")
    
    with open(sets_dir / 'all.txt', 'w', encoding='utf-8') as f:
        for img_name in sorted(all_images):
            f.write(f"{Path(img_name).stem}\n")
    
    with open(sets_dir / 'train_val.txt', 'w', encoding='utf-8') as f:
        train_val_images = train_images | val_images
        for img_name in sorted(train_val_images):
            f.write(f"{Path(img_name).stem}\n")
    
    print(f"Created sets files: train={len(train_images)}, val={len(val_images)}, test={len(test_images)}, all={len(all_images)}")
    
    # Combine all data
    all_data = {**train_data, **val_data, **test_data}
    
    # Process each image
    processed = 0
    skipped = 0
    
    for image_name, boxes_string in all_data.items():
        image_stem = Path(image_name).stem
        source_image_path = images_dir / image_name
        source_json_path = images_dir / f"{image_stem}.json"
        
        # Check if image exists
        if not source_image_path.exists():
            print(f"Warning: Image not found: {source_image_path}")
            skipped += 1
            continue
        
        # Move image
        dest_image_path = images_output_dir / image_name
        if not dest_image_path.exists():
            shutil.copy2(source_image_path, dest_image_path)
        
        # Move JSON if exists
        if source_json_path.exists():
            dest_json_path = json_dir / f"{image_stem}.json"
            if not dest_json_path.exists():
                shutil.copy2(source_json_path, dest_json_path)
        
        # Create CSV annotation
        boxes_data = parse_boxes_string(boxes_string)
        create_csv_annotation(image_name, boxes_data, csv_dir)
        
        processed += 1
        
        if processed % 100 == 0:
            print(f"Processed {processed} images...")
    
    print(f"\nDone! Processed {processed} images, skipped {skipped} images")
    print(f"CSV files: {csv_dir}")
    print(f"JSON files: {json_dir}")
    print(f"Images: {images_output_dir}")
    print(f"Sets: {sets_dir}")

if __name__ == "__main__":
    main()





