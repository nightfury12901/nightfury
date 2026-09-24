import os
import json
import re
from groq import Groq
from brain.tools import open_application, create_word_document, create_powerpoint, generate_flowchart_image, run_terminal_command, write_code_file, send_whatsapp_message, draft_email, build_antigravity_project, analyze_screen
from config import GROQ_API_KEY

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    client = None

# Global conversation history (keeps last 10 messages max)
conversation_history = [
    {
        "role": "system",
        "content": "You are Jarvis, an advanced AI voice assistant. You control the user's Windows computer using the provided tools. If they ask to build a full project or app, use write_code_file MULTIPLE times. When building websites, ALWAYS use Tailwind CSS and modern stunning designs with animations. For documents, use create_word_document and utilize rich sections. For flowcharts, use generate_flowchart_image. For presentations, use create_powerpoint and provide descriptive image_prompts for stunning AI backgrounds. CRITICAL: NEVER use markdown formatting (like **bold**) inside JSON tool arguments or JSON keys, output pure JSON. Be brief and professional."
    }
]

def match_local_intent(text: str):
    """
    Very simple keyword/regex matching for local, fast tasks.
    Returns the string response if handled locally, else None.
    """
    text_lower = text.lower()
    
    # 1. Open Application Intent
    # Only process locally if it's a short command (less than 6 words) 
    # to avoid intercepting complex instructions like "open word and write a story"
    if len(text_lower.split()) < 6:
        open_match = re.search(r'\b(open|start|launch)\b\s+(.*)', text_lower)
        if open_match:
            # Extract everything after the open/start/launch word
            app = open_match.group(2).strip()
            # Clean up common punctuation and extra words like "the"
            app = app.replace('.', '').replace('?', '').replace('the ', '')
            
            # Simple map for common apps
            app_map = {
                'calculator': 'calc',
                'notepad': 'notepad',
                'chrome': 'chrome',
                'browser': 'chrome',
                'spotify': 'spotify:',
                'whatsapp': 'whatsapp:',
                'word': 'winword',
                'powerpoint': 'powerpnt',
                'excel': 'excel',
                'cmd': 'cmd',
                'terminal': 'cmd'
            }
            
            # Try to find a mapped app anywhere in the extracted text
            for key, value in app_map.items():
                if key in app:
                    return open_application(value)
                    
            # Fallback: if it's just one word left, try it
            if len(app.split()) == 1:
                return open_application(app)
            
    # 2. Tell Time Intent
    if 'time' in text_lower and ('what' in text_lower or 'tell' in text_lower):
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
            
    return None

def process_command(text: str) -> str:
    print(f"Jarvis Brain Processing: '{text}'")
    
    # 1. Try local execution first
    local_response = match_local_intent(text)
    if local_response:
        return local_response
        
    # 2. Fallback to Cloud (Groq) for complex tasks and tool usage
    return call_groq_agent(text)

def call_groq_agent(text: str) -> str:
    if not client:
        return "My Groq API key is missing or invalid. Please check the .env file."
        
    print("Jarvis Brain: Delegating to Groq API...")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_word_document",
                "description": "Create a beautifully styled Word document and open it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "The title or topic of the document"},
                        "template_path": {"type": "string", "description": "Optional absolute path to a .docx template provided by the user. Leave empty if none."},
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "content": {"type": "string"},
                                    "image_path": {"type": "string", "description": "Optional absolute path to an image (e.g. from generate_flowchart_image) to insert in this section"}
                                }
                            }
                        }
                    },
                    "required": ["topic", "sections"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_powerpoint",
                "description": "Create a PowerPoint presentation and open it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "The main title/topic of the presentation"},
                        "template_path": {"type": "string", "description": "Optional absolute path to a .pptx template provided by the user. Leave empty if none."},
                        "slides": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "points": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "image_prompt": {"type": "string", "description": "Optional detailed prompt for an AI image generator to fetch a stunning background/illustration for this slide."}
                                },
                                "required": ["title", "points"]
                            },
                            "description": "List of slides with their titles, bullet points, and optional image prompts"
                        }
                    },
                    "required": ["topic", "slides"]
                }
            }
        },

        {
            "type": "function",
            "function": {
                "name": "open_application",
                "description": "Open a local application or program on Windows.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Name of the app (e.g. notepad, calc, winword, chrome)"}
                    },
                    "required": ["app_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_terminal_command",
                "description": "Execute any arbitrary PowerShell or CMD command on the user's computer. Use this for ANY task that can be accomplished via the command line (e.g. file manipulation, opening settings, running scripts, getting system info).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The exact PowerShell command to run."}
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_flowchart_image",
                "description": "Generate a stunning PNG flowchart or diagram using Mermaid code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mermaid_code": {"type": "string", "description": "The raw Mermaid JS diagram code (e.g. graph TD; A-->B;)"},
                        "filename": {"type": "string", "description": "The name to save the PNG as (default flowchart.png)"}
                    },
                    "required": ["mermaid_code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_code_file",
                "description": "Creates a single local file (e.g., HTML, Python, text) with the specified code or text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "The name of the file to create (e.g. index.html, script.py)"},
                        "content": {"type": "string", "description": "The full code or text content to put in the file"}
                    },
                    "required": ["filename", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_whatsapp_message",
                "description": "Send a WhatsApp message to a specific phone number using the desktop app.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone": {"type": "string", "description": "The phone number including country code (e.g., +1234567890)"},
                        "text": {"type": "string", "description": "The message to send"}
                    },
                    "required": ["phone", "text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "draft_email",
                "description": "Draft an email in Gmail in the default browser.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "The recipient's email address"},
                        "subject": {"type": "string", "description": "The subject of the email"},
                        "body": {"type": "string", "description": "The body of the email"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "build_antigravity_project",
                "description": "Create a new project folder and use the Antigravity CLI (agy) to automatically scaffold and build the requested project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "A short, folder-friendly name for the project (e.g. 'TodoApp')"},
                        "prompt": {"type": "string", "description": "The full, detailed plain-English instructions of what to build"}
                    },
                    "required": ["project_name", "prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_screen",
                "description": "See what is currently on the user's screen and answer questions or extract information from it.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The specific question or prompt about what to look for on the screen"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    global conversation_history
    
    # Append the user's new message to history
    conversation_history.append({"role": "user", "content": text})
    
    # Truncate history if it gets too long (keep system prompt + last 10 interactions)
    if len(conversation_history) > 11:
        conversation_history = [conversation_history[0]] + conversation_history[-10:]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=conversation_history,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                # Strip hallucinated markdown bolding from JSON keys
                args_str = tool_call.function.arguments.replace("**", "")
                function_args = json.loads(args_str)
                
                if function_name == "create_word_document":
                    tool_response = create_word_document(function_args.get("topic"), function_args.get("sections"), function_args.get("template_path"))
                elif function_name == "create_powerpoint":
                    tool_response = create_powerpoint(function_args.get("topic"), function_args.get("slides"), function_args.get("template_path"))
                elif function_name == "generate_flowchart_image":
                    tool_response = generate_flowchart_image(function_args.get("mermaid_code"), function_args.get("filename", "flowchart.png"))
                elif function_name == "open_application":
                    tool_response = open_application(function_args.get("app_name"))
                elif function_name == "run_terminal_command":
                    tool_response = run_terminal_command(function_args.get("command"))
                elif function_name == "write_code_file":
                    tool_response = write_code_file(function_args.get("filename"), function_args.get("content"))
                elif function_name == "send_whatsapp_message":
                    tool_response = send_whatsapp_message(function_args.get("phone"), function_args.get("text"))
                elif function_name == "draft_email":
                    tool_response = draft_email(function_args.get("to"), function_args.get("subject"), function_args.get("body"))
                elif function_name == "build_antigravity_project":
                    tool_response = build_antigravity_project(function_args.get("project_name"), function_args.get("prompt"))
                elif function_name == "analyze_screen":
                    tool_response = analyze_screen(function_args.get("query"))
                else:
                    tool_response = "Unknown tool called."
                    
                # We could send the tool_response back to the LLM to get a final conversational response,
                # but for speed in a voice assistant, we can just return a simple confirmation.
                
                # Update history with the action we took
                conversation_history.append({"role": "assistant", "content": f"I executed a tool and got this result: {tool_response}"})
                return f"I have executed the command. {tool_response}"
                
        # Update history with AI's conversational response
        conversation_history.append({"role": "assistant", "content": response_message.content})
        return response_message.content

    except Exception as e:
        return f"Sorry, I encountered an error in my brain: {e}"
