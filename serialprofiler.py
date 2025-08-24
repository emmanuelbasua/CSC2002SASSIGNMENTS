import subprocess
import time
import csv
import statistics
import os
from datetime import datetime

class SerialDungeonHunterProfiler:
    def __init__(self, classpath="bin", java_path=None):
        self.classpath = classpath
        self.java_path = java_path or "java"
        self.serial_class = "DungeonHunter"
        self.results = []

    def run_program(self, grid_size, num_searches_factor, random_seed, runs=3):
        """Run the serial program multiple times and return average timing"""
        times = []
        args = [str(grid_size), str(num_searches_factor), str(random_seed)]

        for run in range(runs):
            start_time = time.time()

            try:
                result = subprocess.run(
                    [self.java_path, "-cp", self.classpath, self.serial_class] + args,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                end_time = time.time()

                if result.returncode != 0:
                    print(f"Error running with args {args}: {result.stderr}")
                    return None

                # Extract execution time from output or use wall clock time
                program_time = self.extract_execution_time(result.stdout)
                if program_time is None:
                    program_time = (end_time - start_time) * 1000  # Convert to ms

                times.append(program_time)

            except subprocess.TimeoutExpired:
                print(f"Timeout for grid size {grid_size}")
                return None
            except Exception as e:
                print(f"Exception: {e}")
                return None

        return {
            'avg_time': statistics.mean(times),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
            'times': times
        }

    def extract_execution_time(self, output):
        """Extract execution time from program output"""
        for line in output.split('\n'):
            if 'time:' in line and 'ms' in line:
                try:
                    time_str = line.split('time:')[1].split('ms')[0].strip()
                    return float(time_str)
                except:
                    continue
        return None

    def profile_serial(self, grid_sizes, num_searches_factors, random_seeds, runs=3):
        """Profile the serial version across different parameters"""
        print("Profiling Serial DungeonHunter...")
        print("-" * 40)

        total_tests = len(grid_sizes) * len(num_searches_factors) * len(random_seeds)
        test_count = 0

        for grid_size in grid_sizes:
            for num_searches_factor in num_searches_factors:
                for random_seed in random_seeds:
                    test_count += 1
                    print(f"Test {test_count}/{total_tests}: Grid={grid_size}, Factor={num_searches_factor}, Seed={random_seed}")

                    result = self.run_program(grid_size, num_searches_factor, random_seed, runs)

                    if result:
                        self.results.append({
                            'grid_size': grid_size,
                            'grid_area': grid_size * grid_size,
                            'num_searches_factor': num_searches_factor,
                            'random_seed': random_seed,
                            'avg_time_ms': round(result['avg_time'], 2),
                            'std_time_ms': round(result['std_time'], 2),
                            'run1_time_ms': round(result['times'][0], 2) if len(result['times']) > 0 else None,
                            'run2_time_ms': round(result['times'][1], 2) if len(result['times']) > 1 else None,
                            'run3_time_ms': round(result['times'][2], 2) if len(result['times']) > 2 else None,
                        })

                        print(f"  Average time: {result['avg_time']:.2f} ± {result['std_time']:.2f} ms")
                    else:
                        print(f"  Failed to run")

                    print()

    def save_to_csv(self, filename=None):
        """Save results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"serial_dungeon_hunter_profile_{timestamp}.csv"

        if not self.results:
            print("No results to save!")
            return

        print(f"Saving {len(self.results)} results to {filename}")

        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'grid_size', 'grid_area', 'num_searches_factor', 'random_seed',
                'avg_time_ms', 'std_time_ms', 'run1_time_ms', 'run2_time_ms', 'run3_time_ms'
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"Results saved to {filename}")
        return filename

    def run_analysis(self):
        """Run the complete profiling analysis"""
        print("SERIAL DUNGEON HUNTER PROFILER")
        print("=" * 40)

        # Test configuration - adjust these ranges as needed
        grid_sizes = [50, 75, 100, 150, 200, 275]
        num_searches_factors = [0.1, 0.2, 0.4]
        random_seeds = [3, 60, 141]  # Multiple seeds for better statistics

        print(f"Configuration:")
        print(f"- Grid sizes: {grid_sizes}")
        print(f"- Search factors: {num_searches_factors}")
        print(f"- Random seeds: {random_seeds}")
        print(f"- Runs per test: 3")
        print()

        # Profile the serial version
        self.profile_serial(grid_sizes, num_searches_factors, random_seeds)

        # Save results
        if self.results:
            filename = self.save_to_csv()

            # Print summary statistics
            print("\nSummary Statistics:")
            avg_times = [r['avg_time_ms'] for r in self.results]
            print(f"- Total tests: {len(self.results)}")
            print(f"- Average execution time: {statistics.mean(avg_times):.2f} ms")
            print(f"- Minimum execution time: {min(avg_times):.2f} ms")
            print(f"- Maximum execution time: {max(avg_times):.2f} ms")

            # Find fastest and slowest configurations
            fastest = min(self.results, key=lambda x: x['avg_time_ms'])
            slowest = max(self.results, key=lambda x: x['avg_time_ms'])

            print(f"\nFastest configuration:")
            print(f"  Grid: {fastest['grid_size']}, Factor: {fastest['num_searches_factor']}, Seed: {fastest['random_seed']}")
            print(f"  Time: {fastest['avg_time_ms']:.2f} ms")

            print(f"\nSlowest configuration:")
            print(f"  Grid: {slowest['grid_size']}, Factor: {slowest['num_searches_factor']}, Seed: {slowest['random_seed']}")
            print(f"  Time: {slowest['avg_time_ms']:.2f} ms")

            return filename
        else:
            print("No successful test runs!")
            return None

# Usage
if __name__ == "__main__":
    # Create profiler instance
    profiler = SerialDungeonHunterProfiler(classpath="bin")

    # Run the analysis
    csv_file = profiler.run_analysis()

    if csv_file:
        print(f"\nProfiling complete! Results saved to: {csv_file}")