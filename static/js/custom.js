function toggleLike() {
    alert("hi this like");
  // Get the like count and like icon elements
  const likeCountElement = document.getElementById('like-count');
  const likeIconElement = document.getElementById('like-icon');

  // Get the current like count
  let likeCount = parseInt(likeCountElement.textContent);

  // Check if the like icon is filled or unfilled
  if (likeIconElement.classList.contains('far')) {
    // If unfilled, increment the like count and set the filled heart icon
    likeCount++;
    likeIconElement.classList.remove('far');
    likeIconElement.classList.add('fas');
  } else {
    // If filled, decrement the like count and set the unfilled heart icon
    likeCount--;
    likeIconElement.classList.remove('fas');
    likeIconElement.classList.add('far');
  }

  // Update the like count in the DOM
  likeCountElement.textContent = likeCount;

  // Send an AJAX request to update the like count in the database
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/update_like_count/', true);  // Update the URL to your Django view
  xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      // Success: Do something if needed
    }
  };
//   const data = {
//     event_id: {{ event.id }},  // Update with the appropriate event ID
//     like_count: likeCount
//   };
  xhr.send(JSON.stringify(data));
 }


 // online event