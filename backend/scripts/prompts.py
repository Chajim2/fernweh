def get_umbrella_terms(text):
    return (
            f"I have this text: {text} (end of text). Analyze the sentiment and emotions in the text and Generate 6 unique and evocative umbrella terms that capture the nuanced feelins expressed.\n"
            "Format your response EXACTLY like this, with all on one line:\n"
            "term1 : definition1;term2 : definition2;term3 : definition3;term4 : definition4;term5 : definition5;term6 : definition6\n"
            "Rules:\n"
            "1. Each term should be a single unique word\n"
            "2. Use English and foreign terms about 50% of the time each, with non-English wordswhen they capture a complex emotion\n"
            "3. Focus on rare or poetic words (like 'ephemeral' or 'ethereal'), can be from any language\n"
            "4. Definitions must be brief (5-10 words) but evocative\n"
            "5. No basic emotions like 'happy' or 'sad'\n"
            "6. All text should be lowercase\n"
            "7. No blank lines between terms\n"
            "8. No additional text or formatting\n"
        )

def get_chunks(text):
    return f"""You are the semantic core of "Fernweh," a social journaling application.
        Your goal is to prepare raw user diary entries for vector embedding.

        INPUT: {text}

        YOUR TASKS:
        1.  **Chunking:** Split the text into logical, atomic "thoughts" or events. Do not split by sentence if the sentences belong to one thought.
        2.  **Context Injection (CRITICAL):** Rewrite each chunk so it stands alone.
        * Replace pronouns (he, she, it, that) with the specific entities mentioned earlier in the text.
        * If the user says "I went there", change it to "I went to [Berlin]".
        * The embedding model will only see the chunk, so it MUST contain all context.
        3.  **Sentiment Classification:** Assign one of these tags to each chunk:
        * `JOY` (Success, happiness, gratitude) -> Triggers "Hype" notifications.
        * `CURIOSITY` (Learning, exploring, ideas) -> Triggers "Brainstorming" notifications.
        * `SADNESS` (Pain, loss, loneliness) -> Triggers "Support/Empathy" notifications.
        * `ANGER` (Frustration, conflict) -> Triggers "Venting" notifications.
        * `NEUTRAL` (Facts, logistics) -> No trigger.

        OUTPUT FORMAT: JSON only."""

def get_update_user_summary_prompt(new_entry, summary):
    return (
        "You are an assistant that maintains a concise summary of a user's lifestyle, habits, and preferences based on their journal entries.\n\n"
        "Current Summary:\n"
        f"{summary}\n\n"
        "New Journal Entry:\n"
        f"{new_entry}\n\n"
        "Your task: Update the Current Summary by incorporating any new relevant information from the New Journal Entry. \n"
        "- Keep the summary focused on facts about the user's preferences, habits, routines, and feelings.\n"
        "- Prioritize keeping existing information; only modify or remove parts if the new entry clearly contradicts or updates them.\n"
        "- Add new insights from the entry if they are significant.\n"
        "- Write the updated summary as a brief list of statements, each on its own line.\n"
        "- Avoid repeating information already in the summary.\n"
        "- If the new entry has no relevant updates, return the Current Summary unchanged.\n\n"
        "Updated Summary:\n"
    )

def get_schedule_day_prompt(daily_notes, summary, fixed_tasks_json, wake_time, sleep_time, activities, lock_meter):
    return (
        "You are an intelligent daily scheduler assistant.\n\n"
        "INPUTS:\n\n"
        f"1. Fixed Tasks (cannot be moved or rescheduled):\n{fixed_tasks_json}\n\n"
        f"2. User Summary (includes prioritized tasks, daily habits, and time preferences):\n{summary}\n\n"
        f"3. Additional Notes for Today:\n{daily_notes}\n\n"
        f"4. Available Activities (optional activities the user enjoys):\n{activities}\n\n"
        f"5. User Awake Window: from {wake_time} to {sleep_time}\n"
        f"6. Lock Meter (relaxation percentage): {lock_meter}%\n\n"
        "TASK:\n\n"
        "Using the fixed tasks as immovable anchors, create a daily schedule that fits all other tasks logically and efficiently, respecting the user's preferences, habits, and awake hours.\n\n"
        "SCHEDULING RULES:\n"
        "- Schedule fixed tasks exactly at their given start times.\n"
        "- Prioritize tasks from the User Summary. If time remains, use the 'Available Activities' list to fill gaps.\n"
        "- Respect the Lock Meter: schedule approximately that percentage of the awake day as relaxation time, distributed throughout the day rather than in one chunk.\n"
        "- Use best practices from productivity science:\n"
        "  • Group work into 50–90 minute focus blocks followed by 5–15 minute breaks.\n"
        "  • Schedule demanding or important tasks earlier in the day (after waking up).\n"
        "  • Place lighter or creative tasks in the afternoon or evening.\n"
        "  • Avoid back-to-back unrelated tasks to minimize mental fatigue (group similar tasks where possible).\n"
        "  • Include meals and short breaks even if Lock Meter is low.\n"
        "- Avoid scheduling tasks beyond the user's sleep time.\n"
        "- Avoid scheduling tasks at times the user dislikes or prefers to avoid.\n\n"
        "OUTPUT:\n"
        """ Your response must be a valid JSON array. Each element should be an object with the following structure:
        [
          {
            "id": 1,
            "title": "Wake up",
            "duration": 0,
            "start_time": "07:10",
            "notes": ""
          },
          {
            "id": 2,
            "title": "Morning Routine",
            "duration": 50,
            "start_time": "07:10",
            "notes": ""
          },
          {
            "id": 3,
            "title": "Class",
            "duration": 120,
            "start_time": "08:00",
            "notes": ""
          }
        ]"""
        "If some tasks cannot fit, omit them, dont overschedule. Output only the JSON array — no explanations or extra text."
    )