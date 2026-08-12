"""
OpenAI GPT se video ke liye title, description, tags generate karta hai.
"""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_metadata(video_filename: str, user_brief: str = "") -> dict:
    """
    video_filename: video ka naam (context ke liye, jaise "gym_routine_day3.mp4")
    user_brief: aap chaho to ek chhota sa note text file (same name .txt) me
                video ke baare me likh sakte ho, jise AI padh kar behtar
                content banayega. Optional hai.

    Returns dict: {title, description, tags (list), hashtags (list)}
    """
    niche = os.getenv("CHANNEL_NICHE", "general content")
    tone = os.getenv("CHANNEL_TONE", "engaging and friendly")

    prompt = f"""
Tum ek expert YouTube SEO copywriter ho. Neeche diye gaye video ke liye
YouTube upload karne layak metadata banao.

Channel niche: {niche}
Channel tone: {tone}
Video file name (context ke liye): {video_filename}
Extra info (agar user ne di ho): {user_brief if user_brief else "Koi extra info nahi di gayi, filename se andaza lagao"}

Mujhe sirf ek valid JSON object return karo, bilkul is format me, koi extra
text ya markdown backticks nahi:

{{
  "title": "SEO optimized catchy title, 60-70 characters ke andar",
  "description": "3-4 paragraph description jisme keywords naturally aayein, ant me relevant hashtags bhi ho",
  "tags": ["tag1", "tag2", "... total 10-15 relevant tags"],
  "hashtags": ["#tag1", "#tag2", "3-5 hashtags"]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    raw_text = response.choices[0].message.content.strip()

    # Agar model ne galti se ```json fences bhej diye to unhe hata do
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        metadata = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(f"AI se valid JSON nahi mila, raw response: {raw_text}")

    return metadata


if __name__ == "__main__":
    # Quick test
    result = generate_metadata("morning_workout_routine.mp4")
    print(json.dumps(result, indent=2, ensure_ascii=False))
