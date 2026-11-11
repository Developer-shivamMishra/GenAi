import OpenAI from "openai";
import { exec } from 'node:child_process';
import dotenv from "dotenv";
import * as readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
dotenv.config();

const apiKey = process.env.OPENAI_API_KEY;
const  getWeather = async (city) => {
    return `The weather in ${city} is 20 degrees celsius`;
}


const executeCommand = async (command) => {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) reject(error);
            resolve({stdout, stderr});
        });
    });
}
const tools = {
    getWeather: getWeather,
    executeCommand: executeCommand,
}
const client = new OpenAI({ apiKey });

const system_prompt = `

You are a  helpful assistant that can resolve a user query.
You work on  START, THINK , ACTION, OBSERVE and OUTPUT mode.

in the START mode, you will be given a user query and you will need to start the process of resolving the query.
Then you think about the query and then you take an action. think atleast 3 times before taking an action.
It there is need to call a tool, you will need to call the tool and then you will need to observe the result of the tool call.
If there  is action called OBSERVE, you will need to observe the result of the action.
Based on the OBSERVE previous step, you either output the result or repeat the loop.

Rules:
 - Always  wait  for next step.
 - Always output the single step before taking the next step.
 - Output  must be  strictly JSON format.
 - Always use the Available tools to resolve the query.
 - Strictly follow the output  in JSON format.

Available tools:
- getWeather(city: string): string
- executeCommand(command): string execute  a given linux command on user's device and return  the STDOUT and STDERR

Example:
START: What is the weather in Tokyo?
THINK: The user is  asking for the weather in Tokyo. I need to call the getWeather tool to get the weather in Tokyo.
THINK: From the available tools,  I will call the getWeather tool to get the weather in Tokyo.
ACTION:  Call  tool getWeather(tokyo)
OBSERVE: The weather in Tokyo is 20 degrees Celsius.
THINK: The weather in Tokyo is 20 degrees Celsius. 
OUTPUT: Hey ,the weather in Tokyo is 20 degrees Celsius which is quite warm.

output example:
{"role:"user", "content":"What is the weather in Tokyo?"}
{"role:"think", "content":"The user is  asking for the weather in Tokyo. I need to call the getWeather tool to get the weather in Tokyo."}
{role:think", "content":"From the available tools,  I will call the getWeather tool to get the weather in Tokyo."}
{role:action", "tool":"Call  tool getWeather(tokyo),  input: "tokyo"}
{role:observe", "content":"The weather in Tokyo is 20 degrees Celsius."}
{role:think", "content":"The weather in Tokyo is 20 degrees Celsius. "}
{role:output", "content":"Hey ,the weather in Tokyo is 20 degrees Celsius which is quite warm."}

output format:
{
    "step": "string",
    "content": "string",
    "tool": "string",
    "input": "string",
    "output": "string"
}
`

async function init() {
    const rl = readline.createInterface({ input, output });

    while (true) {
        const user_query = (await rl.question("You> ")).trim();
        if (user_query.toLowerCase() === "q") {
            rl.close();
            break;
        }

    const messages = [
        {
            role: "system",
            content: system_prompt,
        },
    ]
    
    messages.push({"role": "user", "content": user_query})
    
    while (true) {
        const response = await client.chat.completions.create({
            model: "gpt-5.2-2025-12-11",
            response_format: {
                type: "json_object",
            },
            messages: messages,
    
        })
        messages.push({"role": "assistant", "content": response.choices[0].message.content})
        const  parsed_response = JSON.parse(response.choices[0].message.content)
    
        if(parsed_response.step  && parsed_response.step === "think"){
            console.log(`🧠 ${parsed_response.content}`);
            continue;
        }
        if(parsed_response.step  && parsed_response.step === "output"){
            console.log(`� ${parsed_response.content}`);
            break;
        }
        if(parsed_response.step  && parsed_response.step === "action"){
            const tool = parsed_response.tool
            const input = parsed_response.input
            console.log(`🔧 Calling tool ${tool} with input ${input}`);
            
            const result = tools[tool](input)
    
            messages.push({"role": "assistant", "content": JSON.stringify({step: "observe", "content": result})})
            continue;
        }
    }
    }
}
init();