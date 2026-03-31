import os
import re

def audit_assets():
    template_dir = 'templates'
    static_dir = 'static'
    
    broken_refs = []
    total_refs = 0
    
    # regex for url_for with static
    # Support 'static', "static" and filename='...', filename="..."
    pattern = re.compile(r"url_for\(\s*['\"]static['\"]\s*,\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)")
    
    print(f"Checking templates in: {os.path.abspath(template_dir)}")
    print(f"Static directory: {os.path.abspath(static_dir)}")

    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                # print(f"Checking {file_path}...")
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for filename in matches:
                            total_refs += 1
                            full_path = os.path.join(static_dir, filename).replace("/", os.sep).replace("\\", os.sep)
                            if not os.path.exists(full_path):
                                broken_refs.append({
                                    'template': file_path,
                                    'asset': filename
                                })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    print(f"--- Audit Summary ---")
    print(f"Total references checked: {total_refs}")
    print(f"Broken references found: {len(broken_refs)}")
    
    if broken_refs:
        print("\n--- Broken References ---")
        for ref in broken_refs:
            print(f"Template: {ref['template']}")
            print(f"Asset:    {ref['asset']}")
            # Try to find if the file exists elsewhere in static/
            basename = os.path.basename(ref['asset'])
            found_elsewhere = []
            for s_root, s_dirs, s_files in os.walk(static_dir):
                if basename in s_files:
                    found_elsewhere.append(os.path.relpath(os.path.join(s_root, basename), static_dir))
            
            if found_elsewhere:
                print(f"Suggested alternatives: {', '.join(found_elsewhere)}")
            else:
                print("No alternative found in static/ directory.")
            print("-" * 20)

if __name__ == "__main__":
    audit_assets()
