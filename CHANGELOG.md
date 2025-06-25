# Changelog

## [0.3.0] - 2025-06-16

### 🚀 New Features

- Added AI-driven plan analysis agent (PlanAnalysisAgent) with Azure context integration.
- Introduced `replace` attribute capture in plan analyzer for accurate reporting of resource replacements.
- Flattened single-element action lists in plan analysis to simplify actions representation.

### 🐛 Bug Fixes

- Skipped no-op changes properly in plan analyzer to avoid redundant entries.
- Fixed reporting of replacement operations in plan reporter.

### 📖 Documentation Improvements

- Updated README and documentation for AI analysis and enhanced command-line usage.
- Refreshed advanced usage and API docs to reflect new features and configurations.

### ⬆️ Dependencies

- Added `backoff` for improved retry and error handling.

### ⚙️ Other Changes

- Removed deprecated `scripts/install_ai_deps.sh`.
- Refactored base reporter and context management for consistency.

---

## [0.2.0] - 2024-06-15

### 🎨 Enhanced Output Formats and CLI Arguments

This release introduces multiple output formats and improved CLI arguments for better usability and integration capabilities.

### Major Changes

- **Multiple Output Formats:**
  - Added support for three output formats:
    - Console output (default): Colorized, human-readable format
    - Markdown output: Structured markdown for documentation and code reviews
    - JSON output: Machine-readable format for integration with other tools
  - Each format maintains consistent data structure while optimizing for its use case

- **Improved CLI Arguments:**
  - New output format options:
    - `--output`: Choose between 'default', 'markdown', or 'json' formats
    - `--detailed`: Show detailed resource information
    - `--hide-changes`: Hide detailed attribute changes
  - Deprecated arguments (with backward compatibility):
    - `--changes` → Use `--hide-changes` instead
    - `--details` → Use `--detailed` instead
    - `--markdown` → Use `--output markdown` instead

- **Code Quality Improvements:**
  - Refactored reporter implementation to follow DRY principles
  - Centralized resource processing logic
  - Improved test coverage for all output formats
  - Enhanced error handling and validation

### Migration Notes

- The deprecated arguments will be removed in a future version
- Update your scripts and CI/CD pipelines to use the new argument names
- Consider using the JSON output format for better integration with other tools

---

## [0.1.0] - 2024-06-05

### 🎉 Project Reborn: tfsumpy 0.1.0

This release marks a **new beginning** for tfsumpy. The project has been refocused and rebuilt to be a best-in-class Terraform plan summarizer, with a modern, extensible architecture.

### Major Changes

- **Simplified Core:**
  - tfsumpy now focuses exclusively on summarizing Terraform plan files. All previous risk assessment and policy compliance features have been removed.
  - The CLI and API are streamlined for clarity and ease of use.

- **Extensible by Design:**
  - tfsumpy now supports plug-and-play extensions via a simple plugin system. You can add your own analyzers and reporters by dropping Python files in a `plugins/` directory (or specify `--plugin-dir`).
  - This makes it easy to add custom compliance checks, cost estimation, notifications, or integrations with other tools—without modifying the core codebase.

### Why This Change?

- **Focus:**
  - By concentrating on plan summarization, tfsumpy is easier to use, maintain, and extend.
- **Flexibility:**
  - Users and organizations can now build their own extensions for any workflow or integration.
- **Community:**
  - We encourage sharing and contributing plugins to grow the ecosystem.

### Migration & Support Notes

- **Older releases are no longer supported.**
  - The previous risk and policy features are not maintained and will not receive updates.
  - If you need those features, consider implementing them as plugins using the new extension system.
- **This is a fresh start.**
  - We recommend all users upgrade to 0.1.0+ and take advantage of the new architecture.

### How to Extend

- See the [Extending tfsumpy](docs/extending.md) documentation for examples and best practices.
- Write your own analyzer or reporter, place it in the `plugins/` directory, and tfsumpy will auto-load it.

---

## [Older releases]

Older versions of tfsumpy are deprecated and will not be supported going forward. Please upgrade to 0.1.0+ for the latest features.