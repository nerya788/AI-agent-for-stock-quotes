import os
from urllib import response
from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from server.services.agent_tools import get_stock_price, identify_intent
from server.models.agent_dto import AgentResponse
from langchain_groq import ChatGroq

USE_CLOUD = False
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AgentService:
    def __init__(self):
        print("🤖 Initializing AgentService with model: llama3.2:1b")
        
        # model="llama3.2:1b" - ודא שזה השם המדויק ב-Ollama שלך
        self.tools = [get_stock_price, identify_intent]
        self.user_memories = {}
        # לוגיקת בחירת מודל
        if USE_CLOUD and ChatGroq:
            print("🚀 Initializing Agent with CLOUD model (Groq Llama 3-8b)")
            self.llm = ChatGroq(
                temperature=0, 
                model_name="llama-3.1-8b-instant", 
                api_key=GROQ_API_KEY
            )
        else:
            print("🐌 Initializing Agent with LOCAL model (Ollama Llama 3)")
            # כאן אנחנו משתמשים בשם הגנרי 'llama3' שיתאים לחברים שלך
            # אצלך זה יכשל אם אין לך llama3, אבל זה בסדר כי אתה ב-USE_CLOUD=True
            self.llm = OllamaLLM(model="llama3", temperature=0)

        # --- 1. PREFIX: הגדרת האישיות (לפני הכלים) ---
        self.prefix = """You are a professional financial advisor assistant. 
                        Your goal is to help the user with stock questions.
                        You have access to the following tools:"""
        
        # --- 2. FORMAT INSTRUCTIONS: החוקים הטכניים (אחרי הכלים) ---
        # שים לב: כאן אין {tools}, רק {tool_names}!
        self.format_instructions = """To use a tool, you MUST use the following format:
        Thought: Do I need to use a tool? Yes
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action

        When you have a response for the Human, or if you do not need to use a tool, you MUST use the format:
        Thought: Do I need to use a tool? No
        Final Answer: [your response here]"""

        # --- 3. SUFFIX: סגירה והיסטוריה ---
        self.suffix = """Begin!

        Previous conversation history:
        {chat_history}

        User Request: {input}
        {agent_scratchpad}"""


    def _get_memory_for_user(self, user_id: str):
        if user_id not in self.user_memories:
            self.user_memories[user_id] = ConversationBufferMemory(
                memory_key="chat_history", 
                return_messages=True
            )
        return self.user_memories[user_id]

    def _get_executor_for_user(self, user_id: str):
        memory = self._get_memory_for_user(user_id)
        
        # שימוש ב-initialize_agent (הכי יציב לגרסה הזאת)
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, # סוג סוכן שמשתמש בזיכרון
            verbose=True,
            memory=memory,
            handle_parsing_errors=self._handle_parsing_error, # חיבור פונקציית התיקון
            max_iterations=3, # מניעת לופ אינסופי (חשוב ל-Timeout!)
            agent_kwargs={
                "prefix": self.prefix,
                "format_instructions": self.format_instructions,
                "suffix": self.suffix
            }
        )

    def _handle_parsing_error(self, error) -> str:
        """
        מנגנון הצלה חכם:
        אם המודל נתן את התשובה הנכונה אבל הפורמט שבר את LangChain,
        אנחנו מחלצים את התשובה מתוך הודעת השגיאה ומחזירים אותה כהצלחה.
        """
        response = str(error)
        
        # 1. התיקון הקריטי: אם התגית נמצאת בתוך השגיאה - הצלנו את המצב!
        if "<<CONFIRM_BUY:" in response or "<<CONFIRM_SELL:" in response:            # אנחנו מחזירים את התגית עצמה, וכך ה-process_request יתפוס אותה
            raise ValueError(f"###STOP_CHAIN_SUCCESS###{response}")
                 
        if "<<OPEN_INVESTMENT_FORM>>" in response:
            raise ValueError("###STOP_CHAIN_FORM###")
        
        if "Final Answer:" in response:
            clean_text = response.split("Final Answer:")[-1].strip().strip("`")
            # זורקים שגיאה יזומה כדי לצאת מהלופ של LangChain
            raise ValueError(f"###STOP_CHAIN_CHAT###{clean_text}")
        
        # 2. אם זו סתם שגיאת פורמט בלי תשובה, ננזוף במודל
        if "Could not parse LLM output" in response:
            return "Observation: Invalid Format. Remember to use 'Action:' and 'Action Input:' on separate lines."
        
        return f"Observation: Invalid Format. You provided: {str(error)[:50]}... Remember to use 'Action:' and 'Action Input:' on separate lines."

    def process_request(self, user_input: str, user_id: str) -> AgentResponse:
        executor = self._get_executor_for_user(user_id)
        
        enhanced_input = (
            f"User Request: {user_input}\n"
            f"Context: My User ID is {user_id}.\n"
            "1. IDENTIFY INTENT:\n"
            "   Identify one of the two intentions, when you identify one of them you will only execute the commands that correspond to it"
            "   - 'Buy/Sell/Trade' -> TRADING.\n"
            "   - 'Plan/Offer/Advise/Suggestion/Recommend/Advice' -> INVESTMENT ADVICE.\n"
            "\n"
            "   --- IF TRADING ---\n"
            "2. Step 1: Use 'get_stock_price' to get the current value.\n"
            "3. RESTRICTION: if the user asks to Buy or Sell. Just execute.\n"
            "4. Step 2: Once price is found -> STOP USING TOOLS IMMEDIATELY.\n"
            "5. Step 3: Output ONLY the confirmation tag based on intent:\n"
            "   - If BUYing  -> Final Answer: <<CONFIRM_BUY:SYMBOL,AMOUNT,PRICE>>\n"
            "   - If SELLing -> Final Answer: <<CONFIRM_SELL:SYMBOL,AMOUNT,PRICE>>\n"
            "   - Example: <<CONFIRM_BUY:AAPL,2,150.5>>\n"
            "   - Example: <<CONFIRM_SELL:TSLA,1,700>>\n"
            "\n"
            "2.   --- IF INVESTMENT ADVICE ---\n"
            "3.   - DO NOT start a conversation. DO NOT ask for details..\n"
            "4.   - Example: <<OPEN_INVESTMENT_FORM>>\n"
        )
        
        try:
            # ניסיון להריץ את הסוכן
            result = executor.invoke({"input": enhanced_input})
            raw_output = result["output"]
            
        except ValueError as e:
            # --- כאן אנחנו תופסים את ה-EJECT שלנו ---
            error_str = str(e)
            if "###STOP_CHAIN_SUCCESS###" in error_str:
                # חילוץ התשובה מתוך ה"שגיאה"
                raw_output = error_str.split("###STOP_CHAIN_SUCCESS###")[1]
            elif "###STOP_CHAIN_FORM###" in error_str:
                return AgentResponse(response_type="form", message="Opening investment form...")
            elif "###STOP_CHAIN_CHAT###" in error_str:
                # מצאנו את הטקסט החופשי - שולחים חזרה למשתמש!
                chat_msg = error_str.split("###STOP_CHAIN_CHAT###")[1]
                return AgentResponse(response_type="chat", message=chat_msg)
            else:
                # זו שגיאה אמיתית, לא ה-Eject שלנו
                print(f"Agent Error: {e}")
                return AgentResponse(response_type="chat", message="I found the price but got stuck. Please try again.")
        except Exception as e:
            print(f"Critical Error: {e}")
            return AgentResponse(response_type="chat", message="System error. Please try again.")

        # --- Parsing של התשובה (בין אם הגיעה רגיל או דרך ה-Eject) ---
        if "<<OPEN_INVESTMENT_FORM>>" in raw_output:
            return AgentResponse(response_type="form", message="Opening investment form...")
        
        if "<<CONFIRM_BUY:" in raw_output:
            try:
                # חילוץ אגרסיבי גם אם יש רעש מסביב
                clean = raw_output.split("<<CONFIRM_BUY:")[1].split(">>")[0]
                parts = clean.split(",")
                
                symbol = parts[0].strip().upper()
                amount = int(parts[1].strip())
                price_str = parts[2].strip().replace("$", "").replace(",", "")
                price = float(price_str)
                
                return AgentResponse(
                    response_type="trade_confirmation",
                    message=f"I found {symbol} at ${price}. Confirm buy?",
                    trade_payload={"symbol": symbol, "amount": amount, "price": price, "side": "buy"}
                )
            except Exception as parse_error:
                print(f"Parsing Tag Error: {parse_error}")
                pass
        
        if "<<CONFIRM_SELL:" in raw_output:
            try:
                clean = raw_output.split("<<CONFIRM_SELL:")[1].split(">>")[0]
                parts = clean.split(",")
                symbol = parts[0].strip().upper()
                amount = int(parts[1].strip())
                price = float(parts[2].strip().replace("$", "").replace(",", ""))
                
                return AgentResponse(
                    response_type="trade_confirmation",
                    message=f"I found {symbol} at ${price}. Confirm SELL?",
                    # הוספתי side: sell
                    trade_payload={"symbol": symbol, "amount": amount, "price": price, "side": "sell"}
                )
            except:
                pass

        if "I will proceed" in raw_output or "The price is" in raw_output:
             return AgentResponse(response_type="chat", message="I found the price. Try saying just 'Buy' to trigger the popup.")

        return AgentResponse(response_type="chat", message=raw_output)