// consoleUtils.ts
// This file will contain utilities for interacting with the console, such as reading input from the user or writing output to the console. This can help abstract away direct readline usage and make the console interactions more testable and reusable.

// askQuestion(question: string): Promise<string>
// Description: Prompts the user with a question and returns their input as a string.
// Parameters:
// question: The question to prompt the user with.
// Returns: A promise that resolves to the user's input.