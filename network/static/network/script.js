function editPost(postId) {
    // Hide the original post content and show the textarea
    document.querySelector(`#content-${postId}`).classList.add("d-none");
    document.querySelector(`#edit-textarea-${postId}`).classList.remove("d-none");

    // Show the save button and hide the edit button
    document.querySelector(`#save-btn-${postId}`).classList.remove("d-none");
}

function savePost(postId) {
    const contentField = document.querySelector(`#edit-textarea-${postId}`);
    const content = contentField.value.trim();

    fetch(`/edit/${postId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(`Error: ${data.error}`);
        } else {
            // Update the post content dynamically
            const postContent = document.querySelector(`#content-${postId}`);
            postContent.innerText = data.content;

            // Show updated content and hide textarea
            postContent.classList.remove("d-none");
            contentField.classList.add("d-none");

            // Hide Save button
            document.querySelector(`#save-btn-${postId}`).classList.add("d-none");
        }
    })
    .catch(error => console.error("Error:", error));
}


// Function to get CSRF token (needed for Django POST/PUT requests)
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}


// Likes
function toggleLike(postId) {
    const likeIcon = document.getElementById(`like-icon-${postId}`);
    const likeCount = document.getElementById(`like-count-${postId}`);
    const csrfToken = getCSRFToken();

    fetch(`/like/${postId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            likeIcon.classList.remove("bi-heart");
            likeIcon.classList.add("bi-heart-fill");
        } else {
            likeIcon.classList.remove("bi-heart-fill");
            likeIcon.classList.add("bi-heart");
        }
        likeCount.innerText = data.like_count;  // Update like count
    })
    .catch(error => console.error("Error:", error));
}
