import * as dotenv from 'dotenv';
dotenv.config();
import readline from 'readline';
import { generateAndSavePlotOutline } from './src/workflow/plotOutline';
import { generateAndSaveChapterSummaries } from './src/workflow/chapterSummaries';

// Create the readline interface at the top level of your application
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Adjust the askQuestion function to use the top-level readline interface
function askQuestion(question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (input) => resolve(input));
  });
}

async function main() {
  try {
    // Your main application logic here
    // For example:
    await generateAndSavePlotOutline(askQuestion);
    // Proceed based on user input or application logic
    const proceed = await askQuestion("Would you like to proceed with generating chapter summaries? (y/n): ");
    if (proceed.toLowerCase() === 'y') {
      await generateAndSaveChapterSummaries(askQuestion); // Pass askQuestion or necessary user inputs to the function
    }
    // Any other logic
  } catch (error) {
    console.error("An error occurred:", error);
  } finally {
    rl.close(); // Ensure the readline interface is closed when done
  }
}

main();
