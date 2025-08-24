import subprocess
import os
import shutil
import numpy as np
from PIL import Image
import hashlib
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class DungeonHunterImageComparator:
    def __init__(self, classpath="bin", java_path=None, results_dir="q1"):
        self.classpath = classpath
        self.java_path = java_path or "java"
        self.serial_class = "DungeonHunter"
        self.parallel_class = "DungeonHunterParallel"
        self.results_dir = results_dir
        self.comparison_results = []

        # Create results directory structure
        os.makedirs(self.results_dir, exist_ok=True)
        self.images_dir = os.path.join(self.results_dir, "images")
        self.diff_dir = os.path.join(self.results_dir, "differences")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.diff_dir, exist_ok=True)

    def run_and_capture_images(self, class_name, grid_size, num_searches_factor, random_seed, run_id):
        """Run program and capture generated images"""
        args = [str(grid_size), str(num_searches_factor), str(random_seed)]

        try:
            # Clean up any existing images
            for img_file in ["visualiseSearch.png", "visualiseSearchPath.png"]:
                if os.path.exists(img_file):
                    os.remove(img_file)

            # Run the program
            result = subprocess.run(
                [self.java_path, "-cp", self.classpath, class_name] + args,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(f"Error running {class_name}: {result.stderr}")
                return None, None

            # Capture generated images
            search_img = None
            path_img = None

            if os.path.exists("visualiseSearch.png"):
                search_dest = os.path.join(self.images_dir, f"{class_name}_{run_id}_search.png")
                shutil.copy2("visualiseSearch.png", search_dest)
                search_img = search_dest
                os.remove("visualiseSearch.png")

            if os.path.exists("visualiseSearchPath.png"):
                path_dest = os.path.join(self.images_dir, f"{class_name}_{run_id}_path.png")
                shutil.copy2("visualiseSearchPath.png", path_dest)
                path_img = path_dest
                os.remove("visualiseSearchPath.png")

            return search_img, path_img

        except Exception as e:
            print(f"Exception running {class_name}: {e}")
            return None, None

    def calculate_image_hash(self, image_path):
        """Calculate MD5 hash of image file"""
        if not image_path or not os.path.exists(image_path):
            return None

        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def calculate_pixel_difference(self, img1_path, img2_path):
        """Calculate pixel-wise differences between two images"""
        if not img1_path or not img2_path or not os.path.exists(img1_path) or not os.path.exists(img2_path):
            return None, None, None

        try:
            # Load images
            img1 = Image.open(img1_path).convert('RGB')
            img2 = Image.open(img2_path).convert('RGB')

            # Check if dimensions match
            if img1.size != img2.size:
                return None, f"Size mismatch: {img1.size} vs {img2.size}", None

            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)

            # Calculate differences
            diff = np.abs(arr1.astype(float) - arr2.astype(float))

            # Calculate statistics
            total_pixels = arr1.shape[0] * arr1.shape[1]
            different_pixels = np.sum(np.any(diff > 0, axis=2))
            max_diff = np.max(diff)
            avg_diff = np.mean(diff)

            diff_stats = {
                'total_pixels': total_pixels,
                'different_pixels': int(different_pixels),
                'percent_different': (different_pixels / total_pixels) * 100,
                'max_difference': float(max_diff),
                'avg_difference': float(avg_diff),
                'identical': different_pixels == 0
            }

            return diff_stats, None, diff

        except Exception as e:
            return None, f"Error comparing images: {e}", None

    def create_difference_visualization(self, img1_path, img2_path, diff_array, output_path):
        """Create a visualization showing differences between images"""
        if diff_array is None or img1_path is None or img2_path is None:
            return

        try:
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)

            fig, axes = plt.subplots(1, 3, figsize=(15, 5))

            # Original images
            axes[0].imshow(img1)
            axes[0].set_title('Serial Version')
            axes[0].axis('off')

            axes[1].imshow(img2)
            axes[1].set_title('Parallel Version')
            axes[1].axis('off')

            # Difference visualization
            diff_vis = np.sum(diff_array, axis=2)  # Sum across RGB channels
            im = axes[2].imshow(diff_vis, cmap='hot', vmin=0, vmax=255)
            axes[2].set_title('Differences (Red = Different)')
            axes[2].axis('off')

            plt.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"Error creating difference visualization: {e}")

    def compare_test_case(self, grid_size, num_searches_factor, random_seed):
        """Compare images for a single test case"""
        run_id = f"g{grid_size}_f{num_searches_factor}_s{random_seed}"

        print(f"Comparing: Grid={grid_size}, Factor={num_searches_factor}, Seed={random_seed}")

        # Run serial version
        serial_search, serial_path = self.run_and_capture_images(
            self.serial_class, grid_size, num_searches_factor, random_seed, f"serial_{run_id}"
        )

        # Run parallel version
        parallel_search, parallel_path = self.run_and_capture_images(
            self.parallel_class, grid_size, num_searches_factor, random_seed, f"parallel_{run_id}"
        )

        # Compare search visualization images
        search_comparison = {
            'test_case': run_id,
            'grid_size': grid_size,
            'num_searches_factor': num_searches_factor,
            'random_seed': random_seed,
            'image_type': 'search',
            'serial_image': serial_search,
            'parallel_image': parallel_search,
            'serial_hash': self.calculate_image_hash(serial_search),
            'parallel_hash': self.calculate_image_hash(parallel_search),
            'hash_match': False,
            'pixel_stats': None,
            'error': None
        }

        if search_comparison['serial_hash'] and search_comparison['parallel_hash']:
            search_comparison['hash_match'] = (search_comparison['serial_hash'] == search_comparison['parallel_hash'])

            if not search_comparison['hash_match']:
                pixel_stats, error, diff_array = self.calculate_pixel_difference(serial_search, parallel_search)
                search_comparison['pixel_stats'] = pixel_stats
                search_comparison['error'] = error

                # Create difference visualization
                if diff_array is not None:
                    diff_output = os.path.join(self.diff_dir, f"diff_{run_id}_search.png")
                    self.create_difference_visualization(serial_search, parallel_search, diff_array, diff_output)
                    search_comparison['diff_visualization'] = diff_output

        # Compare path visualization images
        path_comparison = {
            'test_case': run_id,
            'grid_size': grid_size,
            'num_searches_factor': num_searches_factor,
            'random_seed': random_seed,
            'image_type': 'path',
            'serial_image': serial_path,
            'parallel_image': parallel_path,
            'serial_hash': self.calculate_image_hash(serial_path),
            'parallel_hash': self.calculate_image_hash(parallel_path),
            'hash_match': False,
            'pixel_stats': None,
            'error': None
        }

        if path_comparison['serial_hash'] and path_comparison['parallel_hash']:
            path_comparison['hash_match'] = (path_comparison['serial_hash'] == path_comparison['parallel_hash'])

            if not path_comparison['hash_match']:
                pixel_stats, error, diff_array = self.calculate_pixel_difference(serial_path, parallel_path)
                path_comparison['pixel_stats'] = pixel_stats
                path_comparison['error'] = error

                # Create difference visualization
                if diff_array is not None:
                    diff_output = os.path.join(self.diff_dir, f"diff_{run_id}_path.png")
                    self.create_difference_visualization(serial_path, parallel_path, diff_array, diff_output)
                    path_comparison['diff_visualization'] = diff_output

        self.comparison_results.extend([search_comparison, path_comparison])

        # Print results
        print(f"  Search image: {'✓ IDENTICAL' if search_comparison['hash_match'] else '✗ DIFFERENT'}")
        if not search_comparison['hash_match'] and search_comparison['pixel_stats']:
            stats = search_comparison['pixel_stats']
            print(f"    {stats['different_pixels']}/{stats['total_pixels']} pixels different ({stats['percent_different']:.2f}%)")

        print(f"  Path image:   {'✓ IDENTICAL' if path_comparison['hash_match'] else '✗ DIFFERENT'}")
        if not path_comparison['hash_match'] and path_comparison['pixel_stats']:
            stats = path_comparison['pixel_stats']
            print(f"    {stats['different_pixels']}/{stats['total_pixels']} pixels different ({stats['percent_different']:.2f}%)")

        print()

        return search_comparison, path_comparison

    def save_results_to_csv(self, filename=None):
        """Save comparison results to CSV"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.results_dir, f"image_comparison_results_{timestamp}.csv")

        if not self.comparison_results:
            print("No comparison results to save!")
            return None

        print(f"Saving comparison results to {filename}")

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'test_case', 'grid_size', 'num_searches_factor', 'random_seed', 'image_type',
                'serial_image', 'parallel_image', 'serial_hash', 'parallel_hash', 'hash_match',
                'total_pixels', 'different_pixels', 'percent_different', 'max_difference', 'avg_difference',
                'error', 'diff_visualization'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.comparison_results:
                row = {
                    'test_case': result['test_case'],
                    'grid_size': result['grid_size'],
                    'num_searches_factor': result['num_searches_factor'],
                    'random_seed': result['random_seed'],
                    'image_type': result['image_type'],
                    'serial_image': result['serial_image'],
                    'parallel_image': result['parallel_image'],
                    'serial_hash': result['serial_hash'],
                    'parallel_hash': result['parallel_hash'],
                    'hash_match': result['hash_match'],
                    'error': result['error'],
                    'diff_visualization': result.get('diff_visualization', '')
                }

                if result['pixel_stats']:
                    stats = result['pixel_stats']
                    row.update({
                        'total_pixels': stats['total_pixels'],
                        'different_pixels': stats['different_pixels'],
                        'percent_different': round(stats['percent_different'], 4),
                        'max_difference': round(stats['max_difference'], 2),
                        'avg_difference': round(stats['avg_difference'], 4)
                    })

                writer.writerow(row)

        return filename

    def run_comparison(self):
        """Run the complete image comparison analysis"""
        print("DUNGEON HUNTER IMAGE COMPARATOR")
        print("=" * 50)
        print(f"Results will be saved to: {self.results_dir}")
        print(f"Images will be stored in: {self.images_dir}")
        print(f"Difference visualizations in: {self.diff_dir}")
        print()

        # Test configuration - smaller set for image comparison
        grid_sizes =  [10, 25, 40, 50, 75, 90, 100, 115, 135, 150, 185, 200, 225, 275, 315]
        num_searches_factors = [0.1, 0.4]
        random_seeds = [3, 60]

        total_tests = len(grid_sizes) * len(num_searches_factors) * len(random_seeds)
        print(f"Running {total_tests} image comparison tests...")
        print(f"Configuration:")
        print(f"- Grid sizes: {grid_sizes}")
        print(f"- Search factors: {num_searches_factors}")
        print(f"- Random seeds: {random_seeds}")
        print()

        test_count = 0

        for grid_size in grid_sizes:
            for num_searches_factor in num_searches_factors:
                for random_seed in random_seeds:
                    test_count += 1
                    print(f"Test {test_count}/{total_tests}:")
                    self.compare_test_case(grid_size, num_searches_factor, random_seed)

        # Save results
        csv_filename = self.save_results_to_csv()

        # Print summary
        total_comparisons = len(self.comparison_results)
        identical_count = sum(1 for r in self.comparison_results if r['hash_match'])
        different_count = total_comparisons - identical_count

        search_images = [r for r in self.comparison_results if r['image_type'] == 'search']
        path_images = [r for r in self.comparison_results if r['image_type'] == 'path']

        search_identical = sum(1 for r in search_images if r['hash_match'])
        path_identical = sum(1 for r in path_images if r['hash_match'])

        print("=" * 50)
        print("COMPARISON SUMMARY")
        print("=" * 50)
        print(f"Total image comparisons: {total_comparisons}")
        print(f"Identical images: {identical_count}")
        print(f"Different images: {different_count}")
        print()
        print(f"Search visualizations:")
        print(f"  Identical: {search_identical}/{len(search_images)}")
        print(f"  Different: {len(search_images) - search_identical}/{len(search_images)}")
        print()
        print(f"Path visualizations:")
        print(f"  Identical: {path_identical}/{len(path_images)}")
        print(f"  Different: {len(path_images) - path_identical}/{len(path_images)}")

        if different_count > 0:
            print(f"\n⚠️  Found {different_count} image differences!")
            print(f"   Check difference visualizations in: {self.diff_dir}")
            print(f"   Original images stored in: {self.images_dir}")
            print(f"   Detailed results saved to: {csv_filename}")
        else:
            print(f"\n✅ All images are identical!")
            print(f"   Original images stored in: {self.images_dir}")
            print(f"   Results saved to: {csv_filename}")

        return csv_filename

    def cleanup(self):
        """Clean up results directory"""
        if os.path.exists(self.results_dir):
            shutil.rmtree(self.results_dir)
            print(f"Cleaned up results directory: {self.results_dir}")

# Usage
if __name__ == "__main__":
    import sys

    # Create comparator instance - saves everything to q1 folder
    comparator = DungeonHunterImageComparator(classpath="bin")

    try:
        # Run the comparison
        csv_file = comparator.run_comparison()

        if csv_file:
            print(f"\nImage comparison complete!")
            print(f"All results saved in folder: {comparator.results_dir}")
            print(f"- CSV report: {csv_file}")
            print(f"- Original images: {comparator.images_dir}")
            print(f"- Difference visualizations: {comparator.diff_dir}")

            # Ask if user wants to clean up files
            if "--cleanup" in sys.argv:
                comparator.cleanup()
            else:
                print(f"\nTo clean up all files, run with --cleanup flag")

    except KeyboardInterrupt:
        print("\nComparison interrupted by user")
    except Exception as e:
        print(f"Error during comparison: {e}")