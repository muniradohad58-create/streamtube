document.addEventListener('DOMContentLoaded', () => {
  // Dark/Light Theme Toggle
  const themeToggle = document.getElementById('theme-toggle');
  const currentTheme = localStorage.getItem('theme') || 'light';
  
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    if(themeToggle) themeToggle.checked = true;
  }

  if (themeToggle) {
    themeToggle.addEventListener('change', (e) => {
      if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
      }
    });
  }

  // Search Autocomplete
  const searchInput = document.getElementById('search-input');
  const suggestionsBox = document.getElementById('suggestions-box');

  if (searchInput && suggestionsBox) {
    searchInput.addEventListener('input', async (e) => {
      const q = e.target.value.trim();
      if (!q) {
        suggestionsBox.style.display = 'none';
        return;
      }

      try {
        const response = await fetch(`/api/search-suggestions?q=${encodeURIComponent(q)}`);
        const suggestions = await response.json();

        if (suggestions.length > 0) {
          suggestionsBox.innerHTML = suggestions.map(s => `<div class="suggestion-item">${s}</div>`).join('');
          suggestionsBox.style.display = 'block';

          document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
              searchInput.value = item.textContent;
              suggestionsBox.style.display = 'none';
              searchInput.form.submit();
            });
          });
        } else {
          suggestionsBox.style.display = 'none';
        }
      } catch (err) {
        console.error(err);
      }
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.style.display = 'none';
      }
    });
  }
});