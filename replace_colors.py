import os
import glob

replacements = {
    "#0B1220": "#0A0A0A",
    "#0D1526": "#050505",
    "#151F32": "#121212",
    "#4C7EFF": "#DC2626",
    "#3B6FEF": "#B91C1C",
    "#3B82F6": "#DC2626",
    "#24344D": "#262626",
    "#2A3950": "#262626",
    "rgba(11, 18, 32": "rgba(10, 10, 10",
    "rgba(11,18,32": "rgba(10,10,10"
}

for root, _, files in os.walk("camfindai-ui/src"):
    for file in files:
        if file.endswith((".tsx", ".ts", ".css")):
            filepath = os.path.join(root, file)
            with open(filepath, "r") as f:
                content = f.read()
            
            new_content = content
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
                
            if new_content != content:
                with open(filepath, "w") as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

