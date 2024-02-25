import * as dotenv from 'dotenv';
dotenv.config(); // Ensure this is at the top to load environment variables
import { generateText } from './src/api/openAI';
import { writeContentToFile } from './src/utils/filewriter';
import readline from 'readline';

// Create a readline interface for stdin and stdout
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to ask for user input
function askQuestion(question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (input) => resolve(input));
  });
}

async function main() {
  try {
    // Ask the user for a prompt
    const userPrompt: string = await askQuestion("Enter your prompt: ");
    
    // Pass the user's prompt to the generateText function
    const generatedText = await generateText(userPrompt);
    console.log("Generated Text:", generatedText);
    
    // Write the generated text to a file
    await writeContentToFile(generatedText, 'generated-text.txt');

    // Close the readline interface
    rl.close();
  } catch (error) {
    console.error("An error occurred:", error);
    rl.close(); // Make sure to close the readline interface in case of an error
  }
}

main();
