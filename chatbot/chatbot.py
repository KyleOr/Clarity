import os
import json
import hashlib
from model_processor import generate_response, get_available_models, set_model, SELECTED_MODEL, initialize_chatbot

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "input")
output_dir = os.path.join(base_dir, "output")
context_input_dir = os.path.join(base_dir, "context_input")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def load_page_context(url: str) -> dict:
    """Load context data for a specific URL"""
    try:
        # Generate URL hash to match context file naming
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        context_file = os.path.join(context_input_dir, f"context_{url_hash}.json")
        
        if os.path.exists(context_file):
            with open(context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Try to find context by URL matching
            if os.path.exists(context_input_dir):
                for filename in os.listdir(context_input_dir):
                    if filename.startswith("context_") and filename.endswith(".json"):
                        try:
                            with open(os.path.join(context_input_dir, filename), 'r', encoding='utf-8') as f:
                                context_data = json.load(f)
                                if context_data.get('page_info', {}).get('url') == url:
                                    return context_data
                        except Exception:
                            continue
    except Exception as e:
        print(f"⚠️ Error loading page context: {e}")
    
    return {}

def load_analysis_data():
    """Load analysis data from Clarity results"""
    # This will be updated to load from Clarity fact-check results
    # For now, return empty to avoid errors
    print("📊 No analysis data loaded yet - will be integrated with Clarity results")
    return {}

def load_system_prompt():
    """Load the system prompt from prompt.txt"""
    try:
        prompt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("⚠️ prompt.txt not found, using fallback prompt")
        return """You are Clarity, an AI assistant specialized in digital safety, cybersecurity education, and misinformation detection. You help users navigate the digital world safely and make informed decisions about online content."""

def create_clarity_prompt(context, user_question):
    """Create the full prompt for the Clarity AI assistant"""
    system_prompt = load_system_prompt()
    
    # Format context information
    context_info = ""
    analysis_context = {}
    
    if context:
        if isinstance(context, dict):
            # Extract URL for context loading
            url = context.get('url')
            if url:
                analysis_context = load_page_context(url)
            
            # Build context information
            if context.get('url'):
                context_info += f"Current Page: {context['url']}\n"
            if context.get('title'):
                context_info += f"Page Title: {context['title']}\n"
            if context.get('content'):
                # Limit content to prevent prompt overflow
                content = context['content'][:1000] + "..." if len(context['content']) > 1000 else context['content']
                context_info += f"Page Content: {content}\n"
            
            # Add rich analysis context if available
            if analysis_context:
                context_info += "\n--- CLARITY ANALYSIS ---\n"
                
                # Add talking points
                talking_points = analysis_context.get('key_talking_points', [])
                if talking_points:
                    context_info += "Key Points:\n"
                    for point in talking_points[:5]:  # Limit to top 5 points
                        context_info += f"• {point}\n"
                
                # Add credibility assessment
                credibility = analysis_context.get('credibility_assessment', {})
                if credibility:
                    rating = credibility.get('overall_rating', 'unknown')
                    total_claims = credibility.get('total_claims_analyzed', 0)
                    suspicious = credibility.get('suspicious_claims', 0)
                    context_info += f"Credibility: {rating.upper()} ({total_claims} claims, {suspicious} suspicious)\n"
                
                # Add security assessment
                security = analysis_context.get('security_assessment', {})
                if security:
                    risk = security.get('overall_risk_level', 'unknown')
                    threats = security.get('total_threats', 0)
                    context_info += f"Security Risk: {risk.upper()} ({threats} threats detected)\n"
                
                # Add actionable advice
                advice = analysis_context.get('actionable_advice', [])
                if advice:
                    context_info += "Recommendations:\n"
                    for rec in advice[:3]:  # Limit to top 3 recommendations
                        context_info += f"• {rec}\n"
                
                # Add educational opportunities
                education = analysis_context.get('educational_opportunities', [])
                if education:
                    context_info += "Educational Topics:\n"
                    for topic in education[:2]:  # Limit to top 2 topics
                        context_info += f"• {topic}\n"
            
        else:
            context_info = str(context)[:1500] + "..." if len(str(context)) > 1500 else str(context)

    full_prompt = f"""{system_prompt}

CURRENT CONTEXT:
{context_info if context_info else "No specific page context available."}

USER QUESTION: {user_question}

RESPONSE (Be helpful, educational, and focused on digital safety):"""

    return full_prompt

def generate_chat_response(user_question: str, analysis_context: str = "") -> str:
    """Generate a response for the Clarity chatbot"""
    
    if not SELECTED_MODEL:
        if not initialize_chatbot():
            return "❌ Chatbot not properly initialized. Please check model setup."
    
    # Create the prompt
    prompt = create_clarity_prompt(analysis_context, user_question)
    
    # Generate response with appropriate settings for conversational AI
    response = generate_response(prompt, n_tokens=300, temperature=0.8)
    
    # Clean the response more thoroughly
    if "RESPONSE:" in response:
        response = response.split("RESPONSE:", 1)[1].strip()
    
    if "RESPONSE (Be helpful" in response:
        response = response.split("RESPONSE (Be helpful", 1)[0].strip()
    
    # Remove any prompt echoes or system messages
    lines = response.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip lines that look like prompt fragments or system messages
        if not (line.startswith("USER QUESTION:") or 
               line.startswith("You are Clarity") or
               line.startswith("Your role is") or
               line.startswith("CURRENT CONTEXT:") or
               line.startswith("ANALYSIS CONTEXT:") or
               line.startswith("RESPONSE:") or
               line.startswith("Page Content:") or
               line.startswith("Current Page:") or
               line.startswith("Page Title:") or
               "specialized in digital safety" in line or
               "Clarity Analysis:" in line or
               line == "" or
               line.startswith("Be helpful")):
            cleaned_lines.append(line)
    
    response = '\n'.join(cleaned_lines).strip()
    
    # Remove any remaining prompt artifacts and model artifacts
    response = response.replace("CURRENT CONTEXT:", "").strip()
    response = response.replace("USER QUESTION:", "").strip()
    response = response.replace("[end of text]", "").strip()
    
    # Ensure we have a reasonable response
    if len(response) < 30:
        return "Hello! I'm Clarity, your digital safety assistant. I'm here to help you understand online content, identify potential misinformation, and stay safe while browsing. What would you like to know about this page or digital safety in general?"
    
    # Ensure response doesn't end mid-sentence
    if response and not response.endswith(('.', '!', '?', ':', ';')):
        # Find the last complete sentence
        sentences = response.split('.')
        if len(sentences) > 1:
            response = '.'.join(sentences[:-1]) + '.'
    
    return response

def test_chatbot():
    """Test function to verify chatbot is working"""
    print("🤖 Testing Clarity Chatbot...")
    
    if not initialize_chatbot():
        print("❌ Failed to initialize chatbot")
        return False
    
    # Test with a simple question
    test_question = "Hello! What can you help me with?"
    print(f"\n🔍 Test Question: {test_question}")
    
    response = generate_chat_response(test_question)
    print(f"\n🤖 Response: {response}")
    
    # Test with context from the property update page
    print(f"\n🔍 Testing with rich context from property analysis...")
    test_context = {
        'url': 'https://propertyupdate.com.au/australian-property-market/',
        'title': 'This week\'s Australian Property Market Update',
        'content': 'Property market analysis with data about housing prices, government schemes, and market trends...'
    }
    context_question = "What should I know about the security and credibility of this property market information?"
    
    context_response = generate_chat_response(context_question, test_context)
    print(f"\n🤖 Context Response: {context_response}")
    
    return True

if __name__ == "__main__":
    test_chatbot()
