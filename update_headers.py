import os
import re

# CSS Block with Mobile Responsiveness & Trigger Styling
CSS_BLOCK = """<style>
    .boxcar-header .c-box { display: flex; justify-content: space-between; align-items: center; width: 100%; }
    .boxcar-header .st-logo { display: flex; justify-content: flex-start; align-items: center; width: 100%; margin-bottom: 10px; }
    .boxcar-header .st-logo img { max-width: 260px; width: 100%; height: auto; display: block; margin: 0 auto; }
    .boxcar-header .nav-out-bar { width: 100%; display: flex; justify-content: flex-end; align-items: center; }
    .boxcar-header .right-box { display: flex; justify-content: center; align-items: center; }
    
    /* Navigation Spacing Fix */
    .boxcar-header .main-menu .navigation > li,
    .sticky-header .main-menu .navigation > li {
        margin-left: 15px !important;
        margin-right: 15px !important;
    }

    /* Sticky Header Styling */
    .sticky-header {
        padding: 5px 50px;
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .sticky-header .main-menu .navigation > li > a { color: #ffffff !important; }
    .sticky-header .logo img { max-height: unset !important; max-width: 260px !important; height: auto !important; width: 100%; }
    .sticky-header .nav-out-bar { display: flex; justify-content: flex-end; align-items: center; }

    /* Mobile Navigation Styling */
    .mobile-navigation { display: none; margin-left: auto; align-items: center; }
    .mobile-navigation a { display: flex; align-items: center; }
    
    /* Sidebar (Mobile Menu) Styling */
    .mm-navbar__title { display: none !important; } /* Hide "Menu" text */
    .mm-logo-header img { filter: brightness(0); } /* Make sidebar logo black */
    
    /* Fix Dropdown Arrows Alignment (Inventory Filters) */
    .drop-menu .select {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding-right: 15px;
    }
    
    /* Fix Inventory Sidebar "More Filter" Overlap & Width */
    .wrap-fixed-sidebar {
        position: fixed !important; /* Ensure fixed positioning */
        z-index: 2147483647 !important; /* MAX INT to ensure top-most */
        top: 0; left: 0; right: 0; bottom: 0;
        display: none; /* KEY FIX: Hide by default */
        visibility: hidden;
        pointer-events: none;
    }
    .wrap-fixed-sidebar.active {
        display: block !important;
        visibility: visible !important;
        pointer-events: auto !important;
    }
    .widget-sidebar-filter {
        width: 300px !important; /* Further reduced from 320px */
        max-width: 85vw !important;
        right: auto !important; 
        left: 0 !important; /* Move to Left to match Mobile Menu UI */
        position: fixed !important;
        z-index: 2147483647 !important;
        background-color: #ffffff !important; /* Ensure Opaque Background */
        overflow-y: auto !important; /* Ensure scrollable */
    }

    /* Sidebar Width Override - FURTHER REDUCED */
    .mm-menu { 
        width: 65% !important; 
        max-width: 260px !important; /* SIGNIFICANTLY REDUCED WIDTH */
        background-color: #ffffff !important; /* Fix Transparency */
        z-index: 99999999 !important; /* Fix Z-Index Overlap */
    }
    .mm-panels, .mm-panel {
        background-color: #ffffff !important; /* Ensure Panels are White */
    }

    /* Reduce Navbar Gap (User Request) */
    .mm-navbar {
        height: auto !important;
        min-height: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        line-height: normal !important;
    }

    /* RESPONSIVE LOGIC: Desktop ONLY above 1040px */
    @media (min-width: 1041px) {
        .boxcar-header .nav-out-bar, .sticky-header .nav-out-bar { display: flex !important; }
        /* FORCE NAV CONTENT TO SHOW: Overrides theme hiding logic */
        .boxcar-header .nav-out-bar .nav, .sticky-header .nav-out-bar .nav { display: block !important; }
        .boxcar-header .main-menu, .sticky-header .main-menu { display: block !important; }
        
        .mobile-navigation { display: none !important; }
        .boxcar-header .st-logo img { max-width: 260px; }
        
        /* Ensure right-box is visible on desktop */
        .boxcar-header .right-box { display: flex !important; }
    }

    /* RESPONSIVE LOGIC: Mobile/Tablet at 1040px or less */
    @media (max-width: 1040px) {
        .boxcar-header .st-logo img { max-width: 180px; }
        .sticky-header .logo img { max-width: 180px !important; }
        
        /* Hide Desktop Nav */
        .boxcar-header .nav-out-bar, .sticky-header .nav-out-bar { display: none !important; }
        
        /* FIX: Show Right Box BUT hide everything except Hamburger */
        .boxcar-header .right-box { display: flex !important; align-items: center !important; }
        .boxcar-header .right-box > * { display: none !important; } 
        .boxcar-header .right-box > .mobile-navigation { display: flex !important; margin-left: auto !important; }

        /* Show Hamburger */
        .mobile-navigation { display: flex !important; }
        
        .sticky-header { padding: 5px 20px !important; }
    }
    
    @media (max-width: 575px) {
        .boxcar-header .st-logo img { max-width: 140px; }
        .sticky-header .logo img { max-width: 140px !important; }
    }
</style>"""

# Mobile Trigger HTML Template (3-Line White Hamburger)
MOBILE_TRIGGER_HTML = """<div class="mobile-navigation">
                            <a href="#nav-mobile" title="">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M3 12H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M3 6H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M3 18H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </a>
                        </div>"""

# Sticky Header HTML Template (with 3-Line Mobile Trigger)
STICKY_HTML = """
            <!-- Sticky Header -->
            <div class="sticky-header">
                <div class="inner-container">
                    <div class="c-box">
                        <div class="logo">
                            <a href="index.html"><img src="{img_prefix}images/logo.svg" alt="First Stop Motors"></a>
                        </div>
                        <div class="nav-out-bar">
                            <nav class="nav main-menu">
                                <ul class="navigation" id="navbar">
                                    <li><a href="index.html"><span>Home</span></a></li>
                                    <li><a href="about.html"><span>About</span></a></li>
                                    <li><a href="inventory-list-01.html"><span>Inventory</span></a></li>
                                    <li><a href="trade-in.html"><span>Trade-In</span></a></li>
                                    <li><a href="contact.html"><span>Contact</span></a></li>
                                </ul>
                            </nav>
                        </div>
                        <!-- Mobile Trigger for Sticky Header -->
                        <div class="mobile-navigation">
                            <a href="#nav-mobile" title="">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M3 12H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M3 6H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M3 18H21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            <!-- End Sticky Header -->
"""

# JS to inject logo into mobile menu (MMENU)
MOBILE_LOGO_SCRIPT = """
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        // Wait for mmenu to initialize
        setTimeout(function() {{
            var mmenu = document.querySelector(".mm-menu");
            if (mmenu && !mmenu.querySelector(".mm-logo-header")) {{
                var logoDiv = document.createElement("div");
                logoDiv.className = "mm-logo-header";
                logoDiv.className = "mm-logo-header";
                logoDiv.style.textAlign = "left"; 
                logoDiv.style.display = "flex"; // Use Flexbox
                logoDiv.style.justifyContent = "flex-start"; // Force Left
                logoDiv.style.alignItems = "center";
                logoDiv.style.padding = "70px 0px 20px 20px"; // Top 70, Bottom 20, Left 20
                logoDiv.innerHTML = '<img src="{img_prefix}images/logo.svg" style="max-width: 180px; height: auto; display: block;" alt="Logo">';
                // Insert at the top of the menu panel
                var panel = mmenu.querySelector(".mm-panel");
                if (panel) {{
                    panel.insertBefore(logoDiv, panel.firstChild);
                }}
            }}
        }}, 1000); // Delay to ensure mmenu is ready

        // REMOVE mm-wrapper_opening CLASS (User Request)
        // This class manages the opening animation but user wants it gone
        var observer = new MutationObserver(function(mutations) {{
            mutations.forEach(function(mutation) {{
                if (mutation.attributeName === "class") {{
                    var target = mutation.target;
                    if (target.classList.contains("mm-wrapper_opening")) {{
                        target.classList.remove("mm-wrapper_opening");
                        // console.log("Removed mm-wrapper_opening from", target);
                    }}
                }}
            }});
        }});
        
        // Observe html and body and wrapper
        observer.observe(document.documentElement, {{ attributes: true }});
        observer.observe(document.body, {{ attributes: true }});
        // Also check initial state
        document.documentElement.classList.remove("mm-wrapper_opening");
        document.body.classList.remove("mm-wrapper_opening");
    }});
</script>
"""

SIDEBAR_MOVE_SCRIPT = """
<script>
    document.addEventListener("DOMContentLoaded", function() {
        var sidebar = document.querySelector(".wrap-fixed-sidebar");
        if (sidebar && document.body) {
            document.body.appendChild(sidebar);
        }
    });
</script>
"""

IGNORE_DIRS = [".git", ".gemini", "node_modules", ".vscode", "backups", "css", "js", "images", "fonts", "webfonts"]

def update_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    original_content = content
    filename = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, os.getcwd())
    depth = rel_path.count(os.sep)
    prefix = "../" * depth if depth > 0 else ""
    
    # 1. Update CSS
    content = re.sub(r'<style>.*?\.boxcar-header \.c-box.*?</style>', '', content, flags=re.DOTALL)
    if "<body>" in content:
        content = content.replace("<body>", CSS_BLOCK + "\n<body>")
    
    # 2. Update Sticky Header
    content = re.sub(r'<!-- Sticky Header -->.*?<!-- End Sticky Header -->', '', content, flags=re.DOTALL)
    
    my_sticky_html = STICKY_HTML.format(img_prefix=prefix)
    if depth > 0:
        my_sticky_html = my_sticky_html.replace('href="', 'href="' + prefix)
        my_sticky_html = my_sticky_html.replace('href="' + prefix + '#nav-mobile"', 'href="#nav-mobile"')

    if "</header>" in content:
        content = content.replace("</header>", my_sticky_html + "\n</header>")

    # 3. Inject Main Header Mobile Trigger 
    # Logic: Look for existing trigger (2-line or 3-line) or missing one.
    
    main_part_end = content.find('<!-- Sticky Header -->')
    if main_part_end == -1: main_part_end = len(content)
    main_part = content[:main_part_end]
    
    # Check if we already have a mobile trigger. 
    if '<div class="mobile-navigation">' in main_part:
        # Regex to match the block and replace only first occurence
        trigger_regex = r'<div class="mobile-navigation">\s*<a href="#nav-mobile".*?</a>\s*</div>'
        trigger_search = re.search(trigger_regex, main_part, re.DOTALL)
        if trigger_search:
            old_str = trigger_search.group(0)
            new_str = MOBILE_TRIGGER_HTML
            content = content.replace(old_str, new_str, 1)
            # print(f"Updated Main Mobile Trigger to White in {filename}")
    else:
        # If missing, inject it.
        match = re.search(r'(<div class="nav-out-bar">.*?</div>)(\s*</div>)', content, re.DOTALL)
        if match:
             trigger = MOBILE_TRIGGER_HTML 
             content = content.replace(match.group(0), match.group(1) + trigger + match.group(2), 1)
             print(f"Injected Main Mobile Trigger in {filename}")

    # REMOVE LEGACY HAMBURGER (To match Homepage)
    # Regex to remove div.hamburger block
    content = re.sub(r'<div class="hamburger" id="hamburger-menu".*?</div>', '', content, flags=re.DOTALL)

    # 3. Clean UP: Remove ANY existing instances of our custom scripts to prevent duplicates
    # This matches the Sidebar Move script pattern
    content = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{\s*var sidebar = document\.querySelector\("\.wrap-fixed-sidebar"\);[\s\S]*?\}\);\s*</script>', '', content)
    
    # This matches the Mobile Logo script pattern (start of it - reliable signature)
    content = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded", function\(\) \{\s*// Wait for mmenu to initialize[\s\S]*?\}\);\s*</script>', '', content)
    
    # 4. Inject Scripts (Once)
    # Prepare scripts with prefixes
    my_sidebar_script = SIDEBAR_MOVE_SCRIPT
    my_logo_script = MOBILE_LOGO_SCRIPT.format(img_prefix=prefix)
    
    scripts_to_inject = ""
    
    # Check if Sidebar Move Script is needed
    if 'class="wrap-fixed-sidebar"' in content or "widget-sidebar-filter" in content:
        scripts_to_inject += "\n" + my_sidebar_script
        
    # Always inject Logo Script (unless explicitly unwanted, but we want it everywhere)
    scripts_to_inject += "\n" + my_logo_script

    if "</body>" in content:
        content = content.replace("</body>", scripts_to_inject + "\n</body>")
    else:
        content += scripts_to_inject

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
    else:
        print(f"No changes needed for {filename}")

count = 0
for root, dirs, files in os.walk(os.getcwd()):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    for file in files:
        if file.endswith(".html"):
            update_file(os.path.join(root, file))
            count += 1

print(f"Processed {count} files.")
