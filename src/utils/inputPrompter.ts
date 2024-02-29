import readline from 'readline';

// Set up readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * Prompts the user with a question and returns their input as a string.
 * @param {string} question The question to prompt the user with.
 * @returns {Promise<string>} The user's input.
 */

export function askQuestion(question: string): Promise<string> {
    return new Promise((resolve) => {
      rl.question(question, (input) => resolve(input));
    });
  }
  