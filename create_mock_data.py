import os
import json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# zodiac_traits.json
# -----------------------------
zodiac_traits = {
    "Aries": {
        "personality": "Bold, energetic, initiator, competitive.",
        "strengths": "Leadership, courage, action-oriented, optimism.",
        "challenges": "Impatient, impulsive, short-tempered."
    },
    "Taurus": {
        "personality": "Reliable, grounded, loyal, beauty-loving.",
        "strengths": "Patience, practicality, determination.",
        "challenges": "Stubbornness, resistance to change."
    },
    "Gemini": {
        "personality": "Curious, expressive, adaptable, witty.",
        "strengths": "Communication, creativity, social intelligence.",
        "challenges": "Inconsistency, restlessness."
    },
    "Cancer": {
        "personality": "Emotional, protective, nurturing, intuitive.",
        "strengths": "Empathy, loyalty, emotional intelligence.",
        "challenges": "Moodiness, over-sensitivity."
    },
    "Leo": {
        "personality": "Confident, charismatic, expressive, generous.",
        "strengths": "Leadership, creativity, enthusiasm.",
        "challenges": "Pride, desire for validation."
    },
    "Virgo": {
        "personality": "Analytical, detail-oriented, practical.",
        "strengths": "Organization, discipline, reliability.",
        "challenges": "Perfectionism, overthinking."
    },
    "Libra": {
        "personality": "Diplomatic, charming, harmony-seeking.",
        "strengths": "Fairness, aesthetics, social intelligence.",
        "challenges": "Indecisiveness, conflict avoidance."
    },
    "Scorpio": {
        "personality": "Intense, passionate, mysterious.",
        "strengths": "Determination, emotional depth.",
        "challenges": "Jealousy, secrecy."
    },
    "Sagittarius": {
        "personality": "Adventurous, philosophical, optimistic.",
        "strengths": "Curiosity, independence, vision.",
        "challenges": "Impulsiveness, blunt communication."
    },
    "Capricorn": {
        "personality": "Disciplined, responsible, ambitious.",
        "strengths": "Persistence, structure, leadership.",
        "challenges": "Rigidity, work obsession."
    },
    "Aquarius": {
        "personality": "Innovative, unconventional, humanitarian.",
        "strengths": "Creativity, independent thinking.",
        "challenges": "Emotional detachment, unpredictability."
    },
    "Pisces": {
        "personality": "Compassionate, imaginative, intuitive.",
        "strengths": "Empathy, artistic talent, spirituality.",
        "challenges": "Escapism, over-sensitivity."
    }
}

with open(f"{DATA_DIR}/zodiac_traits.json", "w") as f:
    json.dump(zodiac_traits, f, indent=2)


# -----------------------------
# planetary_impacts.json
# -----------------------------
planetary_impacts = {
    "Sun": {
        "meaning": "Represents identity, ego, vitality and self-expression.",
        "type": "benefic"
    },
    "Moon": {
        "meaning": "Represents emotions, intuition, subconscious patterns.",
        "type": "benefic"
    },
    "Mars": {
        "meaning": "Represents ambition, aggression, energy and action.",
        "type": "malefic"
    },
    "Venus": {
        "meaning": "Represents love, beauty, relationships and creativity.",
        "type": "benefic"
    },
    "Mercury": {
        "meaning": "Represents communication, logic, intellect and travel.",
        "type": "neutral"
    },
    "Jupiter": {
        "meaning": "Represents wisdom, expansion, fortune and growth.",
        "type": "benefic"
    },
    "Saturn": {
        "meaning": "Represents discipline, karma, responsibility and lessons.",
        "type": "malefic"
    },
    "Rahu": {
        "meaning": "Represents illusion, ambition, obsession and unconventional paths.",
        "type": "malefic"
    },
    "Ketu": {
        "meaning": "Represents detachment, spirituality and karmic release.",
        "type": "malefic"
    }
}

with open(f"{DATA_DIR}/planetary_impacts.json", "w") as f:
    json.dump(planetary_impacts, f, indent=2)


# -----------------------------
# career_guidance.txt
# -----------------------------
career_guidance = [
    "Opportunities may arise in leadership roles today.",
    "Focus on learning to improve long-term gains.",
    "Working with teams will bring productive outcomes.",
    "Avoid rushing into decisions without clarity.",
    "Trust your instincts while starting new initiatives.",
    "Networking could open unexpected career doors.",
    "A disciplined approach may help you overcome challenges.",
    "Consider improving communication with colleagues.",
    "Strategic planning will bring better results than impulsive action.",
    "Patience in professional matters may lead to long-term rewards."
]

with open(f"{DATA_DIR}/career_guidance.txt", "w") as f:
    f.write("\n".join(career_guidance))


# -----------------------------
# love_guidance.txt
# -----------------------------
love_guidance = [
    "Emotional clarity strengthens relationships.",
    "Try communicating your feelings openly.",
    "Avoid arguments driven by ego or impatience.",
    "Show appreciation for the small gestures.",
    "Spend quality time with loved ones today.",
    "Honesty may help resolve lingering misunderstandings.",
    "Listening carefully can deepen emotional bonds.",
    "Romantic opportunities may arise through shared activities.",
    "Forgiveness can restore harmony in relationships.",
    "Patience may help strengthen emotional connections."
]

with open(f"{DATA_DIR}/love_guidance.txt", "w") as f:
    f.write("\n".join(love_guidance))


# -----------------------------
# spiritual_guidance.txt
# -----------------------------
spiritual_guidance = [
    "Meditation can enhance inner balance and clarity.",
    "Focus on gratitude to attract more abundance in life.",
    "Listen to intuition — the universe may be guiding you.",
    "Spending time in nature may restore inner peace.",
    "Reflect on past experiences for spiritual growth.",
    "Practicing mindfulness may improve emotional stability.",
    "Acts of kindness may strengthen spiritual alignment.",
    "Journaling thoughts can help clarify deeper emotions."
]

with open(f"{DATA_DIR}/spiritual_guidance.txt", "w") as f:
    f.write("\n".join(spiritual_guidance))


# -----------------------------
# nakshatra_mapping.json
# -----------------------------
nakshatra_mapping = {
    "Ashwini": "Fast-moving, healing, beginnings.",
    "Bharani": "Strong willpower, transformation.",
    "Krittika": "Fiery energy, truth-seeker, protector.",
    "Rohini": "Creativity, beauty, fertility and growth.",
    "Mrigashira": "Curiosity, searching mind, exploration.",
    "Ardra": "Transformation through challenges.",
    "Punarvasu": "Renewal, optimism and fresh starts.",
    "Pushya": "Nurturing, spiritual wisdom and stability.",
    "Magha": "Leadership, ancestral power and authority."
}

with open(f"{DATA_DIR}/nakshatra_mapping.json", "w") as f:
    json.dump(nakshatra_mapping, f, indent=2)

print("Astrology knowledge base generated in ./data/")