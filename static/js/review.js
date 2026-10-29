document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('review-modal');
  const form = document.getElementById('review-form');
  const list = document.getElementById('review-list');
  const errorBox = document.getElementById('review-form-errors');
  const submitButton = document.getElementById('submit-review');
  const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;

  let editingCard = null;

  // Update the star selection.
  function updateStars() {
    const rating = Number(form.querySelector('input[name="rating"]:checked')?.value || 0);

    form.querySelectorAll('.rating-option').forEach(option => {
      const value = Number(option.querySelector('input').value);
      option.classList.toggle('selected', value <= rating);
      option.classList.remove('preview');
    });

    document.getElementById('rating-hint').textContent =
      rating ? `${rating} / 5 stars` : 'Choose 1 to 5 stars';
  }

  // Open the same form for creating or editing.
  function openForm(card = null) {
    editingCard = card;
    form.reset();
    form.action = card ? card.dataset.editUrl : form.dataset.createUrl;

    document.getElementById('review-modal-title').textContent =
      card ? 'Edit your review' : 'Write a review';
    submitButton.textContent = card ? 'Save Changes' : 'Submit Review';

    if (card) {
      const rating = form.querySelector(`input[name="rating"][value="${card.dataset.rating}"]`);
      if (rating) rating.checked = true;
      form.querySelector('[name="comment"]').value =
        card.querySelector('.review-comment').dataset.comment;
    }

    errorBox.hidden = true;
    updateStars();
    modal.showModal();
  }

  // Recalculate the review count and average.
  function updateSummary() {
    const cards = [...list.querySelectorAll('.review-card')];
    const total = cards.reduce((sum, card) => sum + Number(card.dataset.rating), 0);

    document.getElementById('review-count').textContent = cards.length;
    document.getElementById('average-rating').textContent =
      cards.length ? (total / cards.length).toFixed(1) : '0.0';
    document.getElementById('review-empty').hidden = cards.length > 0;
  }

  // Fill a review card with data returned by Django.
  function fillCard(card, review) {
    card.id = `review-${review.id}`;
    card.dataset.reviewId = review.id;
    card.dataset.rating = review.rating;
    card.dataset.editUrl = review.edit_url;
    card.dataset.deleteUrl = review.delete_url;

    card.querySelector('.review-author').textContent = review.username;
    card.querySelector('.review-date').textContent = review.created_at;

    const rating = card.querySelector('.review-rating');
    rating.textContent = `★ ${review.rating} / 5`;
    rating.setAttribute('aria-label', `${review.rating} out of 5 stars`);

    const comment = card.querySelector('.review-comment');
    comment.dataset.comment = review.comment;
    comment.textContent = review.comment || 'No written review.';
  }

  // Send a POST request to Django.
  async function post(url, body) {
    const response = await fetch(url, {
      method: 'POST',
      body,
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
      }
    });

    const data = await response.json();
    if (!response.ok || !data.ok) throw data;
    return data.review;
  }

  // Modal buttons and star selection.
  document.getElementById('open-review-modal').onclick = () => openForm();
  document.getElementById('close-review-modal').onclick = () => modal.close();
  document.getElementById('cancel-review-modal').onclick = () => modal.close();
  form.addEventListener('change', updateStars);
  updateStars();

  // CREATE or EDIT
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    submitButton.disabled = true;
    errorBox.hidden = true;

    try {
      const review = await post(form.action, new FormData(form));

      if (editingCard) {
        fillCard(editingCard, review);
      } else {
        const card = document.createElement('article');
        card.className = 'review-card';
        card.innerHTML = `
          <div class="review-card-top">
            <div>
              <strong class="review-author"></strong>
              <span class="review-date"></span>
            </div>
            <span class="review-rating"></span>
          </div>
          <p class="review-comment"></p>
          <div class="review-actions">
            <button type="button" class="review-link js-edit-review">Edit</button>
            <button type="button" class="review-link review-link-danger js-delete-review">Delete</button>
          </div>
        `;
        fillCard(card, review);
        list.prepend(card);
      }

      updateSummary();
      modal.close();
    } catch (error) {
      const messages = Object.values(error?.errors || {}).flat();
      errorBox.textContent =
        messages.map(item => item.message || String(item)).join(' ') ||
        'Something went wrong. Please try again.';
      errorBox.hidden = false;
    } finally {
      submitButton.disabled = false;
    }
  });

  // EDIT or DELETE buttons on review cards.
  list.addEventListener('click', async event => {
    const card = event.target.closest('.review-card');
    if (!card) return;

    if (event.target.closest('.js-edit-review')) {
      openForm(card);
      return;
    }

    const button = event.target.closest('.js-delete-review');
    if (!button || !confirm('Delete this review?')) return;

    button.disabled = true;
    try {
      await post(card.dataset.deleteUrl);
      card.remove();
      updateSummary();
    } catch (error) {
      button.disabled = false;
      alert('Could not delete review.');
    }
  });
});
