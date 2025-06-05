# Changelog

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