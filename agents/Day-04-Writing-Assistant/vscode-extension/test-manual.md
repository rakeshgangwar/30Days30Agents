# Manual Testing Guide for Writing Assistant VS Code Extension

This document outlines the steps for manually testing the Writing Assistant VS Code extension.

## Prerequisites

1. Ensure the Writing Assistant backend service is running at http://localhost:8000
2. VS Code is installed
3. The extension is built and installed in VS Code

## Test Setup

1. Open VS Code
2. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Run the "Developer: Install Extension from Location..." command
4. Select the `agents/Day-04-Writing-Assistant/vscode-extension` directory
5. Reload VS Code when prompted

## Test Cases

### 1. Command Registration and UI Elements

#### 1.1 Command Registration

- [ ] Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
- [ ] Type "Writing Assistant"
- [ ] Verify the following commands are available:
  - [ ] Writing Assistant: Draft with AI
  - [ ] Writing Assistant: Analyze Grammar & Style
  - [ ] Writing Assistant: Summarize Text
  - [ ] Writing Assistant: Adjust Tone
  - [ ] Writing Assistant: Preferences
  - [ ] Writing Assistant: Open Panel

#### 1.2 Context Menu

- [ ] Open a text file
- [ ] Right-click in the editor
- [ ] Verify the "Writing Assistant" submenu is available
- [ ] Verify all commands are available in the submenu

#### 1.3 Toolbar Buttons

- [ ] Open a text file
- [ ] Verify the Writing Assistant toolbar buttons are visible in the editor title bar
- [ ] Verify clicking each button triggers the corresponding command

#### 1.4 Keyboard Shortcuts

- [ ] Open a text file
- [ ] Test the following keyboard shortcuts:
  - [ ] Ctrl+Alt+D / Cmd+Alt+D for Draft with AI
  - [ ] Ctrl+Alt+A / Cmd+Alt+A for Analyze Grammar & Style
  - [ ] Ctrl+Alt+S / Cmd+Alt+S for Summarize Text
  - [ ] Ctrl+Alt+T / Cmd+Alt+T for Adjust Tone
  - [ ] Ctrl+Alt+P / Cmd+Alt+P for Preferences

### 2. Core Functionality

#### 2.1 Draft with AI

- [ ] Open a text file
- [ ] Run the "Writing Assistant: Draft with AI" command
- [ ] Enter a prompt (e.g., "Write a paragraph about artificial intelligence")
- [ ] Verify the draft is generated and displayed in a new editor
- [ ] Test with selected text as context
- [ ] Verify the draft incorporates the context

#### 2.2 Analyze Grammar & Style

- [ ] Open a text file with some text
- [ ] Select the text
- [ ] Run the "Writing Assistant: Analyze Grammar & Style" command
- [ ] Verify the analysis is generated and displayed in a new editor
- [ ] Check that issues are properly formatted and categorized
- [ ] Verify the improved text is included

#### 2.3 Summarize Text

- [ ] Open a text file with a long paragraph
- [ ] Select the text
- [ ] Run the "Writing Assistant: Summarize Text" command
- [ ] Select a format (Paragraph or Bullet Points)
- [ ] Verify the summary is generated and displayed in a new editor
- [ ] Check that the summary format matches the selected format

#### 2.4 Adjust Tone

- [ ] Open a text file with some text
- [ ] Select the text
- [ ] Run the "Writing Assistant: Adjust Tone" command
- [ ] Select a tone (e.g., Professional, Casual, etc.)
- [ ] Verify the adjusted text is generated
- [ ] Test both options: "Replace Selected Text" and "Show in New Editor"
- [ ] Verify the adjusted text matches the selected tone

### 3. Preferences Management

#### 3.1 Open Preferences Panel

- [ ] Run the "Writing Assistant: Preferences" command
- [ ] Verify the preferences panel opens
- [ ] Check that all form fields are displayed correctly

#### 3.2 Set User ID

- [ ] In the preferences panel, enter a user ID
- [ ] Click "Set User ID"
- [ ] Verify a success message is displayed
- [ ] Close and reopen the preferences panel
- [ ] Verify the user ID is persisted

#### 3.3 Save Preferences

- [ ] In the preferences panel, select a preferred model
- [ ] Select a default tone
- [ ] Click "Save Preferences"
- [ ] Verify a success message is displayed
- [ ] Check that the VS Code settings are updated
- [ ] Verify the preferences are used in subsequent commands

#### 3.4 Load Preferences from Server

- [ ] Change some preferences in the panel
- [ ] Click "Load from Server"
- [ ] Verify the preferences are loaded from the server
- [ ] Verify the form fields are updated with the loaded preferences

### 4. Result Display

#### 4.1 Text Editor Display

- [ ] Set the result display mode to "editor" in VS Code settings
- [ ] Run any command that generates output
- [ ] Verify the result is displayed in a text editor
- [ ] Check that the content is properly formatted with Markdown

#### 4.2 Webview Display

- [ ] Set the result display mode to "webview" in VS Code settings
- [ ] Run any command that generates output
- [ ] Verify the result is displayed in a webview panel
- [ ] Check that the content is properly formatted with HTML
- [ ] Test the "Copy to Clipboard" and "Insert into Editor" buttons

### 5. Error Handling

#### 5.1 Backend Unavailable

- [ ] Stop the backend service
- [ ] Run any command that requires the backend
- [ ] Verify an appropriate error message is displayed
- [ ] Check that the extension doesn't crash

#### 5.2 Invalid Inputs

- [ ] Run the "Draft with AI" command with an empty prompt
- [ ] Verify appropriate handling (either prevent submission or show error)
- [ ] Run commands that require selected text without selecting any text
- [ ] Verify appropriate warning messages are displayed

#### 5.3 API Errors

- [ ] Modify the API URL to an invalid one in VS Code settings
- [ ] Run any command that requires the backend
- [ ] Verify an appropriate error message is displayed
- [ ] Check that the error message includes useful information

## Test Results

Document any issues found during testing:

1. Issue: [Description]
   - Steps to reproduce: [Steps]
   - Expected behavior: [Expected]
   - Actual behavior: [Actual]
   - Severity: [High/Medium/Low]

## Debugging Tips

- Check the VS Code Developer Tools (Help > Toggle Developer Tools)
- Look for console logs and errors
- Check the VS Code Output panel for extension logs
- Verify network requests to the backend service
