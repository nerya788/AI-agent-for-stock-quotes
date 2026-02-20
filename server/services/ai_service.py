import os
import requests
import json
import re

from langchain_community.llms import Ollama

try:
    from huggingface_hub import InferenceClient
except ImportError:  # huggingface-hub is optional
    InferenceClient = None

# --- Our addition: JSON parser model (Groq) ---
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None


class AIService:
    def __init__(self):
        # Keep the original variables exactly the same
        self.llm = None
        self.is_active = False

        # New: dedicated JSON parser LLM
        self.parser_llm = None

        self.hf_client = None
        self.hf_active = False
        self.hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.hf_translation_model = os.getenv(
            "HF_TRANSLATION_MODEL", "Helsinki-NLP/opus-mt-en-he"
        )

        # 1. Load the local model (lecturer's Llama 3.2)
        try:
            from langchain_ollama import OllamaLLM

            self.llm = OllamaLLM(model="llama3.2:1b")
            self.is_active = True
            print("✅ AI Service initialized (Local Ollama is ready)")
        except ImportError:
            print("⚠️ langchain-ollama not installed. AI Service running in MOCK mode.")
        except Exception as e:
            print(f"⚠️ AI Service warning: {e}. Running in MOCK mode.")

        # 2. Load the smart data parser (Groq Llama 70B)
        groq_key = os.getenv("GROQ_API_KEY")
        if ChatGroq and groq_key:
            try:
                self.parser_llm = ChatGroq(
                    temperature=0.0,  # Temperature 0: no creativity, only extraction
                    model_name="llama-3.3-70b-versatile",
                    api_key=groq_key,
                )
                print("✅ Cloud Parser (Groq 70B) initialized for JSON extraction")
            except Exception as e:
                print(f"⚠️ Groq parser init failed: {e}")

        # 3. Load Hugging Face for news ranking (unchanged)
        try:
            if InferenceClient is not None:
                self.hf_client = (
                    InferenceClient(
                        provider="hf-inference",
                        api_key=self.hf_token,
                    )
                    if self.hf_token
                    else None
                )
                self.hf_active = bool(self.hf_token)
                if self.hf_active:
                    print(
                        "✅ HF Client initialized (token detected) for news AI features"
                    )
                else:
                    print("⚠️ HF token not set – news AI in MOCK mode")
            else:
                print("⚠️ huggingface-hub not installed. News ranking in MOCK mode.")
        except Exception as e:
            print(f"⚠️ HF Client init failed: {e}. News ranking in MOCK mode.")

    def analyze_stock(self, symbol: str, price: float) -> str:
        # Unchanged: uses the local model
        if not self.is_active or not self.llm:
            return (
                f"[MOCK Analysis] The AI service is currently optimized via Docker. "
                f"Mock insight: {symbol} at ${price} shows stable trends. "
                f"Consider market volatility before investing."
            )

        try:
            prompt = f"Analyze the stock {symbol} at {price} USD. Is it risky? Answer in 2 short sentences."
            return self.llm.invoke(prompt)
        except Exception as e:
            print(f"❌ Connection to Ollama failed: {e}")
            return "AI Service is offline. Please check your Docker container."

    def generate_investment_plan(self, prompt: str) -> dict:
        """
        Generate an investment plan: use the local model to write the text and Groq to extract JSON.
        """
        # Ensure the local model (generator) is available
        if not self.is_active or not self.llm:
            return {"plan_text": "⚠️ AI Service is unavailable.", "basket": []}

        try:
            print(
                f"🤖 AI Service: Step 1 - Local AI (Llama 3.2) generating plan text..."
            )

            # --- Step 1: local model writes the plan text (do NOT ask it for JSON) ---
            generator_prompt = (
                "You are an expert financial advisor. "
                "Write a beautifully formatted, personalized investment plan using Markdown, emojis, and clear headings. "
                "CRITICAL RULES FOR STOCKS:\n"
                "1. Recommend ONLY real, well-known, actively traded US market stock ticker symbols (e.g., AAPL, MSFT, TSLA).\n"
                "2. DO NOT invent or hallucinate ticker symbols!\n"
                "3. If the user asks for Israeli market focus, ONLY use US-listed Israeli companies (like TEVA, CHKP, CYBR, NICE, MNDY).\n"
                "4. Specify their exact percentage allocation. The percentages MUST sum to exactly 100%.\n\n"
                f"User Request:\n{prompt}"
            )

            response = self.llm.invoke(generator_prompt)
            plan_text = (
                response.content.strip()
                if hasattr(response, "content")
                else str(response).strip()
            )

            basket_data = []

            # --- Step 2: parser (Groq) reads the text and extracts only JSON ---
            if self.parser_llm:
                print(f"🧠 AI Service: Step 2 - Cloud Parser (Groq) extracting JSON...")
                parser_prompt = (
                    "You are a strict data extraction bot. "
                    "Read the following investment plan and extract ALL recommended stock symbols and their percentages. "
                    "CRITICAL: You MUST extract EVERY SINGLE stock mentioned in the text. Do not leave any out! "
                    "Return ONLY a valid JSON array of objects. Do NOT return any markdown, text, or explanations. "
                    "Use this exact schema for your output:\n"
                    "[\n"
                    '  {"symbol": "AAPL", "percentage": 40},\n'
                    '  {"symbol": "MSFT", "percentage": 30},\n'
                    '  {"symbol": "NVDA", "percentage": 30}\n'
                    "]\n\n"
                    f"PLAN TEXT TO PARSE:\n{plan_text}"
                )

                parser_response = self.parser_llm.invoke(parser_prompt)
                clean_json = (
                    parser_response.content.strip()
                    if hasattr(parser_response, "content")
                    else str(parser_response).strip()
                )

                # Quick Markdown cleanup in case Groq added fences
                clean_json = (
                    clean_json.replace("```json", "").replace("```", "").strip()
                )
                clean_json = re.sub(r",\s*([\]}])", r"\1", clean_json)

                try:
                    basket_data = json.loads(clean_json)
                    print(
                        f"✅ Extracted basket successfully with {len(basket_data)} items."
                    )
                except json.JSONDecodeError as e:
                    print(
                        f"❌ Parser failed to output valid JSON: {e}\nRaw output: {clean_json}"
                    )
            else:
                print("⚠️ No Groq parser available. Basket will be empty.")

            return {"plan_text": plan_text, "basket": basket_data}

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return {"plan_text": f"Error generating plan: {e}", "basket": []}

    def rank_news_for_stock(self, symbol: str, news_items: list[dict]) -> list[dict]:
        # MOCK mode...
        if not self.hf_active or not getattr(self, "hf_token", None):
            ranked = []
            for item in news_items:
                text = f"{item.get('title', '')}. {item.get('summary', '')}"
                score = min(len(text) / 400.0, 1.0)
                enriched = dict(item)
                enriched["importance_score"] = round(float(score), 3)
                ranked.append(enriched)

            ranked.sort(key=lambda x: x["importance_score"], reverse=True)
            return ranked

        ranked_items: list[dict] = []
        api_url = (
            "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
        )
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        labels = ["very important", "somewhat important", "not important"]

        # --- Optimization: limit AI calls to the first 5 items ---
        MAX_AI_REQUESTS = 5

        for index, item in enumerate(news_items):
            text = f"[Ticker: {symbol.upper()}] {item.get('title', '')}. {item.get('summary', '')}".strip()
            if not text:
                continue

            # If we're in the first 5 items, request a smart ranking from Hugging Face
            if index < MAX_AI_REQUESTS:
                try:
                    resp = requests.post(
                        api_url,
                        headers=headers,
                        json={
                            "inputs": text,
                            "parameters": {
                                "candidate_labels": labels,
                                "multi_label": False,
                            },
                        },
                        timeout=8,  # 8 seconds max; if they're busy, fall back immediately
                    )

                    if resp.status_code != 200:
                        raise ValueError(f"status={resp.status_code}")

                    data = resp.json()
                    label_scores: dict[str, float] = {}

                    # Case 1: list of dicts
                    if (
                        isinstance(data, list)
                        and len(data) > 0
                        and isinstance(data[0], dict)
                        and "label" in data[0]
                    ):
                        for d_item in data:
                            label_scores[d_item.get("label", "")] = float(
                                d_item.get("score", 0.0)
                            )

                    # Case 2: list wrapping an older format
                    elif (
                        isinstance(data, list)
                        and len(data) > 0
                        and isinstance(data[0], dict)
                        and "labels" in data[0]
                    ):
                        inner = data[0]
                        for lbl, sc in zip(
                            inner.get("labels", []), inner.get("scores", [])
                        ):
                            label_scores[lbl] = float(sc)

                    # Case 3: classic dict format
                    elif (
                        isinstance(data, dict) and "labels" in data and "scores" in data
                    ):
                        for lbl, sc in zip(data["labels"], data["scores"]):
                            label_scores[lbl] = float(sc)

                    # Case 4: single-label fallback
                    elif isinstance(data, dict) and "label" in data and "score" in data:
                        label_scores[data["label"]] = float(data["score"])

                    else:
                        raise ValueError(f"Unexpected format. Raw: {data}")

                    score = (
                        1.0 * label_scores.get("very important", 0.0)
                        + 0.6 * label_scores.get("somewhat important", 0.0)
                        + 0.1 * label_scores.get("not important", 0.0)
                    )

                except Exception as e:
                    print(
                        f"⚠️ HF ranking failed for item {index+1} (using fallback): {e}"
                    )
                    # If it fails, use the fallback formula
                    score = min(len(text) / 400.0, 1.0)

            else:
                # --- After the first 5: save time by using fallback only ---
                score = min(len(text) / 400.0, 1.0)

            enriched = dict(item)
            enriched["importance_score"] = round(float(score), 3)
            ranked_items.append(enriched)

        ranked_items.sort(key=lambda x: x["importance_score"], reverse=True)
        return ranked_items
