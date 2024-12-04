document.addEventListener('DOMContentLoaded', function() {
    // Lighting mode selection
    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            modeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            fetch('/set_lighting_mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    mode: this.dataset.mode
                })
            });
        });
    });

    // Brightness control
    const brightnessSlider = document.querySelector('.brightness-slider');
    brightnessSlider.addEventListener('change', function() {
        fetch('/set_brightness', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                brightness: this.value
            })
        });
    });

    // Feed button
    const feedBtn = document.querySelector('.feed-btn');
    if (feedBtn) {
        feedBtn.addEventListener('click', function() {
            fetch('/feed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: 1
                })
            }).then(response => response.json())
              .then(data => {
                  if (data.success) {
                      // Could show a success message
                  }
              });
        });
    }

    // Feeding button handler
    document.querySelector('.feed-btn').addEventListener('click', async function() {
        try {
            const response = await fetch('/record-feeding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            if (data.status === 'success') {
                // Add visual feedback
                this.classList.add('active');
                setTimeout(() => {
                    this.classList.remove('active');
                }, 200);
            }
        } catch (error) {
            console.error('Error recording feeding:', error);
        }
    });

    // Feeding switch handler (momentary switch)
    const feedSwitch = document.getElementById('feed-switch');

    // Handle mouse events for momentary switch
    feedSwitch.addEventListener('mousedown', async function() {
        this.checked = true;
        try {
            const response = await fetch('/record-feeding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error recording feeding:', error);
        }
    });

    feedSwitch.addEventListener('mouseup', function() {
        this.checked = false;
    });

    feedSwitch.addEventListener('mouseleave', function() {
        this.checked = false;
    });

    // Handle touch events for mobile devices
    feedSwitch.addEventListener('touchstart', async function(e) {
        e.preventDefault(); // Prevent default touch behavior
        this.checked = true;
        try {
            const response = await fetch('/record-feeding', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error recording feeding:', error);
        }
    });

    feedSwitch.addEventListener('touchend', function(e) {
        e.preventDefault();
        this.checked = false;
    });

    feedSwitch.addEventListener('touchcancel', function(e) {
        e.preventDefault();
        this.checked = false;
    });

    // Water flow level selection
    const levelBtns = document.querySelectorAll('.level-btn');
    levelBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            levelBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            fetch('/set_flow_level', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    level: this.textContent.replace('档', '')
                })
            });
        });
    });

    // Toggle switches
    const switches = document.querySelectorAll('.switch input');
    switches.forEach(switchInput => {
        switchInput.addEventListener('change', function() {
            const type = this.closest('[class$="-section"]')?.classList[0]?.replace('-section', '') || '';
            
            fetch(`/toggle_${type}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    enabled: this.checked
                })
            });
        });
    });

    // Update temperature and status periodically
    function updateStatus() {
        fetch('/get_tank_data')
            .then(response => response.json())
            .then(data => {
                document.querySelector('.temp-value').textContent = `${data.temperature}°C`;
                document.querySelector('.temp-range').textContent = 
                    `最高 ${data.max_temp}°C 最低 ${data.min_temp}°C`;
            });
    }

    // Update status every 30 seconds
    setInterval(updateStatus, 30000);
    updateStatus(); // Initial update
});
