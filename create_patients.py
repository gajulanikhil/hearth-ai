"""One-time script to seed 5 demo patients."""
import json
from pathlib import Path

BASE = Path(__file__).parent / "data" / "patients"

patients = [
    {
        "id": "robert_hayes",
        "profile": {
            "name": "Robert Hayes",
            "age": 82,
            "stage": "mild",
            "primary_family_contact": "Carol Hayes (daughter)",
            "emotional_anchors": ["Navy service 1962-1966", "fishing on Lake Travis", "classic Ford Mustangs"],
            "calming_topics": ["baseball", "woodworking", "his golden retriever Duke"],
            "avoid_topics": ["Korea", "his brother Jim passing"],
            "current_mood_baseline": "alert and sociable in the mornings",
            "best_time_of_day": "morning"
        },
        "memories": [
            {
                "submitted_by": "Carol Hayes",
                "relationship": "daughter",
                "memory_text": "Dad spent every Saturday morning in the garage working on his 1968 Ford Mustang. He bought it the year I was born and said he would never sell it. He had a specific order for everything — he always cleaned the carburetor first, then moved to the bodywork. Mom would bring coffee out at exactly nine and he would wipe his hands on a red rag and take it without stopping whatever he was explaining to me. He called it the Red Lady. It is still in the garage.",
                "associated_photos": ["mustang_garage.jpg"],
                "emotional_tone": "warm",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Carol Hayes",
                "relationship": "daughter",
                "memory_text": "He served on the USS Coral Sea from 1962 to 1966. He does not talk about the hard parts but he lights up when you ask about the guys in his unit. He called them Sal and Benny and Mouse. Mouse could eat six cheeseburgers in one sitting and nobody believed him the first time. Dad still laughs when he tells that story.",
                "associated_photos": ["navy_photo.jpg"],
                "emotional_tone": "nostalgic",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Carol Hayes",
                "relationship": "daughter",
                "memory_text": "Every summer we drove to Lake Travis with the boat. Dad would be up at five to launch before the other families got there. He had a whole philosophy about early morning fishing — water temperature and the way bass feed before the sun gets high. He taught me to cast when I was six. I still do it the way he showed me, with the flick at the end of the wrist.",
                "associated_photos": [],
                "emotional_tone": "joyful",
                "voice_sample_file": None
            }
        ]
    },
    {
        "id": "eleanor_voss",
        "profile": {
            "name": "Eleanor Voss",
            "age": 75,
            "stage": "moderate",
            "primary_family_contact": "Thomas Voss (husband)",
            "emotional_anchors": ["teaching third grade for 32 years", "Christmas Eve strudel tradition", "Vienna trip 1989"],
            "calming_topics": ["classical piano", "roses in her garden", "Jane Austen novels"],
            "avoid_topics": ["the fire at the school", "losing the baby in 1976"],
            "current_mood_baseline": "warm but occasionally disoriented after 3pm",
            "best_time_of_day": "mid-morning"
        },
        "memories": [
            {
                "submitted_by": "Thomas Voss",
                "relationship": "husband",
                "memory_text": "Eleanor taught third grade at Riverside Elementary for thirty-two years. She graded every paper at the kitchen table on Fridays and wrote a real note on every one — not just the grade. Parents used to call the school just to say thank you. She kept a box of letters from former students. There must be two hundred in there. She read them when she was having a hard day.",
                "associated_photos": ["eleanor_classroom.jpg"],
                "emotional_tone": "warm",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Thomas Voss",
                "relationship": "husband",
                "memory_text": "We went to Vienna for our 25th anniversary in 1989. Eleanor had wanted to go since she was a girl because of Mozart. We attended a concert at the Musikverein — she wore her navy dress and cried during the second movement of the Clarinet Concerto. She said it was the most beautiful two hours of her life. I think she meant it.",
                "associated_photos": ["vienna_1989.jpg"],
                "emotional_tone": "bittersweet",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Thomas Voss",
                "relationship": "husband",
                "memory_text": "Every Christmas Eve, Eleanor made her mother's strudel recipe from scratch — handwritten in German on an index card her grandmother brought from Salzburg. She would start at noon. The whole house smelled of apples and cinnamon and butter. Our son Eric would stand on a step stool and watch. She said the dough had to be thin enough to read a newspaper through.",
                "associated_photos": [],
                "emotional_tone": "nostalgic",
                "voice_sample_file": None
            }
        ]
    },
    {
        "id": "james_okafor",
        "profile": {
            "name": "James Okafor",
            "age": 71,
            "stage": "mild",
            "primary_family_contact": "Amara Okafor (daughter)",
            "emotional_anchors": ["Lagos childhood and the market with his mother", "building his first house in Houston 1988", "coaching youth soccer for 15 years"],
            "calming_topics": ["jazz music", "Nigerian cooking smells", "watching grandchildren play"],
            "avoid_topics": ["the stroke in 2019", "his friend Chukwu passing last year"],
            "current_mood_baseline": "energetic and talkative, very proud",
            "best_time_of_day": "afternoon"
        },
        "memories": [
            {
                "submitted_by": "Amara Okafor",
                "relationship": "daughter",
                "memory_text": "Dad grew up in the Surulere neighborhood of Lagos. He always talks about going to the market with his mother on Saturdays — the smell of smoked fish and palm oil, the sound of generators and haggling. He said his mother could negotiate the price of anything down by half and do it while telling you a story. He says that is where he learned to talk to people.",
                "associated_photos": [],
                "emotional_tone": "nostalgic",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Amara Okafor",
                "relationship": "daughter",
                "memory_text": "When I was twelve, Dad built our first house on Holcombe Street by himself on weekends. He had a full-time job at the refinery but woke up at six every Saturday and Sunday to work. The neighbor Mr. Petrov started helping every weekend and they became lifelong friends. Dad still drives by that house sometimes just to look at it.",
                "associated_photos": ["holcombe_house.jpg"],
                "emotional_tone": "proud",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Amara Okafor",
                "relationship": "daughter",
                "memory_text": "He coached the Westpark Tigers under-ten soccer team for fifteen years. His rule: every kid plays every game, no exceptions. He kept a notebook with every player he ever coached — their positions, what they were working on, what they were good at. He still has it. There are over two hundred names in it.",
                "associated_photos": ["soccer_team.jpg"],
                "emotional_tone": "joyful",
                "voice_sample_file": None
            }
        ]
    },
    {
        "id": "dorothy_sinclair",
        "profile": {
            "name": "Dorothy Sinclair",
            "age": 88,
            "stage": "severe",
            "primary_family_contact": "Helen Sinclair-Park (granddaughter)",
            "emotional_anchors": ["her farm in Lubbock", "playing piano at church for 40 years", "late husband Walter"],
            "calming_topics": ["hymns", "smell of rain on dry earth", "pictures of horses"],
            "avoid_topics": ["the tornado of 1970", "her son Billy passing"],
            "current_mood_baseline": "quiet, responds well to music and gentle touch",
            "best_time_of_day": "early morning before 9am"
        },
        "memories": [
            {
                "submitted_by": "Helen Sinclair-Park",
                "relationship": "granddaughter",
                "memory_text": "Grandma Dorothy grew up on a cotton farm outside Lubbock. She always said the best smell in the world was the dirt after the first rain of spring. She rode horses before school every morning until she was sixteen. Her favorite was a quarter horse named Pearl she got for her twelfth birthday. She could ride bareback by age nine.",
                "associated_photos": ["lubbock_farm.jpg"],
                "emotional_tone": "warm",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Helen Sinclair-Park",
                "relationship": "granddaughter",
                "memory_text": "She played piano at First Baptist Church in Slaton for forty years — hundreds of weddings, funerals, and Christmas cantatas. She learned mostly by ear. She could hear a hymn once and play it back. Even in her seventies she would sit down and play for an hour without stopping. Amazing Grace was always her last song. Always.",
                "associated_photos": [],
                "emotional_tone": "bittersweet",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Helen Sinclair-Park",
                "relationship": "granddaughter",
                "memory_text": "Walter proposed on the front porch of the farm in 1956. He brought wildflowers he picked himself and was so nervous he dropped them twice. They were married for fifty-one years. She kept his reading glasses in her bedside drawer even after he passed. She said it felt wrong to put them anywhere else.",
                "associated_photos": ["walter_dorothy_wedding.jpg"],
                "emotional_tone": "bittersweet",
                "voice_sample_file": None
            }
        ]
    },
    {
        "id": "frank_nguyen",
        "profile": {
            "name": "Frank Nguyen",
            "age": 68,
            "stage": "mild",
            "primary_family_contact": "Linh Nguyen (wife)",
            "emotional_anchors": ["arriving in Houston 1981", "opening the pho restaurant on Bellaire", "his mother teaching him to cook in Saigon"],
            "calming_topics": ["Vietnamese cooking", "fishing at Galveston Bay", "Bruce Lee movies"],
            "avoid_topics": ["the boat crossing", "leaving Saigon"],
            "current_mood_baseline": "cheerful and sociable, occasional word-finding difficulty",
            "best_time_of_day": "morning"
        },
        "memories": [
            {
                "submitted_by": "Linh Nguyen",
                "relationship": "wife",
                "memory_text": "Frank learned to cook from his mother in Saigon. She made pho from scratch every Sunday — broth simmering from Friday night. He memorized her recipe entirely in his head. When we opened the restaurant on Bellaire in 1989, the first bowl he served was her recipe exactly. He cried in the kitchen that day. He thought no one saw but I did.",
                "associated_photos": ["pho_restaurant.jpg"],
                "emotional_tone": "bittersweet",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Linh Nguyen",
                "relationship": "wife",
                "memory_text": "He arrived in Houston in 1981 speaking almost no English. He worked at a shrimp processing plant for two years while he learned, studying index cards on the bus. He became a citizen in 1987 and called it the best day of his life after the day our daughter Mai was born. He framed the certificate and it hung in the restaurant for twenty years.",
                "associated_photos": ["citizenship_day.jpg"],
                "emotional_tone": "proud",
                "voice_sample_file": None
            },
            {
                "submitted_by": "Linh Nguyen",
                "relationship": "wife",
                "memory_text": "Every Sunday when the restaurant was closed, Frank fished at Galveston Bay alone. He said it was the only time he could hear himself think. He always brought home whatever he caught and cooked it that night — steamed with ginger and scallion the way his mother taught him. He said fish tastes different when you catch it yourself.",
                "associated_photos": [],
                "emotional_tone": "warm",
                "voice_sample_file": None
            }
        ]
    }
]

for p in patients:
    d = BASE / p["id"]
    (d / "photos").mkdir(parents=True, exist_ok=True)
    (d / "voice_samples").mkdir(parents=True, exist_ok=True)
    with open(d / "profile.json", "w", encoding="utf-8") as f:
        json.dump(p["profile"], f, indent=2, ensure_ascii=False)
    with open(d / "memories.json", "w", encoding="utf-8") as f:
        json.dump(p["memories"], f, indent=2, ensure_ascii=False)
    print(f"  Created: {p['id']:<20}  {p['profile']['stage']:<10}  age {p['profile']['age']}")

print("\nAll 5 patients created.")
