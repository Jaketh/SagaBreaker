const fs = require('fs').promises;
const path = require('path');

/**
 * Writes content to a specified file path. If the file doesn't exist, it's created, along with any necessary directories.
 * @param {string} content - The content to write to the file.
 * @param {string} filePath - The full path to the file (including the filename and extension).
 */
export async function writeContentToFile(content: string, filePath: string) {
  try {
    // Ensure the directory exists
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    // Write the file
    await fs.writeFile(filePath, content, 'utf8');
    console.log(`Content written to ${filePath}`);
  } catch (error) {
    console.error(`Failed to write to ${filePath}:`, error);
    throw error; // Re-throw the error for further handling if necessary
  }
}