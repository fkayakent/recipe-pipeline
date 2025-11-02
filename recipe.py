from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# System instructions for the recipe agent
instructions = """
You are a helpful recipe assistant specialized in creating healthy, delicious recipes for women.

You have access to the following tools:
1. generate_recipe: Create a detailed recipe based on ingredients, dietary preferences, and meal type
2. suggest_meal_plan: Suggest a meal plan for a day or week
3. calculate_nutrition: Provide nutritional information for a recipe

When the user asks for a recipe or meal suggestion, you should:
1. First, use the appropriate tool to gather information
2. Then provide a detailed, helpful response

To use a tool, respond with JSON format:
{"tool": "tool_name", "input": {"key": "value"}}

Your responses should include:
- Ingredient list
- Step-by-step instructions
- Cooking time
- Servings
- Nutritional benefits (especially important for women's health)
- Tips and variations

Always be encouraging and supportive. Focus on healthy, balanced meals.
"""

# Initialize conversation memory
memory = [('system', instructions)]

# Initialize the AI model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def generate_recipe(params):
    """
    Generate a recipe based on user requirements
    
    Args:
        params: Dictionary with ingredients, meal_type, dietary_prefs, cooking_time
    """
    ingredients = params.get("ingredients", "common ingredients")
    meal_type = params.get("meal_type", "any meal")
    dietary_prefs = params.get("dietary_prefs", "no restrictions")
    cooking_time = params.get("cooking_time", "30 minutes")
    
    recipe_prompt = f"""
    Create a detailed recipe with these specifications:
    - Available ingredients: {ingredients}
    - Meal type: {meal_type}
    - Dietary preferences: {dietary_prefs}
    - Cooking time: {cooking_time}
    
    Include:
    1. Recipe name
    2. Ingredients list with measurements
    3. Step-by-step instructions
    4. Cooking time and servings
    5. Nutritional benefits for women's health
    6. Tips and variations
    """
    
    return recipe_prompt


def suggest_meal_plan(params):
    """
    Suggest a meal plan
    
    Args:
        params: Dictionary with duration, dietary_prefs, goals
    """
    duration = params.get("duration", "1 day")
    dietary_prefs = params.get("dietary_prefs", "balanced")
    goals = params.get("goals", "general health")
    
    meal_plan_prompt = f"""
    Create a meal plan with these specifications:
    - Duration: {duration}
    - Dietary preferences: {dietary_prefs}
    - Health goals: {goals}
    
    Include breakfast, lunch, dinner, and snacks.
    Focus on women's nutritional needs (iron, calcium, folate, etc.)
    """
    
    return meal_plan_prompt


def calculate_nutrition(params):
    
    recipe = params.get("recipe", "")
    
    nutrition_prompt = f"""
    Provide nutritional information for this recipe:
    {recipe}
    
    Include:
    - Calories per serving
    - Protein, carbs, fats
    - Key vitamins and minerals
    - Benefits for women's health
    """
    
    return nutrition_prompt


def run_agent():
    
    response = llm.invoke(memory)
    content = response.content
    print(content)
    
    print("\n🤖 Agent thinking...\n")
    
    # Check if AI wants to use a tool
    if "tool" in content and "{" in content:
        try:
            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            data = json.loads(json_str)
            
            tool_name = data.get("tool")
            tool_input = data.get("input", {})
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Execute the appropriate tool
            if tool_name == "generate_recipe":
                tool_response = generate_recipe(tool_input)
                memory.append(("system", f"Tool result: {tool_response}"))
                
            elif tool_name == "suggest_meal_plan":
                tool_response = suggest_meal_plan(tool_input)
                memory.append(("system", f"Tool result: {tool_response}"))
                
            elif tool_name == "calculate_nutrition":
                tool_response = calculate_nutrition(tool_input)
                memory.append(("system", f"Tool result: {tool_response}"))
                
            else:
                memory.append(("system", "Invalid tool name"))
            
            # Run agent again to get final answer
            run_agent()
            
        except json.JSONDecodeError:
            # If not valid JSON, treat as regular response
            print(f"\n👩‍🍳 Recipe Assistant: {content}\n")
            memory.append(("assistant", content))
            ask_user()
    else:
        # Regular response without tool use
        print(f"\n👩‍🍳 Recipe Assistant: {content}\n")
        memory.append(("assistant", content))
        ask_user()


def ask_user():
    """
    Get input from user
    """
    user_input = input("You: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("\n👋 Happy cooking! Goodbye!\n")
        exit()
    
    if not user_input:
        print("Please enter a question or request.\n")
        ask_user()
        return
    
    memory.append(('human', user_input))
    run_agent()


# Main program
if __name__ == "__main__":
    print("=" * 60)
    print("👩‍🍳 WOMEN'S RECIPE ASSISTANT")
    print("=" * 60)
    print("Ask me for recipes, meal plans, or nutritional advice!")
    print("Type 'quit' to exit")
    print("=" * 60)
    print()
    
    # Start the conversation
    ask_user()