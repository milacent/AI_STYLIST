// static/js/app.js
document.addEventListener('DOMContentLoaded', () => {
    const cardContainer = document.getElementById('card-container');
    let posts = [];

    // Fetch posts from the API
    fetch('http://localhost:8000/api/posts/')
        .then(response => response.json())
        .then(data => {
            posts = data;
            renderCards(posts);
        })
        .catch(error => console.error('Error fetching posts:', error));

    function renderCards(posts) {
        cardContainer.innerHTML = ''; // Clear existing cards
        posts.forEach((post, index) => {
            const card = createCard(post, index);
            cardContainer.appendChild(card);
        });
    }

    function createCard(post, index) {
        const card = document.createElement('div');
        card.classList.add('card');
        card.style.zIndex = posts.length - index; // Stack cards
        card.dataset.id = post.id; // Store post ID for liking

        const img = document.createElement('img');
        img.src = post.image || 'https://via.placeholder.com/300'; // Fallback image
        img.alt = post.title;

        const info = document.createElement('div');
        info.classList.add('info');

        const title = document.createElement('h3');
        title.textContent = post.title;

        const description = document.createElement('p');
        description.textContent = post.description;

        info.appendChild(title);
        info.appendChild(description);
        card.appendChild(img);
        card.appendChild(info);

        // Swipe handling
        let startX = 0;
        let currentX = 0;
        let isDragging = false;

        // Mouse events
        card.addEventListener('mousedown', startDragging);
        card.addEventListener('mousemove', onDrag);
        card.addEventListener('mouseup', endDragging);
        card.addEventListener('mouseleave', endDragging);

        // Touch events for mobile
        card.addEventListener('touchstart', startDragging);
        card.addEventListener('touchmove', onDrag);
        card.addEventListener('touchend', endDragging);

        function startDragging(e) {
            isDragging = true;
            startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        }

        function onDrag(e) {
            if (!isDragging) return;
            currentX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
            const deltaX = currentX - startX;
            card.style.transform = `translateX(${deltaX}px) rotate(${deltaX / 10}deg)`;
        }

        function endDragging() {
            if (!isDragging) return;
            isDragging = false;
            const deltaX = currentX - startX;
            const threshold = 100; // Minimum swipe distance

            if (Math.abs(deltaX) > threshold) {
                const direction = deltaX > 0 ? 'right' : 'left';
                swipeCard(card, direction, post.id);
            } else {
                resetCardPosition(card);
            }
        }

        return card;
    }

    function swipeCard(card, direction, postId) {
        const containerWidth = cardContainer.offsetWidth;
        const offset = direction === 'right' ? containerWidth : -containerWidth;
        card.style.transition = 'transform 0.3s ease-in-out';
        card.style.transform = `translateX(${offset}px) rotate(${offset / 10}deg)`;

        // Handle like/dislike
        if (direction === 'right') {
            // Send like to server
            fetch(`/like_post/${postId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            }).then(response => console.log('Like sent:', response));
        }

        setTimeout(() => {
            card.remove();
            // Optionally, reload cards if needed
        }, 300);
    }

    function resetCardPosition(card) {
        card.style.transition = 'transform 0.3s ease-in-out';
        card.style.transform = 'translateX(0) rotate(0deg)';
    }
    // Helper to get CSRF token
    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) return value;
        }
        return '';
    }
});