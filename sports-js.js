// Sports Picks Enhancement Functions

function toggleReason(element) {
  const content = element.nextElementSibling;
  content.classList.toggle("open");
  element.querySelector('.reason-text').textContent = content.classList.contains('open') ? 'Why Ken picked this ▲' : 'Why Ken picked this ▼';
}

function sharePick(team) {
  const text = `Ken AI is 12-5 NBA this season. Tonight: ${team}. You tailing? 🏀\n\nJoin the mission: https://kenagent.xyz\n#KenAgent`;
  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
}

function shareParlay() {
  const text = `Ken's parlay (+450): ✓ Celtics -4.5, ✓ Warriors/Rockets Over 228.5, ✓ Man City Win\nYou riding? 🎯\n\nhttps://kenagent.xyz`;
  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  // Filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      document.querySelectorAll('.sport-card').forEach(card => {
        if (!card.classList.contains('resolved')) {
          card.style.display = (filter === 'all' || card.dataset.sport === filter) ? 'block' : 'none';
        }
      });
    });
  });

  // Countdown timer
  setInterval(() => {
    document.querySelectorAll('.countdown-time').forEach(time => {
      let text = time.textContent;
      if (text.includes('h')) {
        let [h, m] = text.split('h ').map(x => parseInt(x));
        if (m > 0) {
          m--;
        } else if (h > 0) {
          h--;
          m = 59;
        }
        time.textContent = `${h}h ${m}m`;
      }
    });
  }, 60000);
});
