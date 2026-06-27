import os
from google import genai
from google.genai import types  # Required for strict type-safe orchestration parameters
from database.connection import BotDatabase
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class Gemini_Bot:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.db = BotDatabase()

    def _get_or_create_user(self, platform_user_id, platform, username="Unknown"):
        if not self.db.connect():
            return None
        try:
            with self.db.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id FROM users 
                    WHERE platform = %s AND platform_user_id = %s
                """, (platform.lower(), str(platform_user_id)))
                result = cursor.fetchone()
                if result:
                    return result['id']

                cursor.execute("""
                    INSERT INTO users (platform, platform_user_id, username)
                    VALUES (%s, %s, %s)
                """, (platform.lower(), str(platform_user_id), username))
                self.db.conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print("User registration/lookup error:", e)
            return None
        finally:
            self.db.close()

    # ----------------------------------------------------
    # FETCH HISTORY (Refactored to yield safe SDK objects)
    # ----------------------------------------------------
    def fetch_history(self, internal_user_id):
        history = []
        if not internal_user_id or not self.db.connect():
            return history

        try:
            with self.db.conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT role, message 
                    FROM messages 
                    WHERE user_id = %s
                    ORDER BY id ASC 
                    LIMIT 10
                """, (internal_user_id,))
                rows = cursor.fetchall()

                for row in rows:
                    role = "model" if row["role"] == "assistant" else "user"
                    # Fixed: Use SDK types.Content and types.Part arrays natively
                    history.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=row["message"])]
                        )
                    )
        except Exception as e:
            print("History fetch error:", e)
        finally:
            self.db.close()

        return history

    def save_message(self, internal_user_id, role, text):
        if not internal_user_id or not self.db.connect():
            return
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (user_id, role, message)
                    VALUES (%s, %s, %s)
                """, (internal_user_id, role, text))
                self.db.conn.commit()
        except Exception as e:
            print("Save error:", e)
        finally:
            self.db.close()

    # ----------------------------------------------------
    # GENERATE RESPONSE
    # ----------------------------------------------------
    def generate(self, platform_user_id, text=None, image=None, audio=None, pdf=None, platform="Telegram", username="Unknown"):
        internal_user_id = self._get_or_create_user(platform_user_id, platform, username)
        if not internal_user_id:
            return "⚠️ Database error. Failed to load user profile context."

        prompt_parts = []
        
        # RAG Injection Configuration Layer
        if text:
            try:
                from vector_db.chroma_manager import ChromaManager
                chroma = ChromaManager()
                search_results = chroma.search(user_id=str(platform_user_id), query=text, top_k=3)
                
                if search_results and "documents" in search_results and search_results["documents"][0]:
                    retrieved_chunks = search_results["documents"][0]
                    context_block = "\n---\n".join(retrieved_chunks)
                    
                    rag_prompt = (
                        "You have access to the user's uploaded knowledge base. "
                        "Use the following retrieved context snippets to answer their question accurately:\n\n"
                        f"[START RETRIEVED CONTEXT]\n{context_block}\n[END RETRIEVED CONTEXT]\n\n"
                    )
                    prompt_parts.append(types.Part.from_text(text=rag_prompt))
            except Exception as e:
                print(f"RAG Context retrieval skipped: {e}")

            prompt_parts.append(types.Part.from_text(text=text))
        else:
            prompt_parts.append(types.Part.from_text(text="Analyze the uploaded content"))

        # Multimodal file transformations using native SDK signatures
        if image:
            uploaded = self.client.files.upload(file=image)
            prompt_parts.append(uploaded)
        if audio:
            uploaded = self.client.files.upload(file=audio)
            prompt_parts.append(uploaded)
        if pdf:
            uploaded = self.client.files.upload(file=pdf)
            prompt_parts.append(uploaded)

        # Pull historical blocks and combine safely
        contents = self.fetch_history(internal_user_id)
        
        # Fixed: Appending the new user turn securely using types.Content wrapper 
        contents.append(
            types.Content(
                role="user",
                parts=prompt_parts
            )
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=f"You are a helpful {platform} AI assistant.",
                    max_output_tokens= 500
                )
            )

            self.save_message(internal_user_id, "user", text or "[file]")
            self.save_message(internal_user_id, "assistant", response.text)

            return response.text

        except Exception as e:
            print("Gemini API transaction error:", e)
            return "⚠️ AI service temporarily unavailable."