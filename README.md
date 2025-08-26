# ketanji

## Architecture Design

┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐
│                 │     │                  │     │               │
│    MCP Client   │◄────┤  DeepSeek MCP    │◄────┤  DeepSeek API │
│ (Claude Desktop)│─────►     Server       │─────►               │
│                 │     │                  │     │               │
└─────────────────┘     └──────────────────┘     └───────────────┘

## Features

- Runs locally to protect the privacy of your data
- Customizable - add any LLM you want via the "plugins" directory
- View the `plugins/sample.py` file to see an example of how to create a new "plugin" for ketanji
- Currently, the only installed plugin is for chatting with Deepseek via Ollama but there are plans for future implementations. See the [Roadmap](#roadmap) to see what's planned!

## Roadmap

- Add OpenAI plugin
- Add Gemini plugin
- Add LLaMa plugin
- Create plugins with specific functionality (i.e., browsing the web, summarizing documents, organizing & summarizing notes, etc.)
