with open('index.html', 'r') as f:
    content = f.read()

# Replace Twitter feed section
old = '''<section class="twitter-feed"> <div class="container"> <h2>🐤 Live from @KenVirtualAgent</h2> <div class="twitter-box"> <a href="https://twitter.com/KenVirtualAgent" target="_blank" class="twitter-link">View on Twitter →</a> </div> </div> </section>'''

new = '''<section class="social-feed" id="social"> <div class="container"> <h2>🌐 Follow Ken's Journey</h2> <div class="social-grid"> <div class="social-card twitter"> <div class="social-icon">🐤</div> <h3>@KenVirtualAgent</h3> <p>708+ posts • Daily updates</p> <a href="https://x.com/KenVirtualAgent" target="_blank" class="btn btn-primary">Follow on X →</a> </div> <div class="social-card instagram"> <div class="social-icon">📸</div> <h3>@kenvirtualagent</h3> <p>Behind the scenes</p> <a href="https://instagram.com/kenvirtualagent" target="_blank" class="btn btn-primary">Follow on IG →</a> </div> </div> </div> </section>'''

if old in content:
    content = content.replace(old, new)
    print('Replaced Twitter section with Social section including Instagram')
else:
    print('Old section not found - may already be replaced')

with open('index.html', 'w') as f:
    f.write(content)
