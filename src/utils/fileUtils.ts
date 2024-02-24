// This file will handle all file operations, such as reading from and writing to files. This centralizes file handling logic, making it easier to implement changes or add new file-related functionalities.

// writeToFile(fileName: string, content: string): Promise<void>

// Description: Writes content to a file, overwriting the file if it exists or creating it if it does not.
// Parameters:
// fileName: The name (and path) of the file to write to.
// content: The content to write to the file.
// Returns: A promise that resolves when the file has been written.
// appendToFile(fileName: string, content: string): Promise<void>

// Description: Appends content to a file, creating the file if it does not exist.
// Parameters:
// fileName: The name (and path) of the file to append to.
// content: The content to append to the file.
// Returns: A promise that resolves when the content has been appended.
// readFromFile(fileName: string): Promise<string>

// Description: Reads content from a file.
// Parameters:
// fileName: The name (and path) of the file to read from.
// Returns: A promise that resolves to the content of the file.