import subprocess

result = subprocess.run(
    ["java", "HelloWorld"],
    capture_output=True,
    text=True
)

print("Output:", result.stdout)
print("Errors:", result.stderr)