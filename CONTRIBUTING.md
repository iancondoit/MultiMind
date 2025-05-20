# Contributing to MultiMind

Thank you for your interest in contributing to MultiMind! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## Getting Started

1. Fork the repository
2. Clone your fork to your local machine
3. Create a new branch for your work
4. Make your changes
5. Push your branch to your fork
6. Submit a pull request

## Development Process

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multimind.git
   cd multimind
   ```

2. Make the multimind script executable:
   ```bash
   chmod +x multimind.py
   ```

3. Initialize the directory structure:
   ```bash
   mkdir -p output/completions output/handoffs
   ```

### Coding Standards

- Follow PEP 8 for Python code
- Use meaningful variable, function, and class names
- Include docstrings for all functions, classes, and modules
- Write unit tests for new functionality
- Keep functions and methods concise and focused on a single task

### Documentation

- Update documentation when adding or modifying features
- Use Markdown for documentation files
- Keep the README.md up to date with the latest features
- Update the USER_GUIDE.md for significant changes

### Testing

- Write unit tests for new functionality
- Ensure existing tests pass before submitting a pull request
- Test your changes with realistic use cases

## Pull Request Process

1. Update the documentation with details of changes
2. Update the version number in README.md and USER_GUIDE.md
3. The PR requires approval from at least one maintainer
4. Once approved, a maintainer will merge your PR

## Feature Requests

If you have an idea for a new feature, please submit it as an issue first. Describe the feature, its use case, and any relevant implementation details.

## Bug Reports

If you find a bug, please submit it as an issue with the following information:
- A description of the bug
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Any error messages or stack traces
- Environment information (OS, Python version, etc.)

## Project Structure

When contributing, be aware of the project's structure:

```
/
├── multimind.py             # Main script
├── MultiMindPM/             # Project Manager directory
│   ├── config.json          # Configuration
│   ├── roadmap.md           # Main roadmap
│   ├── roadmaps/            # Project-specific roadmaps
│   ├── directives/          # Project directives
│   ├── reports/             # Status reports
│   ├── rules/               # Coding standards and protocols
│   ├── handoffs/            # Inter-project requests
│   ├── completions/         # Project completion reports
│   └── .cursor-ai-templates/ # AI instruction templates
├── output/                  # Shared output directory
│   ├── completions/         # Completion markers
│   └── handoffs/            # Handoff requests
└── [Project directories]    # Individual project directories
```

## Core Components

When modifying the core functionality, consider these main components:

1. **File Synchronization**: Distributing files from PM to projects
2. **Status Collection**: Gathering status reports from projects
3. **Handoff Processing**: Managing inter-project coordination
4. **Completion Reporting**: Processing project phase completions
5. **Project Initialization**: Setting up new project structures

## Contact

If you have questions or need help, please contact the maintainers through:
- GitHub issues
- Email: [example@example.com]

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (GPL-3.0). 