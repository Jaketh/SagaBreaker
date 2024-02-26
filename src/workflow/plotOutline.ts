import { generateText } from '../api/openAI'; 
import { writeContentToFile } from '../utils/filewriter'; 
import { askQuestion } from '../utils/inputPrompter';

/**
 * Prompts the user for a novel summary, generates a plot outline based on that summary,
 * and saves the plot outline to a file.
 */
export async function generateAndSavePlotOutline(): Promise<void> {
  try {
    // Prompt the user for a novel summary
    const novelSummary = await askQuestion("Enter your novel's summary: ");

    const plotPrompt = "Generate a plot outline based on the following novel summary: ";
    
    // Use the summary to generate a plot outline
    const plotOutline = await generateText(plotPrompt, novelSummary);

    // Save the generated plot outline to a file
    await writeContentToFile(plotOutline, 'plot-outline.txt');

    console.log("Plot outline generated and saved to plot-outline.txt.");
  } catch (error) {
    console.error("An error occurred in generating and saving the plot outline:", error);
    throw error; // Rethrow the error to handle it in the caller if necessary
  }
}
