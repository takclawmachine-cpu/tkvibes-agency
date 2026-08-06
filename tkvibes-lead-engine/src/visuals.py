"""Category → visual config mapping: color schemes, icons, services, taglines."""

# ── Category keyword → visual config ─────────────────────────────────────────

VISUAL_CONFIG = {
    # ── Medical / Dental ──
    "dental": {
        "primary": "#8b5cf6", "secondary": "#a78bfa",
        "icon": "fa-tooth", "icon_hero": "fa-tooth",
        "tagline": "Your Smile Deserves The Best Care",
        "services": [
            ("fa-teeth", "Dental Implants", "Advanced implant solutions for a confident smile"),
            ("fa-teeth-open", "Root Canal", "Painless root canal treatment with modern techniques"),
            ("fa-star-of-life", "Teeth Whitening", "Professional whitening for a brighter smile"),
            ("fa-braces", "Braces & Aligners", "Orthodontic solutions for perfectly aligned teeth"),
        ],
        "why_items": [
            ("Trusted & Safe", "Sterilized equipment, strict hygiene protocols"),
            ("Flexible Hours", "Open 7 days a week, morning and evening slots"),
            ("Affordable Care", "Premium treatments at honest prices"),
        ],
        "meta_suffix": "Dental Care",
    },
    "dentist": {"_inherit": "dental"},
    "clinic": {
        "primary": "#0ea5e9", "secondary": "#38bdf8",
        "icon": "fa-stethoscope", "icon_hero": "fa-hospital",
        "tagline": "Expert Care When You Need It Most",
        "services": [
            ("fa-notes-medical", "General Checkup", "Comprehensive health checkups"),
            ("fa-heart-pulse", "Specialist Consultation", "Expert consultations with top specialists"),
            ("fa-flask", "Diagnostic Tests", "Advanced on-site diagnostic facilities"),
            ("fa-truck-medical", "Emergency Care", "24/7 emergency medical services"),
        ],
        "why_items": [
            ("Expert Team", "Qualified doctors with years of experience"),
            ("Modern Equipment", "State-of-the-art diagnostic technology"),
            ("Patient First", "Compassionate care in a comfortable environment"),
        ],
        "meta_suffix": "Medical Care",
    },
    "medical": {"_inherit": "clinic"},
    "doctor": {"_inherit": "clinic"},
    "hospital": {
        "primary": "#0ea5e9", "secondary": "#06b6d4",
        "icon": "fa-hospital", "icon_hero": "fa-hospital-user",
        "tagline": "Comprehensive Healthcare Under One Roof",
        "services": [
            ("fa-notes-medical", "OPD Services", "Outpatient consultations across all departments"),
            ("fa-heart-pulse", "Cardiology", "Heart care with advanced diagnostic equipment"),
            ("fa-brain", "Neurology", "Expert neurological care and treatment"),
            ("fa-bone", "Orthopedics", "Complete orthopedic solutions from diagnosis to recovery"),
        ],
        "why_items": [
            ("Multi-Specialty", "All departments under one roof"),
            ("24/7 Emergency", "Round-the-clock emergency services"),
            ("Advanced Technology", "Latest medical equipment and techniques"),
        ],
        "meta_suffix": "Healthcare",
    },
    # ── Legal ──
    "lawyer": {
        "primary": "#1e40af", "secondary": "#3b82f6",
        "icon": "fa-scale-balanced", "icon_hero": "fa-gavel",
        "tagline": "Justice. Experience. Results.",
        "services": [
            ("fa-file-signature", "Legal Consultation", "Expert legal advice for your case"),
            ("fa-gavel", "Court Representation", "Skilled representation in all courts"),
            ("fa-file-contract", "Documentation", "Comprehensive legal documentation"),
            ("fa-handshake", "Corporate Law", "Legal solutions for businesses"),
        ],
        "why_items": [
            ("Experienced Team", "Decades of combined legal experience"),
            ("Proven Results", "Track record of successful case outcomes"),
            ("Client Focused", "Personalized attention to every case"),
        ],
        "meta_suffix": "Legal Services",
    },
    "law firm": {"_inherit": "lawyer"},
    "advocate": {"_inherit": "lawyer"},
    "attorney": {"_inherit": "lawyer"},
    "solicitor": {"_inherit": "lawyer"},
    # ── Veterinary ──
    "veterinary": {
        "primary": "#059669", "secondary": "#34d399",
        "icon": "fa-paw", "icon_hero": "fa-dog",
        "tagline": "Caring For Your Furry Family Members",
        "services": [
            ("fa-syringe", "Vaccinations", "Complete vaccination schedules for pets"),
            ("fa-heart-pulse", "Health Checkups", "Regular wellness examinations"),
            ("fa-tooth", "Dental Care", "Pet dental hygiene and treatment"),
            ("fa-scissors", "Grooming", "Professional pet grooming services"),
        ],
        "why_items": [
            ("Loving Care", "Gentle, patient approach to every pet"),
            ("Expert Vets", "Qualified veterinarians with years of experience"),
            ("Modern Facility", "Clean, comfortable clinic environment"),
        ],
        "meta_suffix": "Pet Care",
    },
    "pet clinic": {"_inherit": "veterinary"},
    "veterinarian": {"_inherit": "veterinary"},
    "vet": {"_inherit": "veterinary"},
    # ── Specialty Medical ──
    "orthopedic": {
        "primary": "#0891b2", "secondary": "#22d3ee",
        "icon": "fa-bone", "icon_hero": "fa-person-walking",
        "tagline": "Move Freely. Live Pain-Free.",
        "services": [
            ("fa-x-ray", "Joint Replacement", "Advanced knee, hip and shoulder replacements"),
            ("fa-bone", "Fracture Care", "Expert fracture treatment and management"),
            ("fa-person-walking", "Physiotherapy", "Post-surgery rehabilitation and physio"),
            ("fa-spa", "Pain Management", "Non-surgical pain relief treatments"),
        ],
        "why_items": [
            ("Expert Surgeons", "Leading orthopedic specialists"),
            ("Advanced Techniques", "Minimally invasive surgical options"),
            ("Full Recovery", "Comprehensive post-op rehabilitation"),
        ],
        "meta_suffix": "Orthopedic Care",
    },
    "skin clinic": {
        "primary": "#d946ef", "secondary": "#e879f9",
        "icon": "fa-hand-sparkles", "icon_hero": "fa-spa",
        "tagline": "Reveal Your Natural Radiance",
        "services": [
            ("fa-hand-sparkles", "Skin Treatment", "Expert dermatological treatments"),
            ("fa-spa", "Laser Therapy", "Advanced laser skin treatments"),
            ("fa-face-smile", "Anti-Aging", "Rejuvenation and anti-aging solutions"),
            ("fa-droplet", "Acne Care", "Effective acne treatment and scar removal"),
        ],
        "why_items": [
            ("Expert Dermatologists", "Qualified skin specialists"),
            ("Advanced Technology", "Latest dermatological equipment"),
            ("Personalized Care", "Custom treatment plans for every skin type"),
        ],
        "meta_suffix": "Skin Care",
    },
    "dermatologist": {"_inherit": "skin clinic"},
    "cosmetic": {
        "primary": "#ec4899", "secondary": "#f472b6",
        "icon": "fa-wand-magic-sparkles", "icon_hero": "fa-spa",
        "tagline": "Enhance Your Natural Beauty",
        "services": [
            ("fa-face-smile", "Facial Aesthetics", "Non-surgical facial rejuvenation"),
            ("fa-wand-magic-sparkles", "Laser Treatments", "Advanced laser cosmetic procedures"),
            ("fa-droplet", "Skin Rejuvenation", "Skin resurfacing and renewal treatments"),
            ("fa-syringe", "Injectables", "Botox, fillers and advanced injectables"),
        ],
        "why_items": [
            ("Expert Practitioners", "Certified cosmetic specialists"),
            ("Safe Procedures", "Highest safety standards and protocols"),
            ("Natural Results", "Subtle, natural-looking enhancements"),
        ],
        "meta_suffix": "Cosmetic Treatments",
    },
    "eye clinic": {
        "primary": "#0284c7", "secondary": "#38bdf8",
        "icon": "fa-eye", "icon_hero": "fa-glasses",
        "tagline": "Clear Vision For a Brighter Future",
        "services": [
            ("fa-eye", "Eye Exams", "Comprehensive vision testing"),
            ("fa-glasses", "Contact Lenses", "Professional contact lens fitting"),
            ("fa-microscope", "Laser Surgery", "LASIK and advanced vision correction"),
            ("fa-hospital", "Cataract Surgery", "Modern cataract removal and lens replacement"),
        ],
        "why_items": [
            ("Expert Ophthalmologists", "Experienced eye surgeons"),
            ("Modern Technology", "Advanced diagnostic and surgical equipment"),
            ("Comprehensive Care", "From routine exams to complex surgery"),
        ],
        "meta_suffix": "Eye Care",
    },
    "ophthalmologist": {"_inherit": "eye clinic"},
    "physiotherapy": {
        "primary": "#0d9488", "secondary": "#2dd4bf",
        "icon": "fa-person-walking", "icon_hero": "fa-heart-pulse",
        "tagline": "Restore Movement. Reclaim Your Life.",
        "services": [
            ("fa-person-walking", "Sports Therapy", "Sport injury recovery and prevention"),
            ("fa-spa", "Massage Therapy", "Therapeutic massage for pain relief"),
            ("fa-bone", "Joint Therapy", "Joint mobility and strength restoration"),
            ("fa-heart-pulse", "Cardio Rehab", "Cardiac rehabilitation programs"),
        ],
        "why_items": [
            ("Licensed Therapists", "Certified and experienced physiotherapists"),
            ("Personalized Plans", "Custom treatment programs for each patient"),
            ("Proven Results", "Track record of successful recoveries"),
        ],
        "meta_suffix": "Physiotherapy",
    },
    "physiotherapist": {"_inherit": "physiotherapy"},
    "pediatric": {
        "primary": "#f59e0b", "secondary": "#fbbf24",
        "icon": "fa-child", "icon_hero": "fa-baby",
        "tagline": "Gentle Care For Little Champions",
        "services": [
            ("fa-stethoscope", "Wellness Checkups", "Regular health monitoring for children"),
            ("fa-syringe", "Vaccinations", "Complete immunization schedules"),
            ("fa-heart-pulse", "Developmental Care", "Growth and development monitoring"),
            ("fa-kit-medical", "Pediatric Care", "Expert treatment for childhood illnesses"),
        ],
        "why_items": [
            ("Child-Friendly", "Gentle, welcoming environment for kids"),
            ("Expert Pediatricians", "Specialized children's healthcare"),
            ("Parent Support", "Guidance and support for parents"),
        ],
        "meta_suffix": "Pediatric Care",
    },
    "cardiology": {
        "primary": "#dc2626", "secondary": "#ef4444",
        "icon": "fa-heart-pulse", "icon_hero": "fa-heart",
        "tagline": "Your Heart. Our Mission.",
        "services": [
            ("fa-heart-pulse", "Heart Checkups", "Comprehensive cardiac evaluations"),
            ("fa-heart", "ECG & Echo", "Advanced cardiac diagnostic tests"),
            ("fa-stethoscope", "Cardiology Consult", "Expert cardiologist consultations"),
            ("fa-truck-medical", "Emergency Care", "24/7 cardiac emergency services"),
        ],
        "why_items": [
            ("Top Cardiologists", "Leading heart specialists"),
            ("Advanced Diagnostics", "State-of-the-art cardiac equipment"),
            ("Comprehensive Care", "From prevention to surgery and recovery"),
        ],
        "meta_suffix": "Cardiac Care",
    },
    "fertility": {
        "primary": "#db2777", "secondary": "#f472b6",
        "icon": "fa-baby", "icon_hero": "fa-hand-holding-heart",
        "tagline": "Helping You Build Your Family",
        "services": [
            ("fa-hand-holding-heart", "IVF Treatment", "Advanced IVF and fertility treatments"),
            ("fa-flask", "Fertility Testing", "Comprehensive fertility assessments"),
            ("fa-stethoscope", "Consultation", "Expert fertility counseling and guidance"),
            ("fa-baby", "Fertility Preservation", "Egg/sperm freezing and preservation"),
        ],
        "why_items": [
            ("Expert Specialists", "Leading fertility doctors"),
            ("High Success Rate", "Proven track record of successful pregnancies"),
            ("Emotional Support", "Compassionate care throughout your journey"),
        ],
        "meta_suffix": "Fertility Care",
    },
    # ── Professional Services ──
    "interior designer": {
        "primary": "#7c3aed", "secondary": "#a78bfa",
        "icon": "fa-pen-ruler", "icon_hero": "fa-couch",
        "tagline": "Designing Spaces That Inspire",
        "services": [
            ("fa-couch", "Residential Design", "Beautiful home interiors tailored to your style"),
            ("fa-building", "Commercial Design", "Professional office and retail spaces"),
            ("fa-pen-ruler", "Consultation", "Expert design consultation and planning"),
            ("fa-paint-roller", "Renovation", "Complete home renovation and makeovers"),
        ],
        "why_items": [
            ("Creative Vision", "Unique design concepts for every space"),
            ("End-to-End Service", "From concept to completion"),
            ("Client-First", "Your vision, our expertise"),
        ],
        "meta_suffix": "Interior Design",
    },
    "architect": {
        "primary": "#4338ca", "secondary": "#6366f1",
        "icon": "fa-draw-polygon", "icon_hero": "fa-building",
        "tagline": "Building Dreams Into Reality",
        "services": [
            ("fa-draw-polygon", "Architectural Design", "Innovative building design and planning"),
            ("fa-building", "Commercial Projects", "Professional and commercial architecture"),
            ("fa-house", "Residential Design", "Custom home design and planning"),
            ("fa-ruler-combined", "Interior Design", "Integrated interior architecture"),
        ],
        "why_items": [
            ("Award-Winning Team", "Recognized for design excellence"),
            ("Sustainable Design", "Eco-friendly and energy-efficient solutions"),
            ("Innovation", "Cutting-edge architectural approaches"),
        ],
        "meta_suffix": "Architecture",
    },
    "architecture": {"_inherit": "architect"},
    "chartered accountant": {
        "primary": "#1e40af", "secondary": "#2563eb",
        "icon": "fa-calculator", "icon_hero": "fa-file-invoice-dollar",
        "tagline": "Your Financial Success Partner",
        "services": [
            ("fa-file-invoice-dollar", "Tax Planning", "Expert tax planning and filing"),
            ("fa-calculator", "Accounting", "Comprehensive accounting services"),
            ("fa-chart-line", "Financial Advisory", "Strategic financial planning"),
            ("fa-handshake", "Business Setup", "Company registration and compliance"),
        ],
        "why_items": [
            ("Trusted Expertise", "Years of financial experience"),
            ("Compliance Focus", "Stay compliant with latest regulations"),
            ("Client Success", "Dedicated to your financial growth"),
        ],
        "meta_suffix": "CA Services",
    },
    "ca firm": {"_inherit": "chartered accountant"},
    "financial advisor": {
        "primary": "#047857", "secondary": "#10b981",
        "icon": "fa-chart-line", "icon_hero": "fa-coins",
        "tagline": "Secure Your Financial Future",
        "services": [
            ("fa-coins", "Investment Planning", "Strategic investment portfolio management"),
            ("fa-chart-line", "Wealth Management", "Comprehensive wealth growth strategies"),
            ("fa-shield", "Risk Management", "Insurance and risk assessment"),
            ("fa-piggy-bank", "Retirement Planning", "Secure retirement planning solutions"),
        ],
        "why_items": [
            ("Experienced Advisors", "Qualified financial professionals"),
            ("Personalized Strategy", "Custom plans for your goals"),
            ("Long-Term Focus", "Sustainable wealth building"),
        ],
        "meta_suffix": "Financial Services",
    },
    "wealth management": {"_inherit": "financial advisor"},
    "insurance": {
        "primary": "#0369a1", "secondary": "#0ea5e9",
        "icon": "fa-shield-halved", "icon_hero": "fa-umbrella",
        "tagline": "Protecting What Matters Most",
        "services": [
            ("fa-car", "Auto Insurance", "Comprehensive vehicle coverage"),
            ("fa-house", "Home Insurance", "Protect your home and belongings"),
            ("fa-heart-pulse", "Health Insurance", "Medical coverage for you and family"),
            ("fa-umbrella", "Life Insurance", "Financial security for your loved ones"),
        ],
        "why_items": [
            ("Best Rates", "Competitive premiums and coverage"),
            ("Quick Claims", "Fast and hassle-free claim processing"),
            ("Expert Guidance", "Professional advice for the right coverage"),
        ],
        "meta_suffix": "Insurance",
    },
    "real estate": {
        "primary": "#b91c1c", "secondary": "#ef4444",
        "icon": "fa-building", "icon_hero": "fa-house-chimney",
        "tagline": "Find Your Dream Property",
        "services": [
            ("fa-house-chimney", "Property Sales", "Expert assistance buying and selling"),
            ("fa-building", "Commercial Property", "Office and retail property solutions"),
            ("fa-handshake", "Property Management", "Full-service property management"),
            ("fa-chart-line", "Investment Advisory", "Real estate investment guidance"),
        ],
        "why_items": [
            ("Local Expertise", "Deep knowledge of the local market"),
            ("Premium Listings", "Curated selection of top properties"),
            ("Trusted Service", "Proven track record of successful deals"),
        ],
        "meta_suffix": "Real Estate",
    },
    "real estate agency": {"_inherit": "real estate"},
    # ── Retail & Hospitality ──
    "boutique": {
        "primary": "#db2777", "secondary": "#f472b6",
        "icon": "fa-bag-shopping", "icon_hero": "fa-shirt",
        "tagline": "Discover Your Unique Style",
        "services": [
            ("fa-shirt", "Fashion Collection", "Curated collection of premium fashion"),
            ("fa-gem", "Accessories", "Handpicked accessories and jewelry"),
            ("fa-truck", "Home Delivery", "Free delivery across the city"),
            ("fa-rotate-left", "Easy Returns", "Hassle-free exchange and returns"),
        ],
        "why_items": [
            ("Curated Collection", "Handpicked premium fashion"),
            ("Personal Styling", "Expert style advice and recommendations"),
            ("Premium Quality", "Only the finest materials and brands"),
        ],
        "meta_suffix": "Fashion Boutique",
    },
    "luxury": {
        "primary": "#d4af37", "secondary": "#fbbf24",
        "icon": "fa-gem", "icon_hero": "fa-crown",
        "tagline": "Experience Unparalleled Luxury",
        "services": [
            ("fa-gem", "Premium Collection", "Exclusive luxury products and services"),
            ("fa-crown", "VIP Service", "Personalized concierge experience"),
            ("fa-truck-fast", "White Glove", "Premium delivery and setup service"),
            ("fa-handshake", "Private Events", "Exclusive private shopping events"),
        ],
        "why_items": [
            ("Exclusive Access", "Limited edition and exclusive items"),
            ("Personalized Service", "Dedicated personal shopper"),
            ("Uncompromising Quality", "Only the finest products"),
        ],
        "meta_suffix": "Luxury Experience",
    },
    "salon": {
        "primary": "#db2777", "secondary": "#f472b6",
        "icon": "fa-scissors", "icon_hero": "fa-wand-magic-sparkles",
        "tagline": "Where Beauty Meets Perfection",
        "services": [
            ("fa-scissors", "Hair Styling", "Expert cuts, colors and styling"),
            ("fa-spa", "Facial Treatments", "Rejuvenating skin care treatments"),
            ("fa-hand-sparkles", "Manicure & Pedicure", "Professional nail care services"),
            ("fa-wand-magic-sparkles", "Bridal Makeup", "Complete bridal beauty packages"),
        ],
        "why_items": [
            ("Expert Stylists", "Trained and experienced professionals"),
            ("Premium Products", "Only the best salon products"),
            ("Relaxing Ambiance", "Luxurious salon experience"),
        ],
        "meta_suffix": "Salon & Spa",
    },
    "spa": {
        "primary": "#0d9488", "secondary": "#14b8a6",
        "icon": "fa-spa", "icon_hero": "fa-hand-sparkles",
        "tagline": "Rejuvenate Your Body & Soul",
        "services": [
            ("fa-spa", "Massage Therapy", "Traditional and therapeutic massages"),
            ("fa-hand-sparkles", "Facial Care", "Luxurious facial treatments"),
            ("fa-droplet", "Body Treatments", "Full body scrubs and wraps"),
            ("fa-hot-tub-person", "Hydrotherapy", "Hydrotherapy and steam treatments"),
        ],
        "why_items": [
            ("Tranquil Environment", "Serene escape from daily stress"),
            ("Expert Therapists", "Trained wellness professionals"),
            ("Holistic Approach", "Mind-body wellness solutions"),
        ],
        "meta_suffix": "Wellness Spa",
    },
    "jewelry": {
        "primary": "#d4af37", "secondary": "#fbbf24",
        "icon": "fa-gem", "icon_hero": "fa-ring",
        "tagline": "Treasures That Last Forever",
        "services": [
            ("fa-ring", "Gold Jewelry", "Exquisite gold jewelry collection"),
            ("fa-gem", "Diamond Collection", "Certified diamond jewelry"),
            ("fa-ruler", "Custom Design", "Bespoke jewelry design service"),
            ("fa-clock", "Watch Collection", "Premium timepiece collection"),
        ],
        "why_items": [
            ("Certified Quality", "BIS hallmarked and certified jewelry"),
            ("Expert Craftsmanship", "Handcrafted by master artisans"),
            ("Trusted Legacy", "Generations of jewelry expertise"),
        ],
        "meta_suffix": "Jewelry",
    },
    "cafe": {
        "primary": "#b45309", "secondary": "#d97706",
        "icon": "fa-mug-saucer", "icon_hero": "fa-mug-hot",
        "tagline": "Brewing Happiness Every Day",
        "services": [
            ("fa-mug-hot", "Specialty Coffee", "Premium coffee from around the world"),
            ("fa-utensils", "Food Menu", "Freshly prepared meals and snacks"),
            ("fa-cake", "Desserts", "Artisanal cakes and pastries"),
            ("fa-wifi", "Cafe Experience", "Cozy ambiance with free WiFi"),
        ],
        "why_items": [
            ("Premium Coffee", "Expertly roasted and brewed"),
            ("Fresh Ingredients", "Locally sourced, farm-fresh"),
            ("Cozy Ambiance", "Perfect place to relax and work"),
        ],
        "meta_suffix": "Cafe",
    },
    "restaurant": {
        "primary": "#dc2626", "secondary": "#f97316",
        "icon": "fa-utensils", "icon_hero": "fa-utensils",
        "tagline": "An Unforgettable Dining Experience",
        "services": [
            ("fa-utensils", "Fine Dining", "Exquisite multi-course dining experience"),
            ("fa-wine-glass", "Bar & Lounge", "Curated wine and cocktail selection"),
            ("fa-truck", "Home Delivery", "Same-day delivery across the city"),
            ("fa-calendar-check", "Private Events", "Catering for parties and events"),
        ],
        "why_items": [
            ("Award-Winning Chef", "Culinary excellence and creativity"),
            ("Fresh Ingredients", "Farm-to-table freshness guaranteed"),
            ("Ambiance", "Elegant setting for every occasion"),
        ],
        "meta_suffix": "Restaurant",
    },
    "bakery": {
        "primary": "#b45309", "secondary": "#d97706",
        "icon": "fa-cake", "icon_hero": "fa-bread-slice",
        "tagline": "Freshly Baked, Always Loved",
        "services": [
            ("fa-cake", "Artisan Breads", "Handcrafted sourdough, baguettes and more"),
            ("fa-cake", "Custom Cakes", "Bespoke cakes for every celebration"),
            ("fa-cookie", "Pastries & Desserts", "Daily fresh pastries and sweet treats"),
            ("fa-truck", "Home Delivery", "Free delivery on orders above minimum"),
        ],
        "why_items": [
            ("Fresh Daily", "Baked fresh every morning with premium ingredients"),
            ("Artisan Quality", "Traditional recipes with a modern twist"),
            ("Custom Orders", "Personalized cakes and treats for any occasion"),
        ],
        "meta_suffix": "Bakery",
    },
    "cloud kitchen": {
        "primary": "#ea580c", "secondary": "#f97316",
        "icon": "fa-kitchen-set", "icon_hero": "fa-truck-fast",
        "tagline": "Restaurant-Quality Food, Delivered",
        "services": [
            ("fa-kitchen-set", "Multi-Cuisine Menu", "Diverse cuisines from a single kitchen"),
            ("fa-truck-fast", "Fast Delivery", "Quick delivery within 30-45 minutes"),
            ("fa-mobile-screen", "Online Ordering", "Easy ordering via app and website"),
            ("fa-utensils", "Meal Plans", "Weekly subscription meal plans available"),
        ],
        "why_items": [
            ("Chef-Quality", "Restaurant-grade food at affordable prices"),
            ("Hygiene First", "Strict hygiene and safety protocols"),
            ("Convenience", "Order from anywhere, delivered to your door"),
        ],
        "meta_suffix": "Cloud Kitchen",
    },
    "caterer": {
        "primary": "#7c2d12", "secondary": "#b45309",
        "icon": "fa-utensils", "icon_hero": "fa-plate-wheat",
        "tagline": "Making Every Event Memorable",
        "services": [
            ("fa-plate-wheat", "Wedding Catering", "Complete wedding feast packages"),
            ("fa-calendar-check", "Corporate Events", "Professional catering for businesses"),
            ("fa-people-group", "Party Packages", "Custom menus for private parties"),
            ("fa-truck", "Full Service", "Setup, serving, and cleanup included"),
        ],
        "why_items": [
            ("Custom Menus", "Tailored menus to match your event theme"),
            ("Experienced Team", "Professional chefs and service staff"),
            ("Hassle-Free", "We handle everything from setup to cleanup"),
        ],
        "meta_suffix": "Catering",
    },
    "brewery": {
        "primary": "#92400e", "secondary": "#d97706",
        "icon": "fa-beer-mug-empty", "icon_hero": "fa-wheat-awn",
        "tagline": "Craft Beer. Great Times.",
        "services": [
            ("fa-beer-mug-empty", "Craft Beers", "Rotating selection of house-brewed beers"),
            ("fa-wheat-awn", "Brewery Tours", "Behind-the-scenes brewery experience"),
            ("fa-utensils", "Food Pairing", "Gourmet food paired with craft brews"),
            ("fa-calendar-check", "Events & Tastings", "Regular tasting events and live music"),
        ],
        "why_items": [
            ("Small Batch", "Handcrafted in small batches for quality"),
            ("Unique Flavors", "Seasonal and experimental brews"),
            ("Community Hub", "A welcoming space for beer lovers"),
        ],
        "meta_suffix": "Brewery",
    },
    "ice cream": {
        "primary": "#be185d", "secondary": "#f472b6",
        "icon": "fa-ice-cream", "icon_hero": "fa-mug-hot",
        "tagline": "Sweet Moments, Made Fresh",
        "services": [
            ("fa-ice-cream", "Premium Ice Cream", "Handmade ice cream with natural ingredients"),
            ("fa-cake", "Ice Cream Cakes", "Custom ice cream cakes for celebrations"),
            ("fa-droplet", "Sundaes & Shakes", "Loaded sundaes and thick milkshakes"),
            ("fa-truck", "Party Orders", "Bulk orders for parties and events"),
        ],
        "why_items": [
            ("Made Fresh", "Small-batch, handcrafted daily"),
            ("Natural Ingredients", "Real fruits, cream, and no artificial flavors"),
            ("Unique Flavors", "Classic favorites and creative seasonal specials"),
        ],
        "meta_suffix": "Ice Cream Parlor",
    },
    "confectionery": {
        "primary": "#db2777", "secondary": "#f472b6",
        "icon": "fa-candy-cane", "icon_hero": "fa-gem",
        "tagline": "Sweet Indulgence, Pure Delight",
        "services": [
            ("fa-candy-cane", "Chocolates", "Handcrafted premium chocolates and truffles"),
            ("fa-cake", "Indian Sweets", "Traditional mithai and confections"),
            ("fa-gem", "Gift Boxes", "Beautifully packaged gift assortments"),
            ("fa-truck", "Custom Orders", "Bespoke confectionery for special occasions"),
        ],
        "why_items": [
            ("Premium Quality", "Finest ingredients, handcrafted with care"),
            ("Traditional Recipes", "Authentic recipes passed down generations"),
            ("Gift-Ready", "Elegant packaging perfect for gifting"),
        ],
        "meta_suffix": "Confectionery",
    },
    "juice bar": {
        "primary": "#16a34a", "secondary": "#22c55e",
        "icon": "fa-glass-water", "icon_hero": "fa-apple-whole",
        "tagline": "Fresh Squeezed. Naturally Good.",
        "services": [
            ("fa-apple-whole", "Fresh Juices", "Cold-pressed fruit and vegetable juices"),
            ("fa-leaf", "Smoothies", "Nutritious smoothie bowls and blends"),
            ("fa-droplet", "Detox Programs", "Custom detox and cleanse programs"),
            ("fa-truck", "Subscription", "Weekly juice delivery subscription"),
        ],
        "why_items": [
            ("100% Fresh", "No preservatives, no added sugar"),
            ("Nutritious", "Packed with vitamins and natural goodness"),
            ("Made to Order", "Every drink prepared fresh when you order"),
        ],
        "meta_suffix": "Juice Bar",
    },
    "food truck": {
        "primary": "#e11d48", "secondary": "#fb7185",
        "icon": "fa-truck", "icon_hero": "fa-truck-fast",
        "tagline": "Gourmet on the Go",
        "services": [
            ("fa-truck", "Daily Menu", "Rotating menu of street food favorites"),
            ("fa-calendar-check", "Event Catering", "Book our food truck for your event"),
            ("fa-location-dot", "Location Tracker", "Real-time location updates on social media"),
            ("fa-utensils", "Custom Orders", "Bulk orders for corporate lunches and events"),
        ],
        "why_items": [
            ("Gourmet Quality", "Restaurant-quality food, mobile convenience"),
            ("Unique Concept", "Creative fusion dishes you won't find elsewhere"),
            ("Follow Us", "Check our social media for daily locations"),
        ],
        "meta_suffix": "Food Truck",
    },
    "gym": {
        "primary": "#dc2626", "secondary": "#ef4444",
        "icon": "fa-dumbbell", "icon_hero": "fa-person-running",
        "tagline": "Transform Your Body. Transform Your Life.",
        "services": [
            ("fa-dumbbell", "Strength Training", "Complete weight training facilities"),
            ("fa-person-running", "Cardio Zone", "Modern cardio equipment"),
            ("fa-users", "Group Classes", "Yoga, Zumba, HIIT and more"),
            ("fa-handshake", "Personal Training", "One-on-one expert coaching"),
        ],
        "why_items": [
            ("Modern Equipment", "State-of-the-art fitness machines"),
            ("Expert Trainers", "Certified fitness professionals"),
            ("Welcoming Community", "Supportive environment for all levels"),
        ],
        "meta_suffix": "Fitness",
    },
    "home services": {
        "primary": "#0ea5e9", "secondary": "#38bdf8",
        "icon": "fa-toolbox", "icon_hero": "fa-house-chimney",
        "tagline": "Your Home, Our Expertise",
        "services": [
            ("fa-bolt", "Electrical", "Expert electrical repairs and installation"),
            ("fa-wrench", "Plumbing", "Professional plumbing services"),
            ("fa-paint-roller", "Painting", "Interior and exterior painting"),
            ("fa-snowflake", "AC Service", "AC repair and maintenance"),
        ],
        "why_items": [
            ("Skilled Professionals", "Trained and verified technicians"),
            ("Same-Day Service", "Quick response and timely service"),
            ("Satisfaction Guaranteed", "Quality workmanship guaranteed"),
        ],
        "meta_suffix": "Home Services",
    },
    "coaching": {
        "primary": "#7c3aed", "secondary": "#a855f7",
        "icon": "fa-chalkboard-user", "icon_hero": "fa-graduation-cap",
        "tagline": "Unlock Your Full Potential",
        "services": [
            ("fa-chalkboard-user", "Academic Coaching", "Expert tutoring across all subjects"),
            ("fa-language", "Language Training", "English, foreign languages and more"),
            ("fa-laptop-code", "Skill Development", "Professional and career skills"),
            ("fa-users", "Group Classes", "Interactive small-group learning"),
        ],
        "why_items": [
            ("Expert Teachers", "Qualified and experienced educators"),
            ("Personalized Attention", "Custom learning plans for each student"),
            ("Proven Results", "Track record of academic excellence"),
        ],
        "meta_suffix": "Coaching",
    },
    "retail": {
        "primary": "#7c3aed", "secondary": "#a78bfa",
        "icon": "fa-store", "icon_hero": "fa-bag-shopping",
        "tagline": "Your One-Stop Shopping Destination",
        "services": [
            ("fa-bag-shopping", "Product Range", "Wide selection of quality products"),
            ("fa-truck", "Fast Delivery", "Free delivery on orders above minimum"),
            ("fa-rotate-left", "Easy Returns", "30-day hassle-free return policy"),
            ("fa-gift", "Loyalty Program", "Rewards and exclusive member benefits"),
        ],
        "why_items": [
            ("Quality Products", "Curated selection of top brands"),
            ("Best Prices", "Competitive pricing and daily deals"),
            ("Customer First", "Exceptional shopping experience"),
        ],
        "meta_suffix": "Retail Store",
    },
}

# ── Default fallback ─────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "primary": "#6366f1", "secondary": "#818cf8",
    "icon": "fa-star", "icon_hero": "fa-building",
    "tagline": "Excellence You Can Trust",
    "services": [
        ("fa-star", "Professional Service", "Top-quality service tailored to your needs"),
        ("fa-handshake", "Trusted Team", "Experienced professionals you can rely on"),
        ("fa-clock", "Always Available", "Convenient hours and easy scheduling"),
        ("fa-thumbs-up", "Satisfaction", "100% satisfaction guaranteed"),
    ],
    "why_items": [
        ("Quality Service", "Commitment to excellence in everything we do"),
        ("Expert Team", "Skilled professionals with years of experience"),
        ("Customer Focus", "Your satisfaction is our top priority"),
    ],
    "meta_suffix": "Services",
}


def get_visual_config(category: str) -> dict:
    """Get the visual config for a business category, with inheritance."""
    cat = (category or "").lower().strip()
    best = None
    best_score = 0

    # Score each keyword by how well it matches the category
    for kw, cfg in VISUAL_CONFIG.items():
        if kw in cat:
            score = len(kw) / len(cat) if cat else 0
            if score > best_score:
                best_score = score
                best = cfg

    if best is None:
        return dict(DEFAULT_CONFIG)

    # Resolve _inherit
    resolved = dict(best)
    while "_inherit" in resolved:
        parent_key = resolved.pop("_inherit")
        parent = VISUAL_CONFIG.get(parent_key, DEFAULT_CONFIG)
        # Merge: parent first, then child overrides
        merged = dict(parent)
        merged.update(resolved)
        merged.pop("_inherit", None)
        resolved = merged

    return resolved


def sanitize_phone(phone: str) -> str:
    """Clean phone number for WhatsApp format (digits only)."""
    if not phone:
        return ""
    digits = "".join(c for c in phone if c.isdigit())
    return digits.lstrip("0")


def format_phone_display(phone: str) -> str:
    """Format phone for display."""
    if not phone:
        return ""
    return phone.strip()


def build_hours_html(hours_str: str) -> str:
    """Convert hours string to HTML rows."""
    if not hours_str:
        return '<div class="hours-row"><span>Hours not listed</span><span>—</span></div>'
    rows = []
    for line in hours_str.split(";"):
        line = line.strip()
        if ":" in line:
            day, _, time = line.partition(":")
            rows.append(
                f'<div class="hours-row"><span>{day.strip()}</span>'
                f'<span>{time.strip()}</span></div>'
            )
    if not rows:
        rows.append(f'<div class="hours-row"><span>Hours</span><span>{hours_str}</span></div>')
    return "\n".join(rows)


def build_services_html(cfg: dict) -> str:
    """Build services HTML grid from visual config."""
    services = cfg.get("services", DEFAULT_CONFIG["services"])
    items = []
    for icon, title, desc in services:
        items.append(f"""<div class="card fade-up">
<div class="service-icon"><i class="fa-solid {icon}"></i></div>
<h3 style="font-size:17px;font-weight:700;margin-bottom:8px">{title}</h3>
<p style="font-size:14px;color:#94a3b8;line-height:1.6">{desc}</p>
</div>""")
    return "\n".join(items)


def get_category_services(category: str) -> str:
    """Get services HTML for a given category."""
    cfg = get_visual_config(category)
    return build_services_html(cfg)


def get_why_items(category: str) -> str:
    """Get 'Why Choose Us' HTML items."""
    cfg = get_visual_config(category)
    items = cfg.get("why_items", DEFAULT_CONFIG["why_items"])
    chunks = []
    for title, desc in items:
        chunks.append(f"""<div class="card fade-up" style="text-align:center">
<div class="service-icon" style="margin:0 auto 16px"><i class="fa-solid fa-shield-halved"></i></div>
<h3 style="font-size:17px;font-weight:700;margin-bottom:8px">{title}</h3>
<p style="font-size:14px;color:#94a3b8;line-height:1.6">{desc}</p>
</div>""")
    return "\n".join(chunks)