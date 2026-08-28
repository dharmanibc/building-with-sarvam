const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Speech and Language APIs";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "03 · Speech & Language"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 03 · The lab", title: "Speech and Language\nAPIs, end to end",
  subtitle: "Every mode, every parameter, every silent failure",
  meta: "Saaras · Bulbul · Mayura · Sarvam-Translate · Transliterate · Language ID" });

/* 2 */ s = T.slideL(p, "One script, the whole stack", "The lab");
T.flow(p, s, [
  { t: "Language ID", d: "detect language + script" },
  { t: "Translate", d: "English ⇄ Hindi" },
  { t: "Transliterate", d: "Devanagari → Roman" },
  { t: "Text to Speech", d: "save a .wav in your language" },
  { t: "Speech to Text", d: "transcribe it back, 5 modes" },
  { t: "cost_report()", d: "total spend, in ₹" },
], { y: 2.0, h: 1.7 });
T.txt(s, "Ninety seconds of typing for you. Twenty-eight minutes of understanding. The point of step 4 is that it produces a file you can play — hearing your own language spoken by code you just ran is the moment this becomes real.", {
  x: M, y: 4.05, w: CW, h: 1.0, fontSize: 13.5, color: C.MUTEDL, lineSpacing: 21 });
T.takeaway(p, s, "Whole tour costs about ₹4.20. You have ₹1000 of free credit. Drop your generated audio in chat when you have it.", { icon: "₹" });
T.foot(s, ...FT);

/* 3 */ s = T.sectionSlide(p, { num: "A", title: "Saaras — speech to text", subtitle: "Five modes, three delivery paths, one very expensive gotcha" });

/* 4 */ s = T.slideL(p, "Why Indic ASR is genuinely hard", "Context");
T.cards(p, s, [
  { icon: "22", title: "Scripts and phonologies", body: "Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam, Gurmukhi, Odia, Perso-Arabic. Not variants of one language — different families." },
  { icon: "⇄", title: "Code-mixing is the norm", body: "\"Mera EMI due date kya hai\" is not broken Hindi. It is how 400 million people actually speak. Most models treat it as noise." },
  { icon: "☎", title: "8 kHz telephony", body: "Real Indian call traffic is 8kHz mu-law. Half the frequency range of the 16kHz audio most models are trained on.", color: C.TEAL },
  { icon: "▲", title: "Accent variance", body: "The same language across 1,500 km sounds materially different. Training on one region's speech does not generalise.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 2.2, bSize: 10.5 });
T.takeaway(p, s, "This is why an English-first model with an 'Indian English' setting is not a substitute. It is a different problem, not a harder version of the same one.");
T.foot(s, ...FT);

/* 5 */ s = T.slideL(p, "The five modes — the centrepiece", "Saaras");
T.table(p, s, { y: 1.6, headers: ["mode=", "Returns", "Use it for", "Example output"],
  colW: [1.7, 2.9, 3.5, 3.993],
  rows: [
    ["transcribe", "Native-script text, lightly normalised", "Default. Chat logs, search, storage", "मेरा EMI due date क्या है"],
    ["translate", "English text", "Analytics, dashboards, English-only systems", "What is my EMI due date"],
    ["verbatim", "Every disfluency, filler, repetition", "Compliance, QA scoring, legal record", "मेरा... उम्म... EMI due date क्या है"],
    ["translit", "Roman script", "Where your DB or UI cannot render Devanagari", "mera EMI due date kya hai"],
    ["codemix", "Preserves the actual mix as spoken", "Realistic training data, authentic UX", "mera EMI due date kya hai"],
  ], rowH: 0.52, size: 10.5 });
T.takeaway(p, s, "Same audio file. Five different products. Most people discover mode= three weeks into a project and rewrite everything.");
T.foot(s, ...FT);
s.addNotes("Run all five live on one file. The comparison table is the lab deliverable. Ask the room which mode they'd pick for a compliance recording — verbatim is not the obvious answer until you explain it.");

/* 6 */ s = T.slideL(p, "Three delivery paths — pick by shape of audio", "Saaras");
T.compare(p, s,
  { icon: "1", title: "REST — clips under 30 seconds", color: C.SAF, items: [
    "Simplest possible integration",
    "Max 30 seconds per request",
    "Good for: voice notes, short commands, testing",
    "Auto-detects codec for most formats",
    "mp3, wav, aac, aiff, ogg/opus, flac, mp4/m4a, amr",
    "PCM (pcm_s16le, pcm_l16, pcm_raw) at 16kHz only",
  ]},
  { icon: "2", title: "Batch — long audio, async", color: C.TEAL, items: [
    "Up to 20 files, 60 minutes each",
    "Speaker diarization available (₹45/hr vs ₹30/hr)",
    "Chunk-level timestamps",
    "Good for: meetings, interviews, call-centre archives",
    "Submit → poll → fetch. Plan for job lifecycle",
    "Python SDK handles files up to 1 hour",
  ]},
  { y: 1.7, h: 3.3, size: 11 });
T.rows(p, s, [
  { icon: "3", title: "Realtime WebSocket — live transcription", body: "Ultra-low latency. VAD parameters control how speech segments are detected and finalised. Flush signal for clean boundaries between segments. Start and end events. 8kHz supported. This is the one your voice agent needs." },
], { y: 5.2, rh: 1.0 });
T.foot(s, ...FT);

/* 7 */ s = T.slideD(p, "Where sample_rate belongs — and where it does not", "The correction that surprises people");
T.code(p, s, { y: 1.62, h: 1.95, label: "WRONG — sample_rate is NOT a REST parameter",
  code: `resp = client.speech_to_text.transcribe(\n    file=open("call_8khz.wav", "rb"),\n    model="saaras:v3", language_code="hi-IN",\n    sample_rate=8000,        # <- TypeError: unexpected keyword argument\n)   # A .wav header ALREADY declares the rate. Nothing to pass.` });
T.code(p, s, { y: 3.72, h: 1.95, label: "RIGHT — declare it only when streaming raw samples",
  code: `with client.speech_to_text_streaming.connect(\n        model="saaras:v3", language_code="hi-IN",\n        sample_rate=str(rate),          # <- REQUIRED here\n        input_audio_codec="pcm_s16le",  # raw PCM carries no header\n) as ws: ...` });
T.takeaway(p, s, "Container in, rate declared for you. Raw samples in, you declare it. Get this backwards on a streaming socket and you DO get the silent-garbage failure the internet warns about — just not on the REST path.", { dark: true, y: 5.82, icon: "!" });
s.addNotes("This corrects an earlier version of this deck that claimed 8 kHz REST audio fails silently without sample_rate. Lab 02 measured it: Saaras reads the WAV header and handles 8 kHz fine. Say the correction out loud — a room that hears you fix your own slide trusts the rest of it more.");

/* 8 */ s = T.slideL(p, "Everything else you can control", "Saaras reference");
T.table(p, s, { y: 1.6, headers: ["Parameter", "What it does", "Notes"], colW: [3.0, 4.6, 4.493],
  rows: [
    ["model", "saaras:v3 (default) · saaras:v4", "Pass explicitly to pin behaviour — defaults drift between releases"],
    ["mode", "transcribe / translate / verbatim / translit / codemix", "The five modes. Default transcribe"],
    ["language_code", "hi-IN, ta-IN, bn-IN ... 23 total", "Or omit for auto-detection"],
    ["sample_rate", "STREAMING ONLY — not a REST parameter", "REST raises TypeError; the .wav header carries it (see previous slide)"],
    ["diarization", "Speaker identification", "₹45/hr instead of ₹30/hr. Only pay when you need who-said-what"],
    ["pronunciation dict", "Control specific words and names", "Brand names, SKUs, scheme names. dict_id is honoured on bulbul:v3 only"],
    ["VAD params", "Speech detection on WebSocket", "Controls where a turn ends in realtime"],
    ["flush signal", "Finalise a transcription segment", "WebSocket only. Clean segment boundaries"],
  ], rowH: 0.35, size: 10 });
T.takeaway(p, s, "Legacy note: /speech-to-text-translate is now legacy. Use /speech-to-text with model=saaras:v3 and mode=translate.");
T.foot(s, ...FT);

/* 9 */ s = T.sectionSlide(p, { num: "B", title: "Bulbul — text to speech", subtitle: "Where 60% of your voice product's cost actually lives" });

/* 10 */ s = T.slideL(p, "Pick voices by persona, not preference", "Bulbul");
T.cards(p, s, [
  { icon: "1", title: "Conversational / Friendly", body: "Support bots, assistants, anything where the caller should feel at ease. The default choice for customer service." },
  { icon: "2", title: "News / Authoritative", body: "Announcements, compliance readouts, government notices. Where the content must sound official." },
  { icon: "3", title: "Entertainment / Dynamic", body: "Content, edtech, media. Higher energy and range — wrong for a bank, right for a learning app.", color: C.TEAL },
  { icon: "4", title: "Consistent / Neutral", body: "Long-form narration where you need the voice to disappear rather than perform.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 1.95, bSize: 10.5 });
T.rows(p, s, [
  { icon: "⚙", title: "The control surface", body: "pitch · pace · loudness · tone · sample rate · text preprocessing · max sentence-split length · buffer size to start processing. The last three trade latency against prosody." },
  { icon: "■", title: "Output formats", body: "mp3 · linear16 · mulaw · alaw · opus · flac · aac · wav. For telephony you want mulaw or alaw — get this wrong and you hear static or chipmunks." },
], { y: 3.95, rh: 1.0 });
T.foot(s, ...FT);

/* 11 */ s = T.slideD(p, "Streaming is not optional", "Bulbul");
T.table(p, s, { y: 1.65, headers: ["Path", "First audio", "Use for"], colW: [3.2, 3.0, 5.893],
  rows: [
    ["REST (batch)", "After full generation", "Pre-rendered prompts, IVR menus, anything you can cache"],
    ["HTTP stream", "Progressive", "Web playback where you control the player"],
    ["WebSocket", "Fastest, with end signal", "Voice agents. The only real option for conversation"],
  ], rowH: 0.42, size: 11 });
T.code(p, s, { y: 3.4, h: 2.6, ls: 13, size: 10, label: "PYTHON — the call everyone starts with",
  code: `from sarvamai import SarvamAI\nfrom sarvamai.play import save\n\nclient = SarvamAI(api_subscription_key="YOUR_KEY")\n\nresponse = client.text_to_speech.convert(\n    text="नमस्ते, कैसे हैं आप?",\n    language_code="hi-IN",     # <- NOT target_language_code\n    model="bulbul:v3",         # v2 deprecated 2026-08-27\n    speaker="pooja",           # v3 voice — v2 names raise BadRequestError\n)\nsave(response, "output.wav")` });
T.takeaway(p, s, "Measure time-to-first-byte across all three yourself. Quoting your own numbers beats quoting the docs.", { dark: true, y: 6.05 });

/* 12 */ s = T.slideL(p, "TTS is where a voice product's money goes", "Bulbul · cost");
T.stats(p, s, [
  { value: "₹30", label: "bulbul:v3\nper 10,000 characters" },
  { value: "~1,600", label: "characters an agent speaks\nin a 3-minute call" },
  { value: "₹4.80", label: "TTS cost\nper 3-minute call" },
  { value: "60%", label: "of a voice agent's bill\nis TTS (see Segment 07)", color: C.SAF },
], { y: 1.72, h: 1.95, vSize: 32 });
T.rows(p, s, [
  { icon: "!", title: "bulbul:v2 was deprecated on 27 August 2026 — there is no cheaper tier to fall back to",
    body: "Earlier versions of this deck taught a v2-vs-v3 cost trade. That choice no longer exists, and the v2 voice names (anushka, karun, …) now raise BadRequestError on v3.",
    color: C.RED },
  { icon: "→", title: "So the remaining levers are script length and turn count, not model choice",
    body: "Twenty per cent fewer spoken characters is twenty per cent off your largest line item. Write shorter agent replies — it is cheaper AND it sounds better on a phone call.",
    color: C.TEAL },
], { y: 3.95, rh: 1.05, bSize: 10.5 });
T.takeaway(p, s, "When a vendor removes your cheap option, the saving has to come from the product instead. Shorter replies are the lever you still control.", { icon: "₹" });
T.foot(s, ...FT);

/* 13 */ s = T.slideL(p, "Pronunciation dictionaries", "Bulbul + Saaras");
T.compare(p, s,
  { icon: "→", title: "What breaks without one", color: C.RED, items: [
    "₹1,20,000 read as \"one two zero zero zero zero\"",
    "IRDAI spelled out letter by letter, badly",
    "Bhubaneswar, Thiruvananthapuram, Kozhikode",
    "Your own brand name, mispronounced on every call",
    "Scheme names: PM-KISAN, Ayushman Bharat, MGNREGA",
    "Product SKUs and model numbers",
  ]},
  { icon: "✓", title: "How to use them", color: C.TEAL, items: [
    "Create a dictionary via the API (v2)",
    "Attach it to your TTS or STT calls",
    "Works both directions — output and recognition",
    "sarvam_pronunciation_create / list / get / delete via MCP",
    "Start with the twenty terms your domain uses most",
    "Test with a native speaker, not with your own ear",
  ]},
  { y: 1.7, h: 3.5, size: 11.5 });
T.takeaway(p, s, "This is the unglamorous work that separates a demo from a product. Nobody notices a correct pronunciation. Everybody notices a wrong one.");
T.foot(s, ...FT);

/* 14 */ s = T.sectionSlide(p, { num: "C", title: "The language layer", subtitle: "Translate, transliterate, detect — and one silent failure" });

/* 15 */ s = T.slideL(p, "Mayura or Sarvam-Translate?", "Choosing");
T.compare(p, s,
  { icon: "M", title: "Mayura v1", color: C.SAF, items: [
    "11 languages (10 Indic + English)",
    "Tuned quality, strong context preservation",
    "₹20 per 10K characters",
    "Model ID: mayura:v1",
    "Choose when your languages are covered and quality matters most",
    "Supports output_script properly",
  ]},
  { icon: "S", title: "Sarvam-Translate v1", color: C.TEAL, items: [
    "23 languages (22 Indic + English)",
    "Open weights — released June 2025",
    "₹20 per 10K characters — same price",
    "Model ID: sarvam-translate:v1",
    "Choose when you need the wider coverage",
    "WARNING: output_script is silently ignored here",
  ]},
  { y: 1.7, h: 3.3, size: 11.5 });
T.rows(p, s, [
  { icon: "!", title: "Registers matter more than people expect", body: "Colloquial · modern · classical · formal. A government notice translated in a colloquial register reads like a WhatsApp forward. Same API, completely different product.", color: C.RED },
], { y: 5.15, rh: 1.0 });
T.foot(s, ...FT);

/* 16 */ s = T.slideD(p, "The silent failure worth memorising", "Gotcha");
T.code(p, s, { y: 1.6, h: 3.05, ls: 13.5, size: 10, label: "RETURNS HTTP 200. RETURNS THE WRONG THING.",
  code: `resp = client.text.translate(\n    input="What is my EMI due date?",\n    source_language_code="en-IN",\n    target_language_code="hi-IN",\n    model="sarvam-translate:v1",\n    output_script="roman",     # <- SILENTLY IGNORED on this model\n)\n\n# You expected: mera EMI due date kya hai\n# You received: मेरा EMI due date क्या है\n# Status code:  200 OK` });
T.rows(p, s, [
  { icon: "1", title: "Why this class of bug is the dangerous one", body: "An exception you fix in five minutes. A 200 response with subtly wrong output ships to production and is discovered by a customer.", color: C.RED },
  { icon: "2", title: "This is exactly what Agent Skills exist to prevent", body: "npx skills add sarvamai/skills — the translate skill encodes precisely this. Your AI assistant then stops writing it.", color: C.TEAL },
], { y: 4.85, rh: 0.95, dark: true });

/* 17 */ s = T.slideL(p, "Transliterate and Language ID", "The quiet workhorses");
T.cards(p, s, [
  { icon: "→", title: "Transliterate — ₹20/10K", body: "Script conversion preserving pronunciation. Devanagari to Roman and back. Unglamorous and constantly needed." },
  { icon: "★", title: "Where transliteration wins", body: "Search across scripts. Name matching for KYC. Roman-script UIs. Databases that cannot store Unicode Indic. Legacy system integration." },
  { icon: "?", title: "Language ID — ₹3.50/10K", body: "Returns the language AND the script. Auto-detects on multilingual and code-switched input.", color: C.TEAL },
  { icon: "⚡", title: "Use LID as a router", body: "At ₹3.50 per 10,000 characters it is cheap enough to run on every inbound message and route to the right pipeline. Most people forget it exists.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 2.2, bSize: 10.5 });
T.code(p, s, { y: 4.15, h: 1.55, label: "THE AUTO-ROUTING PATTERN — lab 3",
  code: `lang = client.text.identify_language(input=msg).language_code   # ₹0.0035\nreply_en = my_agent(translate_to_english(msg))\nreply = client.text.translate(input=reply_en, target_language_code=lang)` });
T.foot(s, ...FT);

/* 18 */ s = T.analogy(p, { kicker: "A way to think about it", symbol: "Σ", symSize: 82,
  title: "The five-in-one spice box",
  story: "Every Indian kitchen has a masala dabba — one round tin, five or six small bowls inside, one spoon.\n\nIt is not five separate containers because you never use just one. You reach in, take a pinch of this and that, and the combination is the dish.\n\nSaaras, Bulbul, Mayura, Transliterate and Language ID are the same shape.\n\nNobody ships a product that only transcribes. You detect, translate, respond, synthesise. The value is in the combination, not any single tin.",
  punch: "Which is why the lab is one script that touches all of them, rather than five scripts that each touch one. Learn the dabba, not the individual spice." });

/* 19 */ s = T.slideL(p, "The cost of everything in this segment", "₹ summary");
T.table(p, s, { y: 1.65, headers: ["Service", "Price", "Unit", "In practice"],
  colW: [3.2, 2.2, 2.6, 4.093],
  rows: [
    ["Speech to Text", "₹30", "per hour", "₹0.0083 per second, billed per second"],
    ["STT + diarization", "₹45", "per hour", "Only when you need who-said-what"],
    ["STT + translate", "₹30", "per hour", "Same price as transcribe"],
    ["Sarvam Translate v1", "₹20", "per 10K chars", "₹0.002 per character"],
    ["Mayura v1", "₹20", "per 10K chars", "Same price, narrower coverage"],
    ["Transliterate", "₹20", "per 10K chars", ""],
    ["Language ID", "₹3.50", "per 10K chars", "Cheap enough to run on everything"],
    ["Bulbul v2 TTS", "₹15", "per 10K chars", "The margin choice"],
    ["Bulbul v3 TTS", "₹30", "per 10K chars", "Beta pricing"],
  ], rowH: 0.32, size: 10.5 });
T.takeaway(p, s, "Your whole lab today: roughly ₹4.20. Everything is billed per second or per character and rounded up per request — so batch your calls.", { icon: "₹" });
T.foot(s, ...FT);

/* 20 */ s = T.slideD(p, "Before we break", "Checkpoint");
T.rows(p, s, [
  { icon: "✓", title: "You have run every speech and language API", body: "Language ID, translate, transliterate, TTS, STT across five modes. On your own key, against your own audio." },
  { icon: "✓", title: "You know what each one costs", body: "And you have a cost_report() helper you will reuse for the rest of the session.", color: C.TEAL },
  { icon: "!", title: "You have seen two silent failures", body: "Missing sample_rate on telephony audio, and output_script ignored on sarvam-translate. Both return HTTP 200.", color: C.RED },
  { icon: "→", title: "Next: Indus, the agentic platform", body: "We move from calling APIs to deploying agents. Ten-minute break — be back at 5:15.", color: C.TEAL },
], { y: 1.75, rh: 1.02, dark: true, bSize: 10.5 });
T.takeaway(p, s, "Drop your generated audio file in chat before you go. I want to see how many languages this room covers.", { dark: true, y: 6.15, icon: "♪" });

p.writeFile({ fileName: "03_Speech_and_Language_APIs.pptx" }).then(f => console.log("OK", f));
