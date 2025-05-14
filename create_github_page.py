"""
create_github_page.py - Create a simple GitHub Pages site for your game

This creates a landing page that links to downloadable executables 
rather than trying to run the game in browser.
"""
import os
import shutil
import json

def create_github_pages_site():
    """Create a GitHub Pages compatible site in the docs directory"""
    
    # Create docs directory (GitHub Pages default)
    site_dir = "docs"
    if os.path.exists(site_dir):
        shutil.rmtree(site_dir)
    os.makedirs(site_dir)
    
    # Create assets directory for any images/files we might want
    assets_dir = os.path.join(site_dir, "assets")
    os.makedirs(assets_dir)
    
    # Create index.html with a complete, self-contained page
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Decay - Entropy Game</title>
    <meta name="description" content="A game exploring digital entropy and decay. Battle system deterioration through three unique mini-games.">
    <style>
        :root {
            --healthy-color: #adb47d;
            --warning-color: #dce4aa;
            --decay-color: #799f96;
            --bg-dark: #0a0a0a;
            --bg-darker: #000000;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', Monaco, monospace;
            background: var(--bg-darker);
            color: var(--healthy-color);
            overflow-x: hidden;
            line-height: 1.6;
        }
        
        .noise {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.03;
            background-image: 
                radial-gradient(circle at 25% 25%, var(--healthy-color) 1px, transparent 1px),
                radial-gradient(circle at 75% 75%, var(--decay-color) 1px, transparent 1px);
            background-size: 20px 20px;
            animation: noise 0.2s infinite;
        }
        
        @keyframes noise {
            0% { transform: translate(0, 0); }
            25% { transform: translate(-1px, 1px); }
            50% { transform: translate(1px, -1px); }
            75% { transform: translate(-1px, -1px); }
            100% { transform: translate(1px, 1px); }
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .title {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-shadow: 0 0 10px var(--healthy-color);
            animation: glitch 3s infinite;
        }
        
        @keyframes glitch {
            0%, 90%, 100% { transform: translateX(0); }
            91% { transform: translateX(-2px); }
            92% { transform: translateX(2px); }
            93% { transform: translateX(-2px); }
        }
        
        .subtitle {
            font-size: 1.5rem;
            color: var(--warning-color);
            margin-bottom: 2rem;
        }
        
        .decay-bar {
            width: 100%;
            height: 40px;
            background: var(--bg-dark);
            border: 2px solid var(--healthy-color);
            position: relative;
            margin-bottom: 2rem;
            border-radius: 5px;
            overflow: hidden;
        }
        
        .decay-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--decay-color), var(--warning-color), var(--healthy-color));
            width: 0%;
            animation: decay-animation 10s infinite;
            border-radius: 3px;
        }
        
        @keyframes decay-animation {
            0% { width: 100%; }
            50% { width: 30%; }
            100% { width: 100%; }
        }
        
        .decay-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            color: white;
            font-size: 1.1rem;
        }
        
        .description {
            text-align: center;
            font-size: 1.2rem;
            line-height: 1.8;
            margin-bottom: 3rem;
            color: #cccccc;
        }
        
        .download-section {
            background: var(--bg-dark);
            border: 2px solid var(--healthy-color);
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .download-buttons {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-bottom: 2rem;
        }
        
        .download-btn {
            display: inline-block;
            padding: 1rem 2rem;
            background: var(--bg-darker);
            border: 2px solid var(--healthy-color);
            color: var(--healthy-color);
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 5px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }
        
        .download-btn:hover {
            background: var(--healthy-color);
            color: var(--bg-darker);
            box-shadow: 0 0 20px var(--healthy-color);
        }
        
        .download-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, var(--healthy-color), transparent);
            transition: left 0.5s;
        }
        
        .download-btn:hover::before {
            left: 100%;
        }
        
        .coming-soon {
            text-align: center;
            color: var(--warning-color);
            font-style: italic;
            margin-top: 1rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .feature {
            background: var(--bg-dark);
            border: 1px solid var(--decay-color);
            border-radius: 5px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .feature:hover {
            border-color: var(--healthy-color);
            transform: translateY(-5px);
        }
        
        .feature h3 {
            color: var(--warning-color);
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        .feature p {
            color: #cccccc;
            line-height: 1.6;
        }
        
        .requirements {
            background: var(--bg-dark);
            border: 1px solid var(--decay-color);
            border-radius: 5px;
            padding: 1.5rem;
        }
        
        .requirements h3 {
            color: var(--warning-color);
            margin-bottom: 1rem;
        }
        
        .requirements ul {
            list-style: none;
            color: #cccccc;
        }
        
        .requirements li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #333;
        }
        
        .requirements li:before {
            content: "▶ ";
            color: var(--healthy-color);
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            border-top: 1px solid var(--decay-color);
            margin-top: 3rem;
            color: #666;
        }
        
        .github-link {
            color: var(--healthy-color);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .github-link:hover {
            color: var(--warning-color);
            text-shadow: 0 0 5px var(--warning-color);
        }
        
        @media (max-width: 768px) {
            .title {
                font-size: 2.5rem;
            }
            
            .download-buttons {
                flex-direction: column;
                align-items: center;
            }
            
            .container {
                padding: 1rem;
            }
        }
        
        .alert {
            background: rgba(220, 228, 170, 0.1);
            border: 1px solid var(--warning-color);
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
            color: var(--warning-color);
        }
    </style>
</head>
<body>
    <div class="noise"></div>
    
    <div class="container">
        <header class="header">
            <h1 class="title">DIGITAL DECAY</h1>
            <p class="subtitle">A Game of Entropy and Digital Deterioration</p>
            
            <div class="decay-bar">
                <div class="decay-fill"></div>
                <div class="decay-text">System Integrity</div>
            </div>
        </header>
        
        <section class="description">
            <p>Enter a world where digital systems slowly decay and only your quick thinking can restore order. 
            Battle entropy through three unique mini-games as you watch the system's health deteriorate. 
            Can you maintain digital integrity, or will everything collapse into chaos?</p>
        </section>
        
        <section class="download-section">
            <h2 style="text-align: center; margin-bottom: 2rem; color: var(--warning-color);">Download Game</h2>
            
            <div class="alert">
                <strong>📢 Development Status:</strong> The game is currently in development. 
                Executable builds will be available soon through GitHub Releases.
            </div>
            
            <div class="download-buttons">
                <div class="download-btn" onclick="showDownloadInfo('windows')">
                    ⊞ Windows (Coming Soon)
                </div>
                <div class="download-btn" onclick="showDownloadInfo('mac')">
                    ⌘ macOS (Coming Soon)
                </div>
                <div class="download-btn" onclick="showDownloadInfo('linux')">
                    ⬢ Linux (Coming Soon)
                </div>
            </div>
            
            <div id="download-info" style="display: none; background: var(--bg-darker); padding: 1rem; border-radius: 5px; margin-top: 1rem;">
                <h4 style="color: var(--healthy-color); margin-bottom: 0.5rem;">Download Information:</h4>
                <p id="download-text" style="color: #cccccc;"></p>
            </div>
            
            <div class="coming-soon">
                Executables will be posted here when available. 
                <br>
                <a href="https://github.com/yourusername/digital-decay" class="github-link">
                    Check GitHub for updates →
                </a>
            </div>
        </section>
        
        <section class="features">
            <div class="feature">
                <h3>Grid Rejuvenation</h3>
                <p>Click on decaying grid blocks to restore them to their healthy state. Watch as the colors shift from decay back to vitality.</p>
            </div>
            
            <div class="feature">
                <h3>Bounce</h3>
                <p>Use your paddle to bounce falling blocks and prevent system collapse. Quick reflexes are essential for survival.</p>
            </div>
            
            <div class="feature">
                <h3>Keyboard Simon Says</h3>
                <p>Follow the sequence prompts carefully. Only press keys when "Computer says" - disobedience accelerates decay.</p>
            </div>
        </section>
        
        <section class="requirements">
            <h3>System Requirements</h3>
            <ul>
                <li>Windows 7/10/11, macOS 10.12+, or Linux (Ubuntu 16.04+)</li>
                <li>OpenGL 2.1+ support (most modern computers)</li>
                <li>512MB RAM minimum</li>
                <li>100MB disk space</li>
                <li>Keyboard and mouse</li>
            </ul>
        </section>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 Digital Decay. Experience entropy in digital form.</p>
        <p>View source on <a href="https://github.com/yourusername/digital-decay" class="github-link">GitHub</a></p>
    </footer>
    
    <script>
        function showDownloadInfo(platform) {
            const infoDiv = document.getElementById('download-info');
            const textDiv = document.getElementById('download-text');
            
            const messages = {
                windows: "Windows executable will be available in GitHub Releases. Download the .zip file, extract, and run DigitalDecay.exe. You may need to allow it through Windows Defender (normal for unsigned apps).",
                mac: "macOS executable will be available in GitHub Releases. Download, extract, and run. You may need to right-click and 'Open' the first time due to security settings.",
                linux: "Linux executable will be available in GitHub Releases. Download, extract, make executable with 'chmod +x DigitalDecay', then run."
            };
            
            textDiv.textContent = messages[platform];
            infoDiv.style.display = 'block';
        }
        
        // Add some dynamic effects
        document.addEventListener('DOMContentLoaded', function() {
            // Glitch effect on hover for title
            const title = document.querySelector('.title');
            title.addEventListener('mouseenter', function() {
                this.style.animation = 'glitch 0.3s infinite';
            });
            title.addEventListener('mouseleave', function() {
                this.style.animation = 'glitch 3s infinite';
            });
        });
    </script>
</body>
</html>"""
    
    # Write the HTML file
    with open(os.path.join(site_dir, 'index.html'), 'w') as f:
        f.write(html_content)
    
    # Don't create _config.yml - let GitHub Pages use defaults
    # Just create a simple .nojekyll file to avoid Jekyll processing
    with open(os.path.join(site_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    # Create a simple README for the docs directory
    readme_content = """# Digital Decay - Game Website

This directory contains the GitHub Pages website for Digital Decay.

The site is a simple HTML page that provides information about the game and download links.

## Setup

1. Push this repository to GitHub
2. Go to repository Settings → Pages
3. Set source to "Deploy from a branch"
4. Select "main" branch and "/docs" folder
5. Your site will be available at: https://yourusername.github.io/repository-name

## Updating

When you have executables ready:
1. Create a GitHub release with your built executables
2. Update the download links in index.html to point to the release downloads
3. Remove the "Coming Soon" text and alert
"""
    
    with open(os.path.join(site_dir, 'README.md'), 'w') as f:
        f.write(readme_content)
    
    print(f"GitHub Pages site created in '{site_dir}' directory")
    print("\nNext steps:")
    print("1. Commit and push this to your GitHub repository:")
    print("   git add docs/")
    print("   git commit -m 'Add GitHub Pages site'")
    print("   git push origin main")
    print("\n2. Enable GitHub Pages in your repository:")
    print("   - Go to Settings → Pages")
    print("   - Source: Deploy from a branch")
    print("   - Branch: main")
    print("   - Folder: /docs")
    print("\n3. Your site will be available at:")
    print("   https://yourusername.github.io/yourrepository")
    print("\n4. When you have executables built:")
    print("   - Create a GitHub release with the zip files")
    print("   - Update the download links in docs/index.html")
    
    return True

if __name__ == "__main__":
    create_github_pages_site()