import os, json, requests
from app.config import settings
from dotenv import load_dotenv
load_dotenv()  # loads variables from .env into the process environment

class LLMClient:
    def __init__(self):
        self.provider = settings.PROVIDER.lower()

    def generate(self, prompt: str) -> str:
        if self.provider == 'openai':
            return self._openai(prompt)
        elif self.provider == 'gemini':
            return self._gemini(prompt)
        elif self.provider == 'groq':
            return self._groq(prompt)        
        # default to ollama
        return self._ollama(prompt)

    def _gemini(self, prompt: str) -> str:
        import os, requests
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        body = {"contents":[{"parts":[{"text": prompt}]}]}
        r = requests.post(url, json=body, timeout=120); r.raise_for_status()
        j = r.json()
        return j["candidates"][0]["content"]["parts"][0].get("text","").strip()
    def _ollama(self, prompt: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        data = {"model": settings.OLLAMA_MODEL, "prompt": prompt, "temperature": 0}
        with requests.post(url, json=data, stream=True, timeout=120) as r:
            r.raise_for_status()
            out = []
            for line in r.iter_lines():
                if not line: continue
                obj = json.loads(line.decode())
                if "response" in obj:
                    out.append(obj["response"])
                if obj.get("done"): break
            return "".join(out).strip()
    def _groq(self, prompt: str) -> str:
        import os, requests

        key   = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        def mask(s: str | None) -> str:
            if not s:
                return "<<MISSING>>"
            return f"{s[:6]}...{s[-4:]}" if len(s) > 10 else "<<REDacted>>"

        # --- Debug prints (safe) ---
        print("[GROQ] provider=groq")
        print(f"[GROQ] model={model}")
        print(f"[GROQ] key_present={bool(key)} key={mask(key)}")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        # show masked header for verification
        safe_headers = dict(headers)
        safe_headers["Authorization"] = f"Bearer {mask(key)}"
        print(f"[GROQ] headers={safe_headers}")

        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        print("[GROQ] POST https://api.groq.com/openai/v1/chat/completions")

        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=120,
            )
            print(f"[GROQ] status={r.status_code}")
            if r.status_code != 200:
                # print a snippet to see the error details
                print("[GROQ] response snippet:", r.text[:600])
            r.raise_for_status()
            j = r.json()
            return j["choices"][0]["message"]["content"].strip()
        except requests.HTTPError as e:
            # show up to 600 chars of the error body for easy debugging
            err_body = getattr(e.response, "text", "")[:600]
            print("[GROQ] HTTPError:", e)
            print("[GROQ] HTTPError body:", err_body)
            raise
    def _openai(self, prompt: str) -> str:
        # Minimal OpenAI Chat Completions call; user must set OPENAI_API_KEY
        import requests
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": settings.OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=120)
        resp.raise_for_status()
        j = resp.json()
        return j["choices"][0]["message"]["content"].strip()
