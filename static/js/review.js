document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('review-modal');
  const form = document.getElementById('review-form');
  const list = document.getElementById('review-list');
  const emptyState = document.getElementById('review-empty');
  const submitButton = document.getElementById('submit-review');
  const modalTitle = document.getElementById('review-modal-title');
  const errorBox = document.getElementById('review-form-errors');
  const ratingHint = document.getElementById('rating-hint');
  const ratingOptions = document.getElementById('rating-options');
  const ratingInputs = Array.from(form.querySelectorAll('input[name="rating"]'));
  const commentField = form.querySelector('[name="comment"]');
  const createUrl = form.dataset.createUrl;
  const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
  let editingCard = form.dataset.initialEditId
    ? document.getElementById(`review-${form.dataset.initialEditId}`)
    : null;

  function notify(title, message, type = 'normal') {
    if (typeof showToast === 'function') {
      showToast(title, message, type);
    }
  }

  function chosenRating() {
    const checked = form.querySelector('input[name="rating"]:checked');
    return checked ? Number(checked.value) : 0;
  }

  function paintStars(rating, preview = false) {
    ratingInputs.forEach((input) => {
      const star = input.closest('.rating-option');
      const active = Number(input.value) <= rating;

      star.classList.toggle('selected', active && !preview);
      star.classList.toggle('preview', active && preview);
    });

    ratingHint.textContent = rating
      ? `${rating} / 5 stars`
      : 'Choose 1 to 5 stars';
  }

  function clearErrors() {
    errorBox.hidden = true;
    errorBox.textContent = '';
  }

  function openCreate() {
    editingCard = null;
    form.reset();
    form.action = createUrl;
    modalTitle.textContent = 'Write a review';
    submitButton.textContent = 'Submit Review';
    paintStars(0);
    clearErrors();
    modal.showModal();
  }

  function openEdit(card) {
    editingCard = card;
    form.reset();
    form.action = card.dataset.editUrl;
    modalTitle.textContent = 'Edit your review';
    submitButton.textContent = 'Save Changes';
    const rating = Number(card.dataset.rating);
    const selected = ratingInputs.find((input) => Number(input.value) === rating);
    if (selected) selected.checked = true;
    commentField.value = card.querySelector('.review-comment').dataset.comment;
    paintStars(rating);
    clearErrors();
    modal.showModal();
  }

  function updateSummary() {
    const cards = Array.from(list.querySelectorAll('.review-card'));
    const total = cards.reduce((sum, card) => sum + Number(card.dataset.rating), 0);
    document.getElementById('review-count').textContent = cards.length;
    document.getElementById('average-rating').textContent =
      cards.length ? (total / cards.length).toFixed(1) : '0.0';
    emptyState.hidden = cards.length > 0;
  }

  function applyReview(card, review) {
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

  function makeReviewCard(review) {
    const card = document.createElement('article');
    card.className = 'review-card';
    // Only fixed HTML here. User-provided values go through textContent in applyReview.
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
    applyReview(card, review);
    return card;
  }

  function showErrors(data) {
    const errors = Object.entries(data.errors || {}).flatMap(([field, messages]) =>
      messages.map((item) => `${field === '__all__' ? 'Review' : field}: ${item.message}`)
    );
    errorBox.textContent = errors.join(' ') || 'Please check your input.';
    errorBox.hidden = false;
  }

  paintStars(chosenRating());
  document.getElementById('open-review-modal').addEventListener('click', openCreate);
  document.getElementById('close-review-modal').addEventListener('click', () => modal.close());
  document.getElementById('cancel-review-modal').addEventListener('click', () => modal.close());

  ratingOptions.addEventListener('mouseover', (event) => {
    const label = event.target.closest('.rating-option');
    if (label) paintStars(Number(label.querySelector('input').value), true);
  });
  ratingOptions.addEventListener('mouseleave', () => paintStars(chosenRating()));
  ratingInputs.forEach((input) => {
    input.addEventListener('change', () => paintStars(chosenRating()));
    input.addEventListener('focus', () => paintStars(Number(input.value), true));
    input.addEventListener('blur', () => paintStars(chosenRating()));
  });

  // Clicking the dark backdrop closes the dialog.
  modal.addEventListener('click', (event) => {
    const r = modal.getBoundingClientRect();
    if (event.clientX < r.left || event.clientX > r.right ||
        event.clientY < r.top || event.clientY > r.bottom) modal.close();
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearErrors();
    if (!form.reportValidity()) return;
    submitButton.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json',
        },
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        showErrors(data);
        return;
      }

      if (editingCard) {
        applyReview(editingCard, data.review);
        notify('Review updated', 'Your changes were saved.', 'success');
      } else {
        list.prepend(makeReviewCard(data.review));
        notify('Review posted', 'Thanks for sharing your experience!', 'success');
      }
      updateSummary();
      modal.close();
    } catch (error) {
      errorBox.textContent = 'Something went wrong. Please try again.';
      errorBox.hidden = false;
    } finally {
      submitButton.disabled = false;
    }
  });

  list.addEventListener('click', async (event) => {
    const editButton = event.target.closest('.js-edit-review');
    const deleteButton = event.target.closest('.js-delete-review');
    const card = event.target.closest('.review-card');
    if (!card) return;

    if (editButton) {
      openEdit(card);
      return;
    }
    if (!deleteButton || !window.confirm('Delete this review?')) return;

    deleteButton.disabled = true;
    try {
      const response = await fetch(card.dataset.deleteUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
        },
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error('Delete failed');
      card.remove();
      updateSummary();
      notify('Review deleted', 'Your review was removed.', 'success');
    } catch (error) {
      deleteButton.disabled = false;
      notify('Could not delete', 'Please try again.', 'error');
    }
  });
});
