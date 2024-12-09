import os
import sys
import subprocess
import requests
import toml
import re

# Set default email for debian changelog
os.environ['DEBEMAIL'] = 'info@schulstick.org'
from datetime import datetime
from packaging.version import Version, parse

def get_current_version(pyproject_path):
    try:
        with open(pyproject_path, 'r') as f:
            pyproject = toml.load(f)
            return pyproject['project']['version']
    except (FileNotFoundError, KeyError):
        return None

def bump_version(version_str, bump_type='patch'):
    v = parse(version_str)
    major, minor, patch = v.major, v.minor, v.micro
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def update_pyproject(pyproject_path, new_version):
    with open(pyproject_path) as f:
        content = f.read()
    
    updated = re.sub(
        r'(version\s*=\s*)"[^"]+"',
        f'\\1"{new_version}"',
        content
    )
    
    with open(pyproject_path, 'w') as f:
        f.write(updated)

def update_flake(flake_path, new_version):
    with open(flake_path) as f:
        content = f.read()
    
    updated = re.sub(
        r'(version\s*=\s*)"[^"]+"',
        f'\\1"{new_version}"',
        content
    )
    
    with open(flake_path, 'w') as f:
        f.write(updated)

def get_commit_logs():
    try:
        last_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0', '@^'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        # If no previous tag exists, get all commits
        return subprocess.check_output(
            ['git', 'log', '--oneline'],
            universal_newlines=True
        )
    
    return subprocess.check_output(
        ['git', 'log', '--oneline', f'{last_tag}..@'],
        universal_newlines=True
    )

def generate_changelog_with_claude(commits):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return format_raw_changelog(commits)
    
    headers = {
        'x-api-key': api_key,
        'content-type': 'application/json',
        'anthropic-version': '2023-06-01'
    }
    
    prompt = f"""Please create a changelog from these git commits. Group related changes together and make it human readable, skip things that are too technical or have been reverted. Concentrate on the features and fixes that are user relevant:

{commits}

Summary should be 2 or three short sentences.
Format the output in markdown with sections for Summary, Features, Fixes, and Other Changes. Do not include git commit hashes or any form of version numbers."""

    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers=headers,
        json={
            'model': 'claude-3-haiku-20240307',
            'max_tokens': 1024,
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )
    
    if response.status_code == 200:
        return response.json()['content'][0]['text']
    else:
        print(f"Error generating changelog: {response.status_code}")
        return format_raw_changelog(commits)

def format_raw_changelog(commits):
    print("Using raw changelog")
    changes = []
    for line in commits.splitlines():
        if line.strip():
            changes.append(f"* {line}")
    return "\n".join(changes)

def update_changelog(changelog_path, new_version, changes):
    current_date = datetime.now().strftime("%Y-%m-%d")
    new_content = f"""# {new_version} ({current_date})

{changes}

"""
    
    if os.path.exists(changelog_path):
        with open(changelog_path) as f:
            existing_content = f.read()
        new_content += existing_content
    
    with open(changelog_path, 'w') as f:
        f.write(new_content)

def update_debian_changelog(new_version, changes):
    # First create entry with placeholder
    subprocess.run(['dch', '-v', new_version, 'unstable', changes.replace('\n', '\n  ')], check=True)
    
    
def main():
    bump_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    if bump_type not in ('major', 'minor', 'patch'):
        print("Invalid bump type. Use 'major', 'minor', or 'patch'")
        sys.exit(1)
    
    # Get paths
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pyproject_path = os.path.join(script_dir, 'pyproject.toml')
    flake_path = os.path.join(script_dir, 'flake.nix')
    changelog_path = os.path.join(script_dir, 'CHANGELOG.md')
    
    # Get and bump version
    current_version = get_current_version(pyproject_path)
    if not current_version:
        print("Could not find current version")
        sys.exit(1)
    
    new_version = bump_version(current_version, bump_type)
    print(f"Bumping version from {current_version} to {new_version}")
    
    # Update version in files
    update_pyproject(pyproject_path, new_version)
    update_flake(flake_path, new_version)
    
    # Generate changelog
    commits = get_commit_logs()
    changes = generate_changelog_with_claude(commits)
    
    # Update changelogs
    update_changelog(changelog_path, new_version, changes)
    update_debian_changelog(new_version, changes)
    
    print(f"""
Release {new_version} prepared successfully!
Please review the changes and then:
1. Review CHANGELOG.md
2. Review debian/changelog
3. Commit the changes
4. Push the changes and tag with:
   git tag v{new_version}
   git push origin v{new_version}
""")

if __name__ == '__main__':
    main()
