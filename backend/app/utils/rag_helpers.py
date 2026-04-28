# utils/rag_helpers.py
def generate_duplicate_explanation(llm_client, new_text, candidates):
    """
    Ask LLM to generate a short explanation comparing new_text with top candidates.
    llm_client: wrapper around OpenAI/Ollama you already use
    candidates: list of dicts {id, issue, location, similarity}
    returns: str (short explanation)
    """
    prompt = "You are an assistant helping a civic issue reporting app. " \
             "A user submitted this new issue:\n\n" \
             f"NEW ISSUE:\n{new_text}\n\n" \
             "We found similar existing issues (id, similarity, text):\n"
    for c in candidates:
        prompt += f"\nID {c['id']} (score {c.get('similarity', 0)}): {c['issue'][:200].strip()}\n"
    prompt += "\nFor each existing issue, in 1-2 sentences say whether it's the same problem or different and why. " \
              "Then give a single recommended action: LINK <id> or CREATE.\nKeep answer concise (max 120 words)."

    # Call your LLM wrapper (pseudo)
    resp = llm_client.generate(prompt, max_tokens=180, temperature=0.2)
    return resp.strip()
