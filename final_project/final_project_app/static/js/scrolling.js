document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.outfit-card');
    let currentCardIndex = 0;
    let startX, startY, moveX, moveY;
    let currentCard = cards[currentCardIndex];

    const likeBtn = document.querySelector('.like-button');
    const dislikeBtn = document.querySelector('.dislike-button');
    const saveBtn = document.querySelector('.save-button');

    if (cards.length === 0) {
        showEndMessage();
        return;
    }

    function showNextCard() {
        currentCardIndex++;
        if (currentCardIndex < cards.length) {
            currentCard = cards[currentCardIndex];
            currentCard.style.display = 'flex';
        } else {
            showEndMessage();
        }
    }

    function showEndMessage() {
        document.getElementById('cardsContainer').innerHTML = `
            <div class="no-looks-message" style="text-align: center; margin-top: 20px;">
                <button id="loadMoreButton" style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                    Показать ещё
                </button>
            </div>
        `;

        const button = document.getElementById("loadMoreButton");
        if (button) {
            button.addEventListener("click", function () {
                location.reload();
            });
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function sendRatingToServer(lookId, action) {
        const formData = new FormData();
        formData.append('look_id', lookId);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        fetch(`/${action}_look/`, {
            method: 'POST',
            body: formData
        })
        .catch(error => console.error('Ошибка при отправке:', error));
    }

    function swipeCard(direction, card) {
        const likeIndicator = card.querySelector('.like-indicator');
        const dislikeIndicator = card.querySelector('.dislike-indicator');
        const lookId = card.getAttribute('data-look-id');

        if (direction === 'right') {
            card.classList.add('swipe-right');
            likeIndicator.style.opacity = '1';
            sendRatingToServer(lookId, 'like');
        } else {
            card.classList.add('swipe-left');
            dislikeIndicator.style.opacity = '1';
            sendRatingToServer(lookId, 'dislike');
        }

        setTimeout(() => {
            card.style.display = 'none';
            showNextCard();
        }, 500);
    }

    function saveCurrentLook() {
        if (!currentCard) return;

        const lookId = currentCard.getAttribute('data-look-id');
        const formData = new FormData();
        formData.append('look_id', lookId);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        fetch('/save_look/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                const saveIndicator = currentCard.querySelector('.save-indicator');
                if (saveIndicator) {
                    saveIndicator.style.opacity = '1';
                    setTimeout(() => {
                        saveIndicator.style.opacity = '0';
                    }, 1000);
                }
            }
        })
        .catch(error => console.error('Ошибка при сохранении:', error));
    }

    if (likeBtn) likeBtn.addEventListener('click', () => swipeCard('right', currentCard));
    if (dislikeBtn) dislikeBtn.addEventListener('click', () => swipeCard('left', currentCard));
    if (saveBtn) saveBtn.addEventListener('click', saveCurrentLook);

    cards.forEach(card => {
        card.addEventListener('touchstart', e => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        card.addEventListener('touchmove', e => {
            if (!startX || !startY) return;

            moveX = e.touches[0].clientX;
            moveY = e.touches[0].clientY;

            const diffX = moveX - startX;
            const diffY = moveY - startY;

            if (Math.abs(diffY) > Math.abs(diffX)) return;

            card.style.transform = `translateX(${diffX}px) rotate(${diffX * 0.1}deg)`;

            const likeIndicator = card.querySelector('.like-indicator');
            const dislikeIndicator = card.querySelector('.dislike-indicator');

            if (diffX > 50) {
                likeIndicator.style.opacity = Math.min(1, diffX / 100).toString();
                dislikeIndicator.style.opacity = '0';
            } else if (diffX < -50) {
                dislikeIndicator.style.opacity = Math.min(1, -diffX / 100).toString();
                likeIndicator.style.opacity = '0';
            } else {
                likeIndicator.style.opacity = '0';
                dislikeIndicator.style.opacity = '0';
            }
        });

        card.addEventListener('touchend', () => {
            if (!startX || !moveX) return;
            const diffX = moveX - startX;

            if (diffX > 100) swipeCard('right', card);
            else if (diffX < -100) swipeCard('left', card);
            else card.style.transform = '';

            startX = null;
            moveX = null;
        });
    });

    cards.forEach(card => {
        card.addEventListener('mousedown', e => {
            startX = e.clientX;
            startY = e.clientY;
            card.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', e => {
            if (!startX || !currentCard) return;

            moveX = e.clientX;
            moveY = e.clientY;
            const diffX = moveX - startX;
            const diffY = moveY - startY;

            if (Math.abs(diffY) > Math.abs(diffX)) return;

            currentCard.style.transform = `translateX(${diffX}px) rotate(${diffX * 0.1}deg)`;

            const likeIndicator = currentCard.querySelector('.like-indicator');
            const dislikeIndicator = currentCard.querySelector('.dislike-indicator');

            if (diffX > 50) {
                likeIndicator.style.opacity = Math.min(1, diffX / 100).toString();
                dislikeIndicator.style.opacity = '0';
            } else if (diffX < -50) {
                dislikeIndicator.style.opacity = Math.min(1, -diffX / 100).toString();
                likeIndicator.style.opacity = '0';
            } else {
                likeIndicator.style.opacity = '0';
                dislikeIndicator.style.opacity = '0';
            }
        });

        document.addEventListener('mouseup', () => {
            if (!startX || !currentCard) return;

            const diffX = moveX - startX;

            if (diffX > 100) swipeCard('right', currentCard);
            else if (diffX < -100) swipeCard('left', currentCard);
            else currentCard.style.transform = '';

            currentCard.style.cursor = 'grab';
            startX = null;
            moveX = null;
        });
    });

    // Показываем только первую карточку
    cards.forEach((card, index) => {
        if (index !== 0) card.style.display = 'none';
    });
});
