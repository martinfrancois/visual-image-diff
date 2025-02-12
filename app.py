import cv2
import os
import argparse

def compare_images(image_path1, image_path2, diff_path, threshold_value=30):
    """
    Compare two images and save a binary diff image that only shows differences.

    The output image has a white background and black pixels where the images differ.
    The diff image is only saved if there are actual differences.

    Args:
        image_path1 (str): Path to the first image.
        image_path2 (str): Path to the second image.
        diff_path (str): Path to save the diff image.
        threshold_value (int): Difference threshold. Pixel differences greater than this value
                               are considered significant.
    """
    # Load the images
    imgA = cv2.imread(image_path1)
    imgB = cv2.imread(image_path2)

    if imgA is None:
        print(f"Error loading image: {image_path1}")
        return
    if imgB is None:
        print(f"Error loading image: {image_path2}")
        return

    # Check if dimensions match; if not, skip this pair.
    if imgA.shape != imgB.shape:
        print(f"Skipping {image_path1} and {image_path2} due to different dimensions.")
        return

    # Compute the absolute difference between the two images
    diff = cv2.absdiff(imgA, imgB)

    # Convert the difference image to grayscale
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Apply an inverted binary threshold:
    # - Pixels with differences above the threshold become 0 (black)
    # - Others become 255 (white)
    _, diff_mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # Optionally, apply a morphological opening to reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    diff_mask = cv2.morphologyEx(diff_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Check if the diff image contains any differences (i.e., not completely white)
    total_pixels = diff_mask.shape[0] * diff_mask.shape[1]
    if cv2.countNonZero(diff_mask) == total_pixels:
        print(f"No differences found in {os.path.basename(image_path1)}; skipping diff image.")
        return

    # Save the resulting diff image
    cv2.imwrite(diff_path, diff_mask)
    print(f"Diff saved to {diff_path}")

def process_folders(folder1, folder2, output_folder, threshold_value=30):
    """
    Iterate over common image files in two folders and generate diff images if differences exist.

    Args:
        folder1 (str): Path to the first image folder.
        folder2 (str): Path to the second image folder.
        output_folder (str): Folder to save diff images.
        threshold_value (int): Difference threshold for diff image generation.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List files in both folders and determine common files based on filename.
    files1 = set(os.listdir(folder1))
    files2 = set(os.listdir(folder2))
    common_files = files1.intersection(files2)

    # Define common image file extensions.
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
    common_images = [f for f in common_files if os.path.splitext(f)[1].lower() in image_extensions]

    if not common_images:
        print("No common image files found between folders.")
        return

    # Compare each pair of common images.
    for image_name in common_images:
        image_path1 = os.path.join(folder1, image_name)
        image_path2 = os.path.join(folder2, image_name)
        diff_path = os.path.join(output_folder, f"diff_{image_name}")
        compare_images(image_path1, image_path2, diff_path, threshold_value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare two image folders and generate binary diff images. "
                    "The diff image has a white background with differences in black. "
                    "Only images with differences are saved."
    )
    parser.add_argument("folder1", help="Path to the first image folder")
    parser.add_argument("folder2", help="Path to the second image folder")
    parser.add_argument("output_folder", help="Folder to save the diff images")
    parser.add_argument("--threshold", type=int, default=30, help="Threshold for difference detection (default: 30)")
    args = parser.parse_args()

    process_folders(args.folder1, args.folder2, args.output_folder, args.threshold)
