import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

interface Message {
    role: string;
    content: string;
}

interface OpenAIResponse {
    choices: {
        index: number;
        message: Message;
        logprobs: null;
        finish_reason: string;
    }[];
}

export async function generateText(prompt: string, userInput: string, settings?: object): Promise<string> {
    if (!OPENAI_API_KEY) {
        throw new Error("OpenAI API key is not configured.");
    }
    console.log('generateText running...');

    // const fullPrompt = `Prompt:${prompt} User Input: ${userInput}`;
    
    const params = {
        model: "gpt-4-turbo-preview",
        messages: [
            {"role": "system", "content": prompt},
            {"role": "user", "content": userInput}
        ],
        temperature: 0.7,
        max_tokens: 4000,
        ...settings,
    };

    try {
        const response = await axios.post<OpenAIResponse>(OPENAI_API_URL, params, {
            headers: {
                'Authorization': `Bearer ${OPENAI_API_KEY}`,
                'Content-Type': 'application/json',
            },
        });

        const generatedText = response.data.choices[0]?.message.content;
        if (!generatedText) {
            throw new Error("No text was returned from the OpenAI API.");
        }
        console.log("Generated Text:", generatedText);
        return generatedText;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            console.error("Axios error:", error.response.data); // This might contain more detailed error information
            throw new Error(`OpenAI API request failed: ${error.response.data?.error?.message}`);
        } else {
            console.error("Unexpected error:", error);
            throw new Error("An unexpected error occurred while requesting the OpenAI API.");
        }
    }
}
