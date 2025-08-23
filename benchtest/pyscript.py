import subprocess
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from datetime import datetime
import csv
import statistics
import shutil
import re

class DungeonHunterProfiler:
    def __init__(self, classpath="bin", src_path="src", package_name=None, java_path=None):
        self.classpath = classpath
        self.src_path = src_path
        self.package_name = package_name
        self.java_path = java_path or "java"  # Allow custom Java path

        # If no package, use simple class names
        if package_name:
            self.serial_class = f"{package_name}.DungeonHunter"
            self.parallel_class = f"{package_name}.DungeonHunterParallel"
        else:
            self.serial_class = "DungeonHunter"
            self.parallel_class = "DungeonHunterParallel"

    def check_java_versions(self):
        """Check Java compiler and runtime versions"""
        print("Checking Java environment...")

        # Check javac version
        try:
            javac_result = subprocess.run(["javac", "-version"], capture_output=True, text=True)
            print(f"Java Compiler: {javac_result.stderr.strip()}")
        except:
            print("javac not found or not accessible")

        # Check java version
        try:
            java_result = subprocess.run([self.java_path, "-version"], capture_output=True, text=True)
            print(f"Java Runtime: {java_result.stderr.strip().split(chr(10))[0]}")
        except:
            print(f"Java runtime ({self.java_path}) not found or not accessible")

        print()

        # Create results directory
        self.results_dir = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)

        # Create images subdirectory for test images
        self.images_dir = os.path.join(self.results_dir, "test_images")
        os.makedirs(self.images_dir, exist_ok=True)

        # Results storage
        self.serial_results = []
        self.parallel_results = []

    def recompile_sources(self):
        """Attempt to recompile Java sources"""
        if not os.path.exists(self.src_path):
            print(f"Source directory {self.src_path} not found")
            return False

        # Find all Java files in src directory
        java_files = []
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))

        if not java_files:
            print(f"No Java files found in {self.src_path}")
            return False

        # Create bin directory if it doesn't exist
        os.makedirs(self.classpath, exist_ok=True)

        # Compile all Java files
        try:
            cmd = ["javac", "-d", self.classpath] + java_files
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("Compilation successful")
                return True
            else:
                print(f"Compilation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"Compilation exception: {e}")
            return False

    def run_program(self, class_name, grid_size, num_searches_factor, random_seed, runs=3):
        """Run a program multiple times and return average timing and validation data"""
        times = []
        outputs = []

        args = [str(grid_size), str(num_searches_factor), str(random_seed)]

        for run in range(runs):
            start_time = time.time()

            try:
                result = subprocess.run(
                    [self.java_path, "-cp", self.classpath, class_name] + args,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                end_time = time.time()

                if result.returncode != 0:
                    print(f"Error running {class_name} with args {args}:")
                    print(f"STDERR: {result.stderr}")
                    return None

                # Parse execution time from output
                program_time = self.extract_execution_time(result.stdout)
                if program_time is None:
                    program_time = (end_time - start_time) * 1000  # fallback to wall clock time

                times.append(program_time)
                outputs.append({
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'wall_clock_time': (end_time - start_time) * 1000,
                    'program_time': program_time
                })

                # Move generated images to our test images directory
                self.move_generated_images(class_name, grid_size, num_searches_factor, random_seed, run)

            except subprocess.TimeoutExpired:
                print(f"Timeout for {class_name} with grid size {grid_size}")
                return None
            except Exception as e:
                print(f"Exception running {class_name}: {e}")
                return None

        avg_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0

        return {
            'avg_time': avg_time,
            'std_time': std_time,
            'times': times,
            'outputs': outputs
        }

    def move_generated_images(self, class_name, grid_size, num_searches_factor, random_seed, run):
        """Move generated visualization images to our test images directory"""
        # Look for generated images in current directory
        image_files = ["visualiseSearch.png", "visualiseSearchPath.png"]

        for img_file in image_files:
            if os.path.exists(img_file):
                # Create descriptive filename
                class_type = "serial" if "Serial" in class_name else "parallel"
                new_filename = f"{class_type}_grid{grid_size}_factor{num_searches_factor}_seed{random_seed}_run{run}_{img_file}"
                dest_path = os.path.join(self.images_dir, new_filename)

                try:
                    shutil.move(img_file, dest_path)
                    print(f"  Moved {img_file} to {dest_path}")
                except Exception as e:
                    print(f"  Warning: Could not move {img_file}: {e}")

    def extract_execution_time(self, output):
        """Extract execution time from program output"""
        for line in output.split('\n'):
            if 'time:' in line and 'ms' in line:
                try:
                    # Extract number from line like "time: 123 ms"
                    time_str = line.split('time:')[1].split('ms')[0].strip()
                    return float(time_str)
                except:
                    continue
        return None

    def extract_solution_info(self, output):
        """Extract solution information for validation"""
        info = {}
        print(f"DEBUG: Parsing output:\n{output}")  # Debug print

        for line in output.split('\n'):
            print(f"DEBUG: Processing line: '{line.strip()}'")  # Debug print

            if 'Dungeon Master (mana' in line:
                try:
                    # Extract mana value
                    mana_str = line.split('mana ')[1].split(')')[0]
                    info['mana'] = int(mana_str)
                    print(f"DEBUG: Found mana: {info['mana']}")
                except Exception as e:
                    print(f"DEBUG: Error parsing mana from '{line}': {e}")

            # Look for coordinates in the same line as "Dungeon Master" or the line after
            if 'x=' in line and 'y=' in line:
                try:
                    print(f"DEBUG: Found coordinate line: '{line}'")
                    # Try multiple parsing strategies

                    # Strategy 1: Look for x=value y=value pattern
                    x_match = re.search(r'x=([+-]?\d*\.?\d+)', line)
                    y_match = re.search(r'y=([+-]?\d*\.?\d+)', line)

                    if x_match and y_match:
                        info['x'] = float(x_match.group(1))
                        info['y'] = float(y_match.group(1))
                        print(f"DEBUG: Found coordinates: x={info['x']}, y={info['y']}")
                    else:
                        print(f"DEBUG: Could not match x= and y= patterns in '{line}'")

                except Exception as e:
                    print(f"DEBUG: Error parsing coordinates from '{line}': {e}")

            elif 'number dungeon grid points evaluated:' in line:
                try:
                    # Extract grid points evaluated
                    match = re.search(r'number dungeon grid points evaluated:\s*(\d+)', line)
                    if match:
                        info['grid_points_evaluated'] = int(match.group(1))
                        print(f"DEBUG: Found grid points: {info['grid_points_evaluated']}")
                except Exception as e:
                    print(f"DEBUG: Error parsing grid points from '{line}': {e}")

        print(f"DEBUG: Final extracted info: {info}")
        return info

    def profile_serial(self, grid_sizes, num_searches_factors, random_seeds, runs=3):
        """Profile the serial version"""
        print("Profiling Serial Version...")
        print("-" * 50)

        for grid_size in grid_sizes:
            for num_searches_factor in num_searches_factors:
                for random_seed in random_seeds:
                    print(f"Testing: grid_size={grid_size}, searches_factor={num_searches_factor}, seed={random_seed}")

                    result = self.run_program(
                        self.serial_class, grid_size, num_searches_factor, random_seed, runs
                    )

                    if result:
                        solution_info = self.extract_solution_info(result['outputs'][0]['stdout'])

                        self.serial_results.append({
                            'grid_size': grid_size,
                            'num_searches_factor': num_searches_factor,
                            'random_seed': random_seed,
                            'avg_time': result['avg_time'],
                            'std_time': result['std_time'],
                            'times': result['times'],
                            'solution_info': solution_info,
                            'output': result['outputs'][0]['stdout']
                        })

                        print(f"  Avg time: {result['avg_time']:.2f} ± {result['std_time']:.2f} ms")
                        x_coord = solution_info.get('x', 'N/A')
                        y_coord = solution_info.get('y', 'N/A')
                        x_str = f"{x_coord:.1f}" if isinstance(x_coord, (int, float)) else str(x_coord)
                        y_str = f"{y_coord:.1f}" if isinstance(y_coord, (int, float)) else str(y_coord)
                        print(f"  Solution: Mana={solution_info.get('mana', 'N/A')}, "
                              f"Location=({x_str}, {y_str}), "
                              f"Grid Points={solution_info.get('grid_points_evaluated', 'N/A')}")
                    else:
                        print(f"  Failed to run")
                    print()

    def profile_parallel(self, grid_sizes, num_searches_factors, random_seeds, runs=3):
        """Profile the parallel version"""
        print("Profiling Parallel Version...")
        print("-" * 50)

        for grid_size in grid_sizes:
            for num_searches_factor in num_searches_factors:
                for random_seed in random_seeds:
                    print(f"Testing: grid_size={grid_size}, searches_factor={num_searches_factor}, seed={random_seed}")

                    result = self.run_program(
                        self.parallel_class, grid_size, num_searches_factor, random_seed, runs
                    )

                    if result:
                        solution_info = self.extract_solution_info(result['outputs'][0]['stdout'])

                        self.parallel_results.append({
                            'grid_size': grid_size,
                            'num_searches_factor': num_searches_factor,
                            'random_seed': random_seed,
                            'avg_time': result['avg_time'],
                            'std_time': result['std_time'],
                            'times': result['times'],
                            'solution_info': solution_info,
                            'output': result['outputs'][0]['stdout']
                        })

                        print(f"  Avg time: {result['avg_time']:.2f} ± {result['std_time']:.2f} ms")
                        x_coord = solution_info.get('x', 'N/A')
                        y_coord = solution_info.get('y', 'N/A')
                        x_str = f"{x_coord:.1f}" if isinstance(x_coord, (int, float)) else str(x_coord)
                        y_str = f"{y_coord:.1f}" if isinstance(y_coord, (int, float)) else str(y_coord)
                        print(f"  Solution: Mana={solution_info.get('mana', 'N/A')}, "
                              f"Location=({x_str}, {y_str}), "
                              f"Grid Points={solution_info.get('grid_points_evaluated', 'N/A')}")
                    else:
                        print(f"  Failed to run")
                    print()

    def validate_solutions(self):
        """Validate that parallel and serial versions produce same results"""
        print("Validating Solutions...")
        print("-" * 50)

        validation_errors = 0

        for serial_result in self.serial_results:
            # Find corresponding parallel result
            parallel_result = None
            for p_result in self.parallel_results:
                if (p_result['grid_size'] == serial_result['grid_size'] and
                        p_result['num_searches_factor'] == serial_result['num_searches_factor'] and
                        p_result['random_seed'] == serial_result['random_seed']):
                    parallel_result = p_result
                    break

            if parallel_result is None:
                print(f"No parallel result found for serial test case: {serial_result['grid_size']}, {serial_result['num_searches_factor']}, {serial_result['random_seed']}")
                validation_errors += 1
                continue

            serial_solution = serial_result['solution_info']
            parallel_solution = parallel_result['solution_info']

            # Check if solutions match (allowing for small floating point differences)
            solutions_match = True
            mismatch_details = []

            if 'mana' in serial_solution and 'mana' in parallel_solution:
                if serial_solution['mana'] != parallel_solution['mana']:
                    solutions_match = False
                    mismatch_details.append(f"Mana: {serial_solution['mana']} vs {parallel_solution['mana']}")

            if ('x' in serial_solution and 'x' in parallel_solution and
                    'y' in serial_solution and 'y' in parallel_solution):
                if (abs(serial_solution['x'] - parallel_solution['x']) > 0.1 or
                        abs(serial_solution['y'] - parallel_solution['y']) > 0.1):
                    solutions_match = False
                    mismatch_details.append(f"Location: ({serial_solution['x']:.1f},{serial_solution['y']:.1f}) vs ({parallel_solution['x']:.1f},{parallel_solution['y']:.1f})")

            if solutions_match:
                print(f"✓ PASS: Grid {serial_result['grid_size']}, Factor {serial_result['num_searches_factor']}, Seed {serial_result['random_seed']}")
                x_coord = serial_solution.get('x', 'N/A')
                y_coord = serial_solution.get('y', 'N/A')
                x_str = f"{x_coord:.1f}" if isinstance(x_coord, (int, float)) else str(x_coord)
                y_str = f"{y_coord:.1f}" if isinstance(y_coord, (int, float)) else str(y_coord)
                print(f"        Mana={serial_solution.get('mana', 'N/A')}, Location=({x_str}, {y_str})")
            else:
                print(f"✗ FAIL: Grid {serial_result['grid_size']}, Factor {serial_result['num_searches_factor']}, Seed {serial_result['random_seed']}")
                for detail in mismatch_details:
                    print(f"  {detail}")
                validation_errors += 1

        if validation_errors == 0:
            print(f"\n✓ All {len(self.serial_results)} test cases passed validation!")
        else:
            print(f"\n✗ {validation_errors} validation errors found!")

        return validation_errors == 0

    def calculate_speedup(self):
        """Calculate speedup for each test case"""
        speedup_data = []

        for serial_result in self.serial_results:
            # Find corresponding parallel result
            parallel_result = None
            for p_result in self.parallel_results:
                if (p_result['grid_size'] == serial_result['grid_size'] and
                        p_result['num_searches_factor'] == serial_result['num_searches_factor'] and
                        p_result['random_seed'] == serial_result['random_seed']):
                    parallel_result = p_result
                    break

            if parallel_result:
                speedup = serial_result['avg_time'] / parallel_result['avg_time']
                speedup_data.append({
                    'grid_size': serial_result['grid_size'],
                    'num_searches_factor': serial_result['num_searches_factor'],
                    'random_seed': serial_result['random_seed'],
                    'serial_time': serial_result['avg_time'],
                    'parallel_time': parallel_result['avg_time'],
                    'speedup': speedup,
                    'efficiency': speedup / os.cpu_count() if os.cpu_count() else speedup / 4,
                    'mana': serial_result['solution_info'].get('mana', 'N/A'),
                    'x_location': serial_result['solution_info'].get('x', 'N/A'),
                    'y_location': serial_result['solution_info'].get('y', 'N/A'),
                    'serial_grid_points': serial_result['solution_info'].get('grid_points_evaluated', 'N/A'),
                    'parallel_grid_points': parallel_result['solution_info'].get('grid_points_evaluated', 'N/A')
                })

        return speedup_data

    def generate_speedup_graphs(self, speedup_data):
        """Generate speedup graphs"""
        print("Generating speedup graphs...")

        # Group by grid size and num_searches_factor
        grid_sizes = sorted(set([d['grid_size'] for d in speedup_data]))
        search_factors = sorted(set([d['num_searches_factor'] for d in speedup_data]))

        # Speedup vs Grid Size
        plt.figure(figsize=(12, 8))

        for factor in search_factors:
            factor_data = [d for d in speedup_data if d['num_searches_factor'] == factor]
            factor_data.sort(key=lambda x: x['grid_size'])

            sizes = [d['grid_size'] for d in factor_data]
            speedups = [d['speedup'] for d in factor_data]

            plt.plot(sizes, speedups, 'o-', label=f'Search Factor {factor}', linewidth=2, markersize=6)

        plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='No Speedup')
        plt.xlabel('Grid Size')
        plt.ylabel('Speedup')
        plt.title('Speedup vs Grid Size')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f'{self.results_dir}/speedup_vs_grid_size.png', dpi=300, bbox_inches='tight')
        plt.show()

        # Efficiency graph
        plt.figure(figsize=(12, 8))

        for factor in search_factors:
            factor_data = [d for d in speedup_data if d['num_searches_factor'] == factor]
            factor_data.sort(key=lambda x: x['grid_size'])

            sizes = [d['grid_size'] for d in factor_data]
            efficiencies = [d['efficiency'] * 100 for d in factor_data]  # Convert to percentage

            plt.plot(sizes, efficiencies, 's-', label=f'Search Factor {factor}', linewidth=2, markersize=6)

        plt.axhline(y=100, color='black', linestyle='--', alpha=0.5, label='Perfect Efficiency')
        plt.xlabel('Grid Size')
        plt.ylabel('Parallel Efficiency (%)')
        plt.title('Parallel Efficiency vs Grid Size')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f'{self.results_dir}/efficiency_vs_grid_size.png', dpi=300, bbox_inches='tight')
        plt.show()

        # Performance comparison (Serial vs Parallel times)
        plt.figure(figsize=(12, 8))

        for factor in search_factors:
            factor_data = [d for d in speedup_data if d['num_searches_factor'] == factor]
            factor_data.sort(key=lambda x: x['grid_size'])

            sizes = [d['grid_size'] for d in factor_data]
            serial_times = [d['serial_time'] for d in factor_data]
            parallel_times = [d['parallel_time'] for d in factor_data]

            plt.plot(sizes, serial_times, 'o-', label=f'Serial (Factor {factor})', linewidth=2, markersize=6)
            plt.plot(sizes, parallel_times, 's-', label=f'Parallel (Factor {factor})', linewidth=2, markersize=6)

        plt.xlabel('Grid Size')
        plt.ylabel('Execution Time (ms)')
        plt.title('Execution Time Comparison')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.yscale('log')  # Log scale for better visualization
        plt.savefig(f'{self.results_dir}/time_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

    def save_results(self):
        """Save all results to files"""
        print(f"Saving results to {self.results_dir}/...")
        print(f"Test images saved to {self.images_dir}/")

        # Save raw results as JSON
        with open(f'{self.results_dir}/serial_results.json', 'w') as f:
            json.dump(self.serial_results, f, indent=2)

        with open(f'{self.results_dir}/parallel_results.json', 'w') as f:
            json.dump(self.parallel_results, f, indent=2)

        # Save speedup data as CSV
        speedup_data = self.calculate_speedup()
        with open(f'{self.results_dir}/speedup_analysis.csv', 'w', newline='') as f:
            if speedup_data:
                writer = csv.DictWriter(f, fieldnames=speedup_data[0].keys())
                writer.writeheader()
                writer.writerows(speedup_data)

        # Save summary report
        with open(f'{self.results_dir}/summary_report.txt', 'w') as f:
            f.write("DUNGEON HUNTER PARALLEL PERFORMANCE ANALYSIS\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Test Configuration:\n")
            f.write(f"- CPU cores available: {os.cpu_count()}\n")
            f.write(f"- Java classpath: {self.classpath}\n")
            f.write(f"- Java source path: {self.src_path}\n")
            f.write(f"- Serial class: {self.serial_class}\n")
            f.write(f"- Parallel class: {self.parallel_class}\n")
            f.write(f"- Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- Results directory: {self.results_dir}\n")
            f.write(f"- Test images directory: {self.images_dir}\n\n")

            if speedup_data:
                f.write("Performance Analysis:\n")
                f.write(f"- Best speedup: {max(speedup_data, key=lambda x: x['speedup'])['speedup']:.2f}x\n")
                f.write(f"- Average speedup: {statistics.mean([d['speedup'] for d in speedup_data]):.2f}x\n")
                f.write(f"- Best efficiency: {max(speedup_data, key=lambda x: x['efficiency'])['efficiency']*100:.1f}%\n")
                f.write(f"- Average efficiency: {statistics.mean([d['efficiency'] for d in speedup_data])*100:.1f}%\n\n")

                f.write("Solution Analysis:\n")
                f.write("Grid_Size | Factor | Seed | Mana | Location | Serial_GridPts | Parallel_GridPts | Speedup\n")
                f.write("-" * 90 + "\n")
                for data in speedup_data:
                    x_coord = data['x_location']
                    y_coord = data['y_location']
                    x_str = f"{x_coord:.1f}" if isinstance(x_coord, (int, float)) else str(x_coord)
                    y_str = f"{y_coord:.1f}" if isinstance(y_coord, (int, float)) else str(y_coord)
                    f.write(f"{data['grid_size']:8d} | {data['num_searches_factor']:6.1f} | {data['random_seed']:4d} | "
                            f"{str(data['mana']):4s} | ({x_str},{y_str}) | "
                            f"{str(data['serial_grid_points']):13s} | {str(data['parallel_grid_points']):15s} | "
                            f"{data['speedup']:6.2f}x\n")

        return speedup_data

    def run_full_analysis(self, auto_recompile=True):
        """Run the complete analysis pipeline"""
        print("DUNGEON HUNTER PARALLEL PERFORMANCE ANALYSIS")
        print("=" * 60)
        print()

        # Check Java environment
        self.check_java_versions()

        # Test if we can run the classes
        print("Testing Java class compatibility...")
        test_result = subprocess.run(
            [self.java_path, "-cp", self.classpath, self.parallel_class, "10", "0.1", "1"],
            capture_output=True,
            text=True
        )

        if test_result.returncode != 0 and "UnsupportedClassVersionError" in test_result.stderr:
            print("✗ Java version mismatch detected!")
            if auto_recompile:
                print("Attempting automatic recompilation...")
                if self.recompile_sources():
                    print("✓ Recompilation successful, proceeding with analysis...")
                else:
                    print("✗ Recompilation failed. Please manually fix Java version issues.")
                    return
            else:
                print("Please recompile your Java files or use a compatible Java version.")
                return
        elif test_result.returncode != 0:
            print(f"✗ Other error running classes: {test_result.stderr}")
            return
        else:
            print("✓ Java classes are compatible")

        print()

        # Test configuration
        grid_sizes = [50, 100, 150, 200, 300]  # Range of input sizes
        num_searches_factors = [0.1, 0.2, 0.3]  # Different workload factors
        random_seeds = [1, 42, 123]  # Multiple seeds for validation (never 0)

        print(f"Test Configuration:")
        print(f"- Grid sizes: {grid_sizes}")
        print(f"- Search factors: {num_searches_factors}")
        print(f"- Random seeds: {random_seeds}")
        print(f"- CPU cores: {os.cpu_count()}")
        print(f"- Results will be saved to: {self.results_dir}")
        print(f"- Test images will be saved to: {self.images_dir}")
        print()

        # Profile both versions
        self.profile_serial(grid_sizes, num_searches_factors, random_seeds)
        self.profile_parallel(grid_sizes, num_searches_factors, random_seeds)

        # Validate correctness
        validation_passed = self.validate_solutions()

        if validation_passed:
            # Calculate speedup and generate graphs
            speedup_data = self.save_results()
            self.generate_speedup_graphs(speedup_data)

            print(f"\nAnalysis complete! Results saved to {self.results_dir}/")
            print(f"Test images saved to {self.images_dir}/")
            print("\nBest performing configurations:")
            best_speedup = max(speedup_data, key=lambda x: x['speedup'])
            best_x = best_speedup['x_location']
            best_y = best_speedup['y_location']
            best_x_str = f"{best_x:.1f}" if isinstance(best_x, (int, float)) else str(best_x)
            best_y_str = f"{best_y:.1f}" if isinstance(best_y, (int, float)) else str(best_y)
            print(f"- Best speedup: {best_speedup['speedup']:.2f}x at grid size {best_speedup['grid_size']}")
            print(f"  Mana: {best_speedup['mana']}, Location: ({best_x_str}, {best_y_str})")
            best_efficiency = max(speedup_data, key=lambda x: x['efficiency'])
            eff_x = best_efficiency['x_location']
            eff_y = best_efficiency['y_location']
            eff_x_str = f"{eff_x:.1f}" if isinstance(eff_x, (int, float)) else str(eff_x)
            eff_y_str = f"{eff_y:.1f}" if isinstance(eff_y, (int, float)) else str(eff_y)
            print(f"- Best efficiency: {best_efficiency['efficiency']*100:.1f}% at grid size {best_efficiency['grid_size']}")
            print(f"  Mana: {best_efficiency['mana']}, Location: ({eff_x_str}, {eff_y_str})")
        else:
            print("\nValidation failed! Please fix parallel implementation before benchmarking.")

# Usage
if __name__ == "__main__":
    # Initialize profiler for class files in bin directory, source files in src directory
    # No package name needed since classes are not in a package

    # Option 1: Let script try to auto-recompile if version mismatch
    profiler = DungeonHunterProfiler(classpath="bin", src_path="src", package_name=None)

    # Option 2: If you want to specify a specific Java version, uncomment and modify:
    # profiler = DungeonHunterProfiler(classpath="bin", src_path="src", package_name=None, java_path="/usr/lib/jvm/java-8-openjdk/bin/java")

    # Run complete analysis (auto_recompile=True by default)
    profiler.run_full_analysis()