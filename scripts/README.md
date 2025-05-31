# Dependabot Auto-approver

This script automatically approves and merges Dependabot pull requests that pass all required checks.

## Features

- Automatically finds open Dependabot PRs
- Checks if all required status checks have passed
- Approves the PR if not already approved
- Merges the PR with a properly formatted commit message
- Handles errors gracefully and provides meaningful logs

## Requirements

- Python 3.8+
- PyGithub
- A GitHub Personal Access Token with `repo` scope

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install -r scripts/requirements-test.txt
   ```

## Usage

1. Set the required environment variables:
   ```bash
   export GITHUB_TOKEN=your_github_token
   export GITHUB_REPOSITORY=owner/repo
   ```

2. Run the script:
   ```bash
   python -m scripts.approve_dependabot_prs
   ```

## GitHub Actions Workflow

To run this automatically on a schedule, use the provided GitHub Actions workflow:

```yaml
name: Dependabot Auto-merge

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  dependabot-auto-merge:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r scripts/requirements-test.txt
    
    - name: Run Dependabot auto-approver
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITHUB_REPOSITORY: ${{ github.repository }}
      run: |
        python -m scripts.approve_dependabot_prs
```

## Configuration

You can customize the behavior by setting the following environment variables:

- `GITHUB_TOKEN`: Required. A GitHub Personal Access Token with `repo` scope
- `GITHUB_REPOSITORY`: Required. The repository in the format 'owner/repo'
- `REQUIRED_CHECKS`: Optional. Comma-separated list of required check names that must pass before merging

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
