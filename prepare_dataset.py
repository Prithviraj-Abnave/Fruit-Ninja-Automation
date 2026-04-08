import os
import shutil
import random
from pathlib import Path

# Paths
source_images = Path("data/train/images/images")
source_labels = Path("data/train/labels")
target_root = Path("dataset")

# Create structure
for split in ["train", "val", "test"]:
    (target_root / split / "images").mkdir(parents=True, exist_ok=True)
    (target_root / split / "labels").mkdir(parents=True, exist_ok=True)

# Get all base names (stem) from images
all_images = [f for f in source_images.glob("*.jpg")]
image_stems = {f.stem for f in all_images}

# Filter labels that exist for these images
all_labels = {f.stem: f for f in source_labels.glob("*.txt")}
matching_stems = [stem for stem in image_stems if stem in all_labels]

print(f"Found {len(all_images)} images and {len(all_labels)} labels.")
print(f"Matching pairs: {len(matching_stems)}")

# Shuffle and split
random.seed(42)
random.shuffle(matching_stems)

total = len(matching_stems)
train_end = int(total * 0.8)
val_end = int(total * 0.9)

train_stems = matching_stems[:train_end]
val_stems = matching_stems[train_end:val_end]
test_stems = matching_stems[val_end:]

def copy_files(stems, split):
    for stem in stems:
        # Copy image
        shutil.copy(source_images / f"{stem}.jpg", target_root / split / "images" / f"{stem}.jpg")
        # Copy label
        shutil.copy(source_labels / f"{stem}.txt", target_root / split / "labels" / f"{stem}.txt")

print(f"Copying {len(train_stems)} files to train...")
copy_files(train_stems, "train")
print(f"Copying {len(val_stems)} files to val...")
copy_files(val_stems, "val")
print(f"Copying {len(test_stems)} files to test...")
copy_files(test_stems, "test")

print("Dataset preparation complete.")
