import fs from 'fs/promises';
import path from 'path';
import { askQuestion } from '../utils/inputPrompter';
import { generateText } from '../api/openAI';
import { writeContentToFile } from '../utils/filewriter';


export async function generateAndSaveChapterSummaries(): Promise<void> {
    try {
      // Prompt the user for the number of chapters
      const chapterCount = await askQuestion("How many chapters would you like the story to have? ");
      const numChapters = parseInt(chapterCount, 10);
  
      if (isNaN(numChapters) || numChapters <= 0) {
        throw new Error("Please enter a valid number of chapters.");
      }
  
      // Read the plot outline from the file
      const plotOutlinePath = path.join(__dirname, '..', '..', 'output', 'plot-outline.txt');
      
      const plotOutline = await fs.readFile(plotOutlinePath, 'utf8');
  
      let chapterSummaries = `Chapter Summaries for ${numChapters} Chapters:\n\n`;
  
      // Loop to generate a summary for each chapter
      for (let chapter = 1; chapter <= numChapters; chapter++) {
        // Generate chapter summary (This is a simplified example. Adjust the prompt as needed.)
        const chapterSummary = await generateText(`Generate a summary for Chapter ${chapter} based on the plot outline:`, plotOutline);
        chapterSummaries += `Chapter ${chapter}: ${chapterSummary}\n\n`;
      }
  
      // Write all chapter summaries to a file
      const chapterSummariesPath = path.join(__dirname, '..', 'output', 'chapter-summaries.txt');
      await writeContentToFile(chapterSummaries, chapterSummariesPath);
  
      console.log("Chapter summaries generated and saved to chapter-summaries.txt.");
    } catch (error) {
      console.error("An error occurred in generating and saving the chapter summaries:", error);
      throw error;
    }
  }
  