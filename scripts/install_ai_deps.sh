#!/bin/bash

# Function to print colored messages
print_message() {
    echo -e "\033[1;34m$1\033[0m"
}

print_message "Installing AI dependencies for tfsumpy..."

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Error: poetry is not installed"
    exit 1
fi

# Install OpenAI package
print_message "\nInstalling OpenAI package..."
poetry add openai

# Install Google Generative AI package
print_message "\nInstalling Google Generative AI package..."
poetry add google-generativeai

# Install Anthropic package
print_message "\nInstalling Anthropic package..."
poetry add anthropic

print_message "\nAll AI dependencies have been installed successfully!"
print_message "You can now use tfsumpy with AI summarization."
print_message "\nExample usage:"
echo "tfsumpy plan.json --output markdown --ai openai YOUR_API_KEY" 