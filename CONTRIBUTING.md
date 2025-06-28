# Contributing to Packet Tracer Mark Scanner

**Version: 0.1**

Thank you for your interest in contributing to the Packet Tracer Mark Scanner project! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you encounter bugs or have feature requests:

1. **Search existing issues** first to avoid duplicates
2. **Use the issue templates** when creating new issues
3. **Provide detailed information** including:
   - Operating system and version
   - Python version
   - Packet Tracer version
   - Tesseract version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Log files (if applicable)

### Submitting Code Changes

1. **Fork the repository** and create a new branch for your changes
2. **Follow the coding standards** outlined below
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description of changes

## Development Setup

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/packetracermark.git
   cd packetracermark
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run validation script**:
   ```bash
   python scripts/validate_setup.py
   ```

4. **Test your changes using the main launcher**:
   ```bash
   python run.py  # Interactive menu for all tools
   ```

5. **Or test individual components**:
   ```bash
   python scripts/batch_process.py  # Test full workflow
   python scripts/pka_capture.py   # Test capture only
   python scripts/mark_scanner.py  # Test scanning only
   ```

## Coding Standards

### Python Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for all functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable and function names

### Code Organization

- Keep configuration in `scripts/config.py`
- Add new features as separate modules in the `scripts/` directory
- Update `requirements.txt` for new dependencies
- Maintain backward compatibility when possible
- Use the `run.py` launcher as the main entry point
- Follow the established project structure:
  ```
  project/
  ├── run.py              # Main launcher (v0.1)
  ├── scripts/            # All Python modules
  │   ├── config.py       # Configuration management
  │   ├── pka_capture.py  # Screenshot capture
  │   ├── mark_scanner.py # OCR processing
  │   └── ...
  ├── pka/               # PKA files directory
  ├── images/            # Screenshots directory
  ├── logs/              # Log files directory
  └── results/           # Output CSV files
  ```

### Documentation

- Update `README.md` for user-facing changes
- Add docstrings for all public functions
- Include examples in docstrings
- Update configuration documentation for new settings

## Testing Guidelines

### Manual Testing

- Test with different PKA file types
- Test with various image qualities
- Test error handling scenarios
- Verify cross-platform compatibility (if applicable)

### Test Data

- Use anonymized sample data
- Include edge cases in test scenarios
- Test with different Packet Tracer versions
- Validate OCR accuracy with known results

## Pull Request Process

1. **Create a descriptive title** for your PR
2. **Fill out the PR template** completely
3. **Link related issues** using keywords (fixes #123)
4. **Request review** from maintainers
5. **Address feedback** promptly
6. **Ensure CI passes** (when implemented)

## Code Review Criteria

Pull requests will be evaluated on:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Testing**: Are edge cases covered?
- **Documentation**: Is it properly documented?
- **Compatibility**: Does it break existing functionality?

## Feature Requests

When proposing new features:

1. **Describe the use case** clearly
2. **Explain the benefit** to users
3. **Consider implementation complexity**
4. **Discuss potential alternatives**
5. **Be open to feedback** and iteration

## Version 0.1 Focus Areas

As this is the initial release (v0.1), we're particularly focused on:

### Core Stability
- **Bug fixes** and error handling improvements
- **Documentation** enhancements and clarifications
- **Setup and installation** process improvements
- **Cross-platform compatibility** testing and fixes

### User Experience
- **run.py launcher** enhancements and new menu options
- **Better error messages** and user guidance
- **Improved logging** and debugging information
- **Setup validation** improvements

### Code Quality
- **Code organization** and structure improvements
- **Performance optimizations** for OCR processing
- **Memory usage** optimizations for large batches
- **Configuration management** enhancements

## Areas for Contribution

We welcome contributions in these areas:

### High Priority (v0.1+)
- **Cross-platform support** (Linux, macOS)
- **Improved OCR accuracy** algorithms
- **Better error handling** and user feedback
- **Performance optimizations**
- **Unit tests** and automated testing
- **Enhanced run.py launcher** with more options

### Medium Priority (v0.2+)
- **GUI interface** for easier use
- **Batch processing** improvements
- **Export formats** (Excel, JSON, XML)
- **Configuration management** enhancements
- **Logging improvements**
- **Real-time progress indicators**

### Low Priority (v0.3+)
- **Docker containerization**
- **Web interface**
- **Database integration**
- **Advanced reporting features**
- **API endpoints** for integration

## Community Guidelines

- **Be respectful** and inclusive
- **Help newcomers** get started
- **Share knowledge** and best practices
- **Provide constructive feedback**
- **Follow the code of conduct**

## Getting Help

If you need help with contributing:

1. **Check the documentation** first
2. **Search existing issues** and discussions
3. **Ask questions** in issue comments
4. **Join community discussions**

## Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **Project documentation**

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Packet Tracer Mark Scanner project!
