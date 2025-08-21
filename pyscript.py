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

class DungeonHunterProfiler:
    def __init__(self, classpath="src", package_name=None, java_path=None):
        self.classpath = classpath
        self.package_name = package_name
        self.java_path = java_path or "java"  # Allow custom Java path

        # If no package, use simple class names
        if package_name:
            self.serial_class = f"{package_name}.DungeonHunterSerial"
            self.parallel_class = f"{package_name}.DungeonHunterParallel"
        else:
            self.serial_class = "DungeonHunterSerial"
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

        # Results storage
        self.serial_results = []
        self.parallel_results = []

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
        for line in output.split('\n'):
            if 'Dungeon Master (mana' in line:
                try:
                    # Extract mana value
                    mana_str = line.split('mana ')[1].split(')')[0]
                    info['mana'] = int(mana_str)
                except:
                    pass
            elif 'x=' in line and 'y=' in line and 'Dungeon Master' not in line:
                try:
                    # Extract coordinates
                    parts = line.split()
                    x_val = float(parts[0].split('x=')[1])
                    y_val = float(parts[1].split('y=')[1])
                    info['x'] = x_val
                    info['y'] = y_val
                except:
                    pass
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
                        print(f"  Solution: {solution_info}")
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
                        print(f"  Solution: {solution_info}")
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
            if 'mana' in serial_solution and 'mana' in parallel_solution:
                if serial_solution['mana'] != parallel_solution['mana']:
                    solutions_match = False

            if ('x' in serial_solution and 'x' in parallel_solution and
                    'y' in serial_solution and 'y' in parallel_solution):
                if (abs(serial_solution['x'] - parallel_solution['x']) > 0.1 or
                        abs(serial_solution['y'] - parallel_solution['y']) > 0.1):
                    solutions_match = False

            if solutions_match:
                print(f"✓ PASS: Grid {serial_result['grid_size']}, Factor {serial_result['num_searches_factor']}, Seed {serial_result['random_seed']}")
            else:
                print(f"✗ FAIL: Grid {serial_result['grid_size']}, Factor {serial_result['num_searches_factor']}, Seed {serial_result['random_seed']}")
                print(f"  Serial: {serial_solution}")
                print(f"  Parallel: {parallel_solution}")
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
                    'efficiency': speedup / os.cpu_count() if os.cpu_count() else speedup / 4
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
            f.write(f"- Serial class: {self.serial_class}\n")
            f.write(f"- Parallel class: {self.parallel_class}\n")
            f.write(f"- Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if speedup_data:
                f.write("Speedup Analysis:\n")
                f.write(f"- Best speedup: {max(speedup_data, key=lambda x: x['speedup'])['speedup']:.2f}x\n")
                f.write(f"- Average speedup: {statistics.mean([d['speedup'] for d in speedup_data]):.2f}x\n")
                f.write(f"- Best efficiency: {max(speedup_data, key=lambda x: x['efficiency'])['efficiency']*100:.1f}%\n")
                f.write(f"- Average efficiency: {statistics.mean([d['efficiency'] for d in speedup_data])*100:.1f}%\n")

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
            [self.java_path, "-cp", self.classpath, self.parallel_class, "10", "0.1", "0"],
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
        random_seeds = [0, 42, 123]  # Multiple seeds for validation

        print(f"Test Configuration:")
        print(f"- Grid sizes: {grid_sizes}")
        print(f"- Search factors: {num_searches_factors}")
        print(f"- Random seeds: {random_seeds}")
        print(f"- CPU cores: {os.cpu_count()}")
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
            print("\nBest performing configurations:")
            best_speedup = max(speedup_data, key=lambda x: x['speedup'])
            print(f"- Best speedup: {best_speedup['speedup']:.2f}x at grid size {best_speedup['grid_size']}")
            best_efficiency = max(speedup_data, key=lambda x: x['efficiency'])
            print(f"- Best efficiency: {best_efficiency['efficiency']*100:.1f}% at grid size {best_efficiency['grid_size']}")
        else:
            print("\nValidation failed! Please fix parallel implementation before benchmarking.")

# Usage
if __name__ == "__main__":
    # Initialize profiler for class files in same directory
    # No package name needed since classes are in current directory

    # Option 1: Let script try to auto-recompile if version mismatch
    profiler = DungeonHunterProfiler(classpath=".", package_name=None)

    # Option 2: If you want to specify a specific Java version, uncomment and modify:
    # profiler = DungeonHunterProfiler(classpath=".", package_name=None, java_path="/usr/lib/jvm/java-8-openjdk/bin/java")

    # Run complete analysis (auto_recompile=True by default)
    profiler.run_full_analysis()