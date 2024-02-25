const fs = require('fs').promises;
const path = require('path');

/**
 * Writes content to a specified file. If the file doesn't exist, it's created.
 * @param {string} content - The content to write to the file.
 * @param {string} filename - The name of the file (with extension).
 */
export async function writeContentToFile(content: string, filename: string) {
  // Construct the file path to point to the output directory in the project root
  const filePath = path.join(__dirname, '..', '..', 'output', filename);
  try {
    await fs.writeFile(filePath, content, 'utf8');
    console.log(`Content written to ${filename}`);
  } catch (error) {
    console.error(`Failed to write to ${filename}:`, error);
  }
}