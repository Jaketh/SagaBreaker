import * as dotenv from 'dotenv';
dotenv.config();
import { promises as fs } from 'fs';
import { generateAndSavePlotOutline } from './src/workflow/plotOutline';
import { generateAndSaveChapterSummaries } from './src/workflow/chapterSummaries'; // Assuming you have this function

const plotOutlineFilePath = './output/plot-outline.txt'; // Ensure the path matches where you're saving the file

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true; // File exists
  } catch {
    return false; // File does not exist
  }
}

async function main() {
  try {
    const plotOutlineExists = await fileExists(plotOutlineFilePath);

    if (!plotOutlineExists) {
      console.log("Plot outline file does not exist. Generating now...");
      await generateAndSavePlotOutline();
    } else {
      console.log("Plot outline file exists. Proceeding to chapter summaries...");
      // Optionally, ask the user if they want to proceed with generating chapter summaries
      // You can use your existing prompt utility here if you want to ask for confirmation
    }

    // Call the function to start the chapter summaries process
    await generateAndSaveChapterSummaries(); // Ensure this function exists and is correctly implemented

  } catch (error) {
    console.error("An error occurred:", error);
  }
}

main();
