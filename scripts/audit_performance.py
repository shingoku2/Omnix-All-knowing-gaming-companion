import os
import re

def scan_for_performance_issues(root_dir):
    issues = []
    
    # Patterns to look for
    patterns = {
        r'useEffect\(\(\) => \{.*?\}(\s*,\s*\[\])?\)': 'useEffect without dependency array or empty array (check if intentional)',
        r'console\.log': 'Console log left in code',
        r'setInterval': 'setInterval usage (verify cleanup)',
        r'setTimeout': 'setTimeout usage (verify cleanup)',
        r'expensiveFunction': 'Potential expensive function call',
    }
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern, desc in patterns.items():
                        if re.search(pattern, content):
                            issues.append(f"{path}: {desc}")
                            
    return issues

if __name__ == "__main__":
    print("Scanning frontend for performance antipatterns...")
    results = scan_for_performance_issues('frontend/src')
    if results:
        print("Potential issues found:")
        for issue in results:
            print(f"- {issue}")
    else:
        print("No obvious performance antipatterns found.")
