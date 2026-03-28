#!/usr/bin/env python3
"""Fix the _avoid_repeat function to properly handle generic responses."""

import re

def main():
    with open('orchestrator.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of _avoid_repeat
    start_marker = "def _avoid_repeat(self, session_id: str, user_message: str, reply_text: str) -> str:"
    start_idx = content.find(start_marker)

    if start_idx == -1:
        print("ERROR: Could not find _avoid_repeat function")
        return 1

    # Find the end - look for the next "def " at the same indentation
    search_from = start_idx + len(start_marker)
    end_marker = "\n    def process_message"
    end_idx = content.find(end_marker, search_from)

    if end_idx == -1:
        print("ERROR: Could not find end of _avoid_repeat function")
        return 1

    # Back up to include the method's indentation
    func_start = content.rfind("\n    def _avoid_repeat", 0, start_idx + 10)
    if func_start == -1:
        func_start = start_idx - 4

    old_func = content[func_start:end_idx]
    print(f"Found function from {func_start} to {end_idx}")
    print(f"Old function length: {len(old_func)}")

    new_func = '''
    def _avoid_repeat(self, session_id: str, user_message: str, reply_text: str) -> str:
        """Ensure we don't echo identical replies; use message-specific fallback."""
        text = (reply_text or "").strip()
        last = self._last_reply.get(session_id, "").strip()
        
        # Normalize for comparison
        text_normalized = text.lower().replace("'", "'").replace("'", "'")

        def is_generic(t: str) -> bool:
            patterns = [
                "i'm here to support you",
                "i am here to support you",
                "what's on your mind",
                "what is on your mind",
                "can you tell me more",
                "how can i help",
                "how can i support",
            ]
            return any(p in t for p in patterns)

        def paraphrase_for_message(msg: str) -> str:
            msg_lower = msg.lower().strip()
            if any(w in msg_lower for w in ["hello", "hi", "hey"]):
                return "Welcome! I'm your SuperSerene wellness coach. What's been the toughest part of today so far?"
            elif any(w in msg_lower for w in ["not much", "nothing", "idk", "dunno"]):
                return "Sometimes it's hard to name what we feel. If you had to pick one word for today, what would it be?"
            elif any(w in msg_lower for w in ["sad", "down", "low", "depressed"]):
                return "It sounds heavy right now. What happened today that brought this feeling up?"
            elif any(w in msg_lower for w in ["angry", "frustrated", "annoyed", "mad", "fuck"]):
                return "Frustration often signals something important. What boundary or need might be asking for attention?"
            elif any(w in msg_lower for w in ["tired", "exhausted", "drained"]):
                return "Being tired affects everything. Have you been able to rest at all today?"
            elif any(w in msg_lower for w in ["anxious", "worried", "nervous", "stress"]):
                return "Anxiety can feel overwhelming. What's the one thing that feels most urgent right now?"
            else:
                snippet = msg[:80].strip() if msg else "that"
                return f"Thanks for sharing about '{snippet}'. What part of this feels most pressing to you?"

        # If empty or generic, use message-specific fallback
        if not text or is_generic(text_normalized):
            self.log.info("_avoid_repeat: detected generic, using fallback", original=text[:50] if text else "EMPTY")
            text = paraphrase_for_message(user_message)
        # If exactly the same as last reply, also paraphrase
        elif text == last:
            self.log.info("_avoid_repeat: same as last reply, using fallback")
            text = paraphrase_for_message(user_message)

        self._last_reply[session_id] = text
        return text
'''

    new_content = content[:func_start] + new_func + content[end_idx:]

    with open('orchestrator.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("SUCCESS: _avoid_repeat function replaced")
    return 0

if __name__ == "__main__":
    exit(main())
