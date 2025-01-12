const express = require('express');
const path = require('path');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { OpenAI } = require('openai');

dotenv.config(); // Load .env variables

const app = express();
app.use(bodyParser.json()); // Parse JSON body in requests

// Serve static files (HTML, CSS, JS) from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// OpenAI API setup
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

// API route for chatting with OpenAI
app.post('/api/chat', async (req, res) => {
    try {
        const userMessage = req.body.message;
        const response = await openai.completions.create({
            model: 'text-davinci-003',
            prompt: userMessage,
            max_tokens: 150,
            temperature: 0.7,
        });

        const botMessage = response.choices[0].text.trim();
        res.json({ reply: botMessage });
    } catch (error) {
        console.error('Error interacting with OpenAI API:', error);
        res.status(500).json({ error: 'An error occurred' });
    }
});

// Serve the HTML page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start the server
const port = 3000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
