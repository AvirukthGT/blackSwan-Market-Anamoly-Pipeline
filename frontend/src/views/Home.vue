<template>
  <div class="home-container">
    
    <!-- HERO SECTION -->
    <div class="hero-section">
      <h1 class="animate-enter">BLACK SWAN INTELLIGENCE</h1>
      <p class="subtitle">Advanced Analytics for the Modern Trader. Don't just guess. <strong>Know.</strong></p>
      
      <div class="cta-buttons">
        <router-link to="/dashboard" class="btn-primary">OPEN TERMINAL</router-link>
        <router-link to="/news" class="btn-secondary">READ THE WIRE</router-link>
      </div>
    </div>

    <!-- FEATURES ROW -->
    <h2 class="section-header">SYSTEM CAPABILITIES</h2>
    <div class="features-grid">
      
      <router-link to="/dashboard" class="feature-card cartoon-pop">
        <div class="icon-box">
          <!-- Retro TV / Radar SVG -->
          <svg viewBox="0 0 100 100" class="cartoon-svg">
             <path d="M10,20 L90,20 L90,80 L10,80 Z" fill="none" stroke="currentColor" stroke-width="4" />
             <path d="M20,30 L80,30 L80,70 L20,70 Z" fill="none" stroke="currentColor" stroke-width="3" />
             <circle cx="70" cy="50" r="10" stroke="currentColor" stroke-width="3" fill="none" />
             <line x1="30" y1="10" x2="50" y2="20" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
             <line x1="70" y1="10" x2="50" y2="20" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>MARKET RADAR</h3>
        <p>Real-time sector performance. Spot the flow before it hits the tape.</p>
      </router-link>

      <router-link to="/signals" class="feature-card cartoon-pop">
        <div class="icon-box">
          <!-- Cartoon Lightning SVG -->
          <svg viewBox="0 0 100 100" class="cartoon-svg">
             <path d="M55,5 L25,50 L50,50 L40,95 L80,40 L50,40 Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" />
          </svg>
        </div>
        <h3>ALGO SIGNALS</h3>
        <p>Automated Golden Cross and RSI Mean Reversion systems.</p>
      </router-link>

      <router-link to="/news" class="feature-card cartoon-pop">
        <div class="icon-box">
          <!-- Newspaper SVG -->
          <svg viewBox="0 0 100 100" class="cartoon-svg">
             <rect x="25" y="10" width="50" height="40" fill="none" stroke="currentColor" stroke-width="4"/>
             <line x1="35" y1="20" x2="65" y2="20" stroke="currentColor" stroke-width="4"/>
             <line x1="35" y1="30" x2="65" y2="30" stroke="currentColor" stroke-width="4"/>
             <line x1="35" y1="40" x2="50" y2="40" stroke="currentColor" stroke-width="4"/>
             
             <!-- Folded Part -->
             <path d="M25,50 L75,50 L85,40 L85,80 L35,80 Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
             <line x1="45" y1="60" x2="75" y2="60" stroke="currentColor" stroke-width="3"/>
             <line x1="45" y1="70" x2="75" y2="70" stroke="currentColor" stroke-width="3"/>
          </svg>
        </div>
        <h3>NEWS IMPACT</h3>
        <p>AI-driven sentiment analysis. Quantify the chaos.</p>
      </router-link>

    </div>

    <!-- RECOMMENDATIONS / INSIGHTS -->
    <h2 class="section-header">SYSTEM RECOMMENDATIONS</h2>
    <div class="rec-grid">
      
      <div class="rec-card is-bullish cartoon-border">
        <div class="rec-badge">STRONG BUY</div>
        <div class="rec-ticker">NVDA</div>
        <div class="rec-desc">Target: $1,450</div>
      </div>

      <div class="rec-card is-bearish cartoon-border">
        <div class="rec-badge">AVOID</div>
        <div class="rec-ticker">INTC</div>
        <div class="rec-desc">Risk: High</div>
      </div>

      <div class="rec-card is-neutral cartoon-border">
        <div class="rec-badge">WATCHLIST</div>
        <div class="rec-ticker">BTC</div>
        <div class="rec-desc">Zone: Accumulate</div>
      </div>

    </div>

  </div>
</template>

<script setup>
</script>

<style scoped>
.home-container {
  padding: 4rem 2rem;
  color: var(--text-white);
  max-width: 1200px;
  margin: 0 auto;
}

/* HERO */
.hero-section {
  text-align: center;
  margin-bottom: 5rem;
  animation: bounceIn 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

h1 {
  font-family: 'Rubik Mono One', sans-serif;
  font-size: 3.5rem;
  /* Cartoon 3D Text */
  color: #fff;
  text-shadow: 4px 4px 0 #000, 8px 8px 0 var(--accent-primary);
  margin-bottom: 1.5rem;
  letter-spacing: -2px;
  -webkit-text-stroke: 2px #000;
}

.subtitle {
  font-family: 'Space Mono', monospace;
  font-size: 1.2rem;
  color: #ccc;
  max-width: 600px;
  margin: 0 auto 3rem auto;
  font-weight: bold;
  background: #000;
  display: inline-block;
  padding: 0.5rem 1rem;
  border: 2px solid #fff;
  border-radius: 8px;
  box-shadow: 4px 4px 0 #fff;
}

.cta-buttons {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
  font-family: 'Rubik Mono One';
  font-size: 1rem;
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.2s;
  border: 3px solid #000;
  box-shadow: 6px 6px 0 #000;
  text-transform: uppercase;
}

.btn-primary {
  background: var(--accent-primary);
  color: #000;
}
.btn-primary:hover {
  transform: translate(-3px, -3px);
  box-shadow: 9px 9px 0 #000;
}

.btn-secondary {
  background: #fff;
  color: #000;
}
.btn-secondary:hover {
  background: #eee;
  transform: translate(-3px, -3px);
  box-shadow: 9px 9px 0 #000;
}

/* SECTIONS */
.section-header {
  font-family: 'Rubik Mono One';
  font-size: 2rem;
  color: #fff;
  margin-bottom: 2rem;
  text-transform: uppercase;
  text-align: center;
  text-shadow: 3px 3px 0 #000;
  -webkit-text-stroke: 1px #000;
}

/* CARTOON GRID */
.features-grid, .rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 3rem;
  margin-bottom: 6rem;
}

/* CARTOON FEATURE CARDS */
.feature-card {
  background: #fff;
  border: 4px solid #000;
  padding: 2rem;
  border-radius: 20px;
  text-decoration: none;
  color: #000;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 8px 8px 0 #333;
}
.feature-card:hover {
  transform: scale(1.05) rotate(-2deg);
  box-shadow: 12px 12px 0 var(--accent-primary);
}

.icon-box {
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
  color: #000;
}
.cartoon-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(3px 3px 0 rgba(0,0,0,0.2));
}

.feature-card h3 { 
  font-family: 'Rubik Mono One'; 
  font-size: 1.2rem; 
  margin-bottom: 1rem; 
  color: #000;
}
.feature-card p { 
  font-family: 'Space Mono'; 
  font-weight: bold; 
  font-size: 0.9rem; 
  line-height: 1.4; 
  color: #333;
}

/* CARTOON REC CARDS */
.rec-card {
  background: #222;
  padding: 2rem;
  border: 4px solid #fff;
  border-radius: 16px;
  text-align: center;
  position: relative;
  box-shadow: 6px 6px 0 #000;
  transition: transform 0.2s;
}
.rec-card:hover { transform: translateY(-5px); }

.rec-badge {
  font-family: 'Rubik Mono One';
  font-size: 0.9rem;
  color: #000;
  background: #fff;
  padding: 8px 12px;
  border: 2px solid #000;
  border-radius: 8px;
  display: inline-block;
  margin-bottom: 1rem;
  transform: rotate(-3deg);
  box-shadow: 3px 3px 0 rgba(0,0,0,0.5);
}
.is-bullish .rec-badge { background: #00ff9d; }
.is-bearish .rec-badge { background: #fe2c55; }
.is-neutral .rec-badge { background: #ffb800; }

.rec-ticker { 
  font-size: 2.5rem; 
  font-weight: bold; 
  margin-bottom: 0.5rem; 
  font-family: 'Rubik Mono One'; 
  line-height: 1;
  -webkit-text-stroke: 1px #000;
}
.rec-desc { 
  font-family: 'Space Mono'; 
  color: #fff; 
  font-size: 1.1rem; 
  font-weight: bold; 
}

/* ANIMATIONS */
@keyframes bounceIn {
  0% { opacity: 0; transform: scale(0.3); }
  50% { opacity: 1; transform: scale(1.05); }
  70% { transform: scale(0.9); }
  100% { transform: scale(1); }
}

@media (max-width: 768px) {
  h1 { font-size: 2.5rem; }
  .home-container { padding: 2rem 1rem; }
}
</style>
