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

export async function generateText(prompt: string, settings?: object): Promise<string> {
    if (!OPENAI_API_KEY) {
        throw new Error("OpenAI API key is not configured.");
    }
    console.log('generateText ran');
    
    const params = {
        model: "gpt-3.5-turbo",
        messages: [{"role": "user", "content": prompt}], // Use the function's prompt parameter
        temperature: 0.7,
        max_tokens: 150,
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
        if (axios.isAxiosError(error)) {
            console.error("Axios error:", error.message);
            throw new Error(`OpenAI API request failed: ${error.message}`);
        } else {
            console.error("Unexpected error:", error);
            throw new Error("An unexpected error occurred while requesting the OpenAI API.");
        }
    }
}
