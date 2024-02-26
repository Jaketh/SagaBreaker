import * as dotenv from 'dotenv';
dotenv.config();
import { generateAndSavePlotOutline } from './src/workflow/plotOutline'; // Adjust the path as necessary

async function main() {
  try {
    await generateAndSavePlotOutline();
  } catch (error) {
    console.error("An error occurred:", error);
  }
}

main();
