import subprocess
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import statistics
import csv
from datetime import datetime
import re

class MinimalDungeonHunterProfiler:
    def __init__(self, classpath="bin", src_path="src", java_path=None, verbose=True):
        self.classpath = classpath
        self.src_path = src_path
        self.java_path = java_path or "java"
        self.serial_class = "DungeonHunter"
        self.parallel_class = "DungeonHunterParallel"
        self.results_dir = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.images_dir = os.path.join(self.results_dir, "images")
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        self.serial_results = []
        self.parallel_results = []
        self.test_images = []
        self.verbose = verbose

    # ---------------- Run Java Programs ----------------
    def run_program(self, class_name, grid_size, num_searches_factor, random_seed, runs=3):
        times = []
        outputs = []
        args = [str(grid_size), str(num_searches_factor), str(random_seed)]
        for _ in range(runs):
            start_time = time.time()
            result = subprocess.run(
                [self.java_path, "-cp", self.classpath, class_name] + args,
                capture_output=True,
                text=True
            )
            end_time = time.time()
            program_time = self.extract_execution_time(result.stdout) or ((end_time - start_time) * 1000)
            times.append(program_time)
            outputs.append({'stdout': result.stdout, 'program_time': program_time})
        avg_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        return {'avg_time': avg_time, 'std_time': std_time, 'times': times, 'outputs': outputs}

    def extract_execution_time(self, output):
        for line in output.split('\n'):
            if 'time:' in line and 'ms' in line:
                try:
                    return float(line.split('time:')[1].split('ms')[0].strip())
                except:
                    continue
        return None

    def extract_solution_info(self, output):
        info = {}
        for line in output.split('\n'):
            if 'mana' in line:
                try:
                    info['mana'] = int(line.split('mana ')[1].split(')')[0])
                except:
                    pass
            if 'x=' in line and 'y=' in line:
                x_match = re.search(r'x=([+-]?\d*\.?\d+)', line)
                y_match = re.search(r'y=([+-]?\d*\.?\d+)', line)
                if x_match and y_match:
                    info['x'] = float(x_match.group(1))
                    info['y'] = float(y_match.group(1))
            if 'number dungeon grid points evaluated:' in line:
                match = re.search(r'number dungeon grid points evaluated:\s*(\d+)', line)
                if match:
                    info['grid_points_evaluated'] = int(match.group(1))
        return info

    # ---------------- Profile Serial or Parallel Version ----------------
    def profile_version(self, class_name, grid_sizes, factors, seeds):
        results = []
        total_tests = len(grid_sizes) * len(factors) * len(seeds)
        test_count = 0
        for grid in grid_sizes:
            for factor in factors:
                for seed in seeds:
                    test_count += 1
                    print(f"Running {class_name} test {test_count}/{total_tests} — Grid: {grid}, Factor: {factor}, Seed: {seed}")
                    result = self.run_program(class_name, grid, factor, seed)
                    solution = self.extract_solution_info(result['outputs'][0]['stdout'])
                    results.append({
                        'grid_size': grid,
                        'num_searches_factor': factor,
                        'random_seed': seed,
                        'avg_time': result['avg_time'],
                        'std_time': result['std_time'],
                        'solution_info': solution
                    })
        return results

    # ---------------- Speedup Calculation ----------------
    def calculate_speedup(self):
        speedup_data = []
        for s in self.serial_results:
            p = next((p for p in self.parallel_results if
                      p['grid_size']==s['grid_size'] and
                      p['num_searches_factor']==s['num_searches_factor'] and
                      p['random_seed']==s['random_seed']), None)
            if p:
                speedup = s['avg_time']/p['avg_time']
                speedup_data.append({
                    'grid_size': s['grid_size'],
                    'num_searches_factor': s['num_searches_factor'],
                    'random_seed': s['random_seed'],
                    'serial_time': s['avg_time'],
                    'parallel_time': p['avg_time'],
                    'speedup': speedup,
                    'efficiency': speedup / (os.cpu_count() or 4),
                    'mana': s['solution_info'].get('mana','N/A'),
                    'x_location': s['solution_info'].get('x','N/A'),
                    'y_location': s['solution_info'].get('y','N/A'),
                    'serial_grid_points': s['solution_info'].get('grid_points_evaluated','N/A'),
                    'parallel_grid_points': p['solution_info'].get('grid_points_evaluated','N/A')
                })
        return speedup_data

    # ---------------- Generate Graphs ----------------
    def generate_speedup_graphs(self, speedup_data):
        for data in speedup_data:
            data['grid_area'] = data['grid_size']**2

        seeds = sorted(set(d['random_seed'] for d in speedup_data))
        factors = sorted(set(d['num_searches_factor'] for d in speedup_data))

        # By seed
        fig, axes = plt.subplots(1, len(seeds), figsize=(6*len(seeds),6))
        if len(seeds)==1: axes=[axes]
        colors = plt.cm.tab10(np.linspace(0,1,len(factors)))
        for i, seed in enumerate(seeds):
            ax = axes[i]
            for j, factor in enumerate(factors):
                data = sorted([d for d in speedup_data if d['random_seed']==seed and d['num_searches_factor']==factor], key=lambda x: x['grid_area'])
                ax.plot([d['grid_area'] for d in data],[d['speedup'] for d in data],'o-',color=colors[j],label=f'Factor {factor}')
            ax.axhline(1,color='black',linestyle='--',alpha=0.5)
            ax.set_xlabel('Grid Area')
            ax.set_ylabel('Speedup')
            ax.set_title(f'Seed {seed}')
            ax.legend(); ax.grid(True,alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.images_dir, "speedup_by_seed.png"))
        self.test_images.append(fig)
        plt.show()

        # By factor
        fig, axes = plt.subplots(1, len(factors), figsize=(6*len(factors),6))
        if len(factors)==1: axes=[axes]
        seed_colors = plt.cm.tab10(np.linspace(0,1,len(seeds)))
        for i, factor in enumerate(factors):
            ax = axes[i]
            for j, seed in enumerate(seeds):
                data = sorted([d for d in speedup_data if d['random_seed']==seed and d['num_searches_factor']==factor], key=lambda x: x['grid_area'])
                ax.plot([d['grid_area'] for d in data],[d['speedup'] for d in data],'o-',color=seed_colors[j],label=f'Seed {seed}')
            ax.axhline(1,color='black',linestyle='--',alpha=0.5)
            ax.set_xlabel('Grid Area')
            ax.set_ylabel('Speedup')
            ax.set_title(f'Factor {factor}')
            ax.legend(); ax.grid(True,alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.images_dir, "speedup_by_factor.png"))
        self.test_images.append(fig)
        plt.show()

    # ---------------- Save Results ----------------
    def save_results(self):
        if self.verbose:
            print(f"Saving results to {self.results_dir}/...")
            print(f"Test images saved to {self.images_dir}/")

        # Save JSON
        with open(f'{self.results_dir}/serial_results.json', 'w') as f:
            json.dump(self.serial_results, f, indent=2)
        with open(f'{self.results_dir}/parallel_results.json', 'w') as f:
            json.dump(self.parallel_results, f, indent=2)

        # Save CSV
        speedup_data = self.calculate_speedup()
        csv_fieldnames = [
            "grid_size", "num_searches_factor", "random_seed",
            "mana", "x_location", "y_location",
            "serial_grid_points", "parallel_grid_points",
            "serial_time", "parallel_time", "speedup", "efficiency"
        ]
        with open(f'{self.results_dir}/speedup_analysis.csv', 'w', newline='') as f:
            if speedup_data:
                writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
                writer.writeheader()
                writer.writerows(speedup_data)

        # Summary report
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

        # Save images
        for i, img in enumerate(self.test_images):
            img_path = os.path.join(self.images_dir, f'test_image_{i+1}.png')
            img.savefig(img_path)
            if self.verbose:
                print(f"Saved image: {img_path}")

        return speedup_data

    # ---------------- Run Full Analysis ----------------
    def run_analysis(self):
        grid_sizes = [10, 25, 40, 50, 75, 90, 100, 115, 135, 150, 185, 200, 225, 275, 315]
        factors = [0.1, 1, 3]
        seeds = [3, 60,90]

        self.serial_results = self.profile_version(self.serial_class, grid_sizes, factors, seeds)
        self.parallel_results = self.profile_version(self.parallel_class, grid_sizes, factors, seeds)

        speedup_data = self.calculate_speedup()
        self.generate_speedup_graphs(speedup_data)
        self.save_results()
        print("\nAnalysis complete!")

# ---------------- Main ----------------
if __name__ == "__main__":
    profiler = MinimalDungeonHunterProfiler()
    profiler.run_analysis()
