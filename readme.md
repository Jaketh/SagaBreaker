# SagaBreaker

SagaBreaker is a small attempt at blending the art of storytelling with the science of artificial intelligence. Built with the OpenAI API, this project is my currently underwhelming contribution to the world of novel writing. Everyone has a great story inside them, they just don't have time to write a novel.

## What is SagaBreaker?

SagaBreaker is a simple tool that leverages the capabilities of AI to help writers quickly generate plot outlines and chapter summaries. The goal thought is that with GPT-4 Turbo's new 128k context that it should be now capable of holding multiple chapters within context at the same time. By having chapter summaries, think cliff notes, available to reference in context it should be able to compose a novel and minimize inconsistencies.

I'm also hoping to build in some recursive 'consistency checker' functionality that proofreads sections of the novel while other chapters are loaded into context and makes notes about recommended changes.

## Features

- **Plot Outline Generation**: Give us a glimpse of your story idea, and let SagaBreaker sketch out a basic plot outline for you.
- **Chapter Summaries**: With a plot outline in hand, SagaBreaker can also help outline what happens in individual chapters, helping you see your story's path more clearly.
- **Interactive Console**: Everything happens in a straightforward console application, where you're in control of the inputs and can guide the direction of the generation.

## Getting Started

If you're going to try SagaBreaker, you'll need Node.js and an OpenAI API key. Here's how to set things up:

### Prerequisites

- Node.js installed on your computer.
- An OpenAI API key, which you can get by signing up with OpenAI.

### Installation

1. First, clone this repository to a place where you like to keep projects:

```bash
git clone https://github.com/yourusername/SagaBreaker.git
cd SagaBreaker

npm install
```
Create a .env file in the project's root directory and add your OpenAI API key there:

```
OPENAI_API_KEY=your_openai_api_key_here
```

To get it going:
```
npm start
```