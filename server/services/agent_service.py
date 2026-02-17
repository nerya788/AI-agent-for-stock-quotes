from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from server.services.agent_tools import get_stock_price, check_my_portfolio
from server.models.agent_dto import AgentResponse

class AgentService:
    def __init__(self):
        print("🤖 Initializing AgentService with model: llama3.2:1b")
        
        # model="llama3.2:1b" - ודא שזה השם המדויק ב-Ollama שלך
        self.llm = OllamaLLM(model="llama3.2:1b", temperature=0)
        self.tools = [get_stock_price, check_my_portfolio]
        self.user_memories = {}

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

        IMPORTANT rules for Llama 3:
        1. Do NOT write "Action: tool_name(arg)". This is WRONG.
        2. Write "Action: tool_name" on one line, and "Action Input: arg" on the next line.
        3. Do NOT use quotes or brackets in the Action name.
        4. If the user asks for a general plan, your Final Answer MUST be: <<OPEN_INVESTMENT_FORM>>
        5. If you confirm a buy, your Final Answer MUST be: <<CONFIRM_BUY:SYMBOL,AMOUNT,PRICE>>

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

    def _handle_parsing_error(self, error) -> str:
        """פונקציית עזר: אם המודל מתבלבל, אנחנו עוזרים לו"""
        response = str(error)
        # אם המודל כתב בטעות קוד פייתון, ננחה אותו לתקן
        if "Could not parse LLM output" in response or "Missing 'Action Input'" in response:
            return "Observation: You used the wrong format. Do not use parentheses '()'. Write 'Action: [tool_name]' and then 'Action Input: [value]' on a new line."
        return f"Observation: Error: {response}"

    def _get_executor_for_user(self, user_id: str):
        memory = self._get_memory_for_user(user_id)
        
        # יצירת ה-Prompt המותאם
        prompt = PromptTemplate.from_template(self.suffix)
        
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

    def process_request(self, user_input: str, user_id: str) -> AgentResponse:
        executor = self._get_executor_for_user(user_id)
        
        # --- התיקון: הזרקת ה-ID לתוך הקלט ---
        # אנחנו אומרים לסוכן במפורש: "הנה ה-ID של המשתמש, תשתמש בו!"
        enhanced_input = (
            f"User Request: {user_input}\n\n"
            "CONTEXT & RULES:\n"
            f"1. My User ID is: {user_id} (Use this ONLY for 'check_my_portfolio').\n"
            "2. For 'get_stock_price', extract the symbol from my request (e.g. Apple -> AAPL, Google -> GOOGL).\n"
            "3. Do NOT use the User ID as a stock symbol."
        )
        
        try:
            result = executor.invoke({"input": enhanced_input})
            raw_output = result["output"]
            
            # --- Parsing ---
            if "<<OPEN_INVESTMENT_FORM>>" in raw_output:
                return AgentResponse(response_type="form", message="Opening form...")
            
            if "<<CONFIRM_BUY:" in raw_output:
                try:
                    clean = raw_output.split("<<CONFIRM_BUY:")[1].split(">>")[0]
                    parts = clean.split(",")
                    return AgentResponse(
                        response_type="trade_confirmation",
                        message=f"Confirm buy: {parts[1]} shares of {parts[0]}",
                        trade_payload={"symbol": parts[0], "amount": int(parts[1]), "price": float(parts[2])}
                    )
                except:
                    pass

            return AgentResponse(response_type="chat", message=raw_output)

        except Exception as e:
            print(f"Agent Error: {e}")
            # במקרה של שגיאת UUID (כמו שראית), נחזיר הודעה יפה
            if "invalid input syntax for type uuid" in str(e):
                return AgentResponse(response_type="chat", message="I tried to check your portfolio but got confused with the User ID. Please try again.")
            
            return AgentResponse(response_type="chat", message="I'm having trouble connecting to my brain right now. Please try again.")