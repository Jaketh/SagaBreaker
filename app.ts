import dotenv from 'dotenv';
dotenv.config(); // Ensure this is at the top to load environment variables

import { generateText } from './src/api/openAI'; // Adjust the import path as necessary

async function main() {
  try {
    const prompt = "Tell me a joke about AI."; // Example prompt
    const generatedText = await generateText(prompt);
    console.log("Generated Text:", generatedText);
  } catch (error) {
    console.error("An error occurred:", error);
  }
}

main();